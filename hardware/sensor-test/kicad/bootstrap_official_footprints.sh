#!/usr/bin/env bash
# Export authoritative footprint bytes from the same image used by engineering CI.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
inventory="$repo_root/hardware/sensor-test/kicad/footprint-dependencies.json"
output="${1:-$repo_root/bootstrap-output/kicad-9-footprints}"
image="kicad/kicad:9.0.9"
container="issue-11-kicad-footprint-export-$RANDOM"
trap 'docker rm -f "$container" >/dev/null 2>&1 || true' EXIT

python3 "$repo_root/hardware/sensor-test/kicad/inventory_footprints.py" --check
rm -rf "$output"
mkdir -p "$output"
docker pull "$image"
docker create --name "$container" "$image" sleep infinity >/dev/null
docker start "$container" >/dev/null

mapfile -t references < <(python3 -c \
  'import json,sys; print("\n".join(json.load(open(sys.argv[1]))["kicad_standard_requiring_vendoring"]))' \
  "$inventory")
source_map="$(mktemp)"
trap 'rm -f "$source_map"; docker rm -f "$container" >/dev/null 2>&1 || true' EXIT
first_source=""

for reference in "${references[@]}"; do
  library="${reference%%:*}"
  footprint="${reference#*:}"
  mapfile -t candidates < <(docker exec "$container" sh -c \
    "find / -type f -path '*/${library}.pretty/${footprint}.kicad_mod' -print 2>/dev/null" || true)
  if [[ "${#candidates[@]}" -ne 1 ]]; then
    printf 'Expected exactly one official source for %s; found %d:\n%s\n' \
      "$reference" "${#candidates[@]}" "${candidates[*]-}" >&2
    exit 1
  fi
  mkdir -p "$output/${library}.pretty"
  docker cp "$container:${candidates[0]}" "$output/${library}.pretty/${footprint}.kicad_mod"
  [[ -n "$first_source" ]] || first_source="${candidates[0]}"
  printf '%s\t%s\t%s\n' "$reference" "${candidates[0]}" \
    "$library.pretty/$footprint.kicad_mod" >> "$source_map"
done

# Preserve the attribution shipped by the package that owns the exported files.
# Prefer package metadata; fall back to a license adjacent to the footprint root.
package="$(docker exec "$container" sh -c \
  "dpkg-query -S '$first_source' 2>/dev/null | head -n1 | cut -d: -f1" || true)"
license_source=""
if [[ -n "$package" ]]; then
  license_source="$(docker exec "$container" sh -c \
    "test -f '/usr/share/doc/$package/copyright' && printf '%s' '/usr/share/doc/$package/copyright'" || true)"
fi
if [[ -z "$license_source" ]]; then
  footprint_root="${first_source%/*.pretty/*}"
  mapfile -t license_candidates < <(docker exec "$container" sh -c \
    "find '$footprint_root' -maxdepth 2 -type f \\( -iname 'LICENSE*' -o -iname 'COPYING*' \\) -print" || true)
  if [[ "${#license_candidates[@]}" -ne 1 ]]; then
    printf 'Could not identify exactly one license/attribution file for %s\n' "$first_source" >&2
    exit 1
  fi
  license_source="${license_candidates[0]}"
fi
docker cp "$container:$license_source" "$output/LICENSE.kicad-footprints"

python3 - "$output" "$source_map" "$image" <<'PY'
import datetime, hashlib, json, pathlib, sys
output, source_map, image = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
entries = []
for line in source_map.read_text().splitlines():
    reference, source, relative = line.split("\t")
    data = (output / relative).read_bytes()
    entries.append({"reference": reference, "file": relative, "original_source_path": source,
                    "sha256": hashlib.sha256(data).hexdigest()})
license_file = output / "LICENSE.kicad-footprints"
manifest = {"source_image": image, "acquisition_date_utc": datetime.date.today().isoformat(),
            "acquisition_method": "docker cp of uniquely discovered image path",
            "license_file": license_file.name,
            "license_sha256": hashlib.sha256(license_file.read_bytes()).hexdigest(), "files": entries}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
rows = ["# KiCad 9 footprint provenance", "", f"Source image: `{image}`",
        f"Acquisition date (UTC): `{manifest['acquisition_date_utc']}`", "",
        "Files are unmodified bytes exported from the uniquely discovered paths in `manifest.json`.",
        "The manifest records every logical reference, original image path, and SHA-256 digest.",
        "The image-provided attribution is preserved as `LICENSE.kicad-footprints` and hashed in the manifest.", ""]
(output / "PROVENANCE.md").write_text("\n".join(rows))
PY

echo "Exported ${#references[@]} authoritative footprints to $output"
