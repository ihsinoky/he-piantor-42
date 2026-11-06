# Issue 149 evidence and reproduction

The accepted boards are `{16,17}mm/wing-{16,17}mm-silk149.kicad_pcb` and the two
`wing-*-silk149-review.zip` files at this directory's root. See
[the Japanese report](../../../../docs/issue-149-wing-silkscreen.md).

Each order-review ZIP contains exactly seven Gerber layers and two classified
Excellon drill files. `inputs/`, paste-reference, gbrjob, previews and reports
are evidence only. No manufacturer uploads, orders, payments or merges were made.

The inherited `add-silkscreen.py` is retained unchanged as interrupted-run evidence.
It stops before writing a PCB because an unbroken key-frame overlaps a test pad.
Use `build-silkscreen.py`, which cuts local gaps in pitch frames, places pin1 marks
clear of pads, and adds the other required legend. It appends board-level F.SilkS
primitives without reserializing or editing source content. UUIDs are newly generated;
repeat generation yields the same geometry but different added UUIDs.

## Inputs

- Tracked #141 acceptance boards/projects in `../issue-141-wing-power-integrity/runs/KRT-{16,17}-2L-P0300/`.
- Tracked #141 placement/routing inventories, inspection library tables, and Wing129.pretty.
- Tracked JITX `hardware/jitx/wing/generated/representative21-{16,17}mm/{definition.json,placements.csv}`.
- Frozen #147 preflight/CAM files in `inputs/issue147/`, with original path and SHA256
  in `inputs/provenance.json`. These copies avoid dependency on the uncommitted #147
  working tree or its Draft PR #148. Their source PCB SHA is checked against #141.
- `protected-resume-hashes.json.gz`: SHA256/link-text snapshot of 49,477 existing paths,
  excluding only `.issue149-runtime/`, made before generation. Includes the normal `.git`
  and the inherited partial evidence. `resume-start.json` marks completion of this snapshot.

## Tools and runtime

This run reused KiCad 9.0.9/native Python bindings in `.issue129-runtime/kicad/`,
Shapely/numpy in `.issue129-runtime/geometry/`, and Gerbonara 1.5.0, CairoSVG and Pillow
in `.issue147-runtime/viewer-venv/` read-only. New runtime state is confined to
`.issue149-runtime/`. These large tool installations are intentionally untracked.
The isolated Git directory is `.issue149-runtime/git`, branch
`issue-149-wing-silkscreen`; normal `.git` remains unchanged.

From repository root, native commands use the environment below (or the saved
`.issue149-runtime/env.sh` in this workspace):

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$PWD/.issue129-runtime/kicad/usr/lib/python3/dist-packages:$PWD/.issue129-runtime/geometry/lib/python3.12/site-packages"
export LD_LIBRARY_PATH="$PWD/.issue129-runtime/kicad/usr/lib/x86_64-linux-gnu:$PWD/.issue129-runtime/kicad/usr/lib/kicad"
export KICAD_STOCK_DATA_HOME="$PWD/.issue129-runtime/kicad/usr/share/kicad"
export TMPDIR="$PWD/.issue149-runtime/tmp"
export XDG_CONFIG_HOME="$PWD/.issue149-runtime/config"
export XDG_CACHE_HOME="$PWD/.issue149-runtime/cache"
export XDG_DATA_HOME="$PWD/.issue149-runtime/data"
export XDG_STATE_HOME="$PWD/.issue149-runtime/state"
unset DISPLAY WAYLAND_DISPLAY
```

The existing evidence is verified without regenerating the board or exports:

```bash
python3 hardware/kicad/qualification/issue-149-wing-silkscreen/verify-silkscreen.py --verify-only
PYTHONPATH= .issue147-runtime/viewer-venv/bin/python hardware/kicad/qualification/issue-149-wing-silkscreen/inspect-manufacturing.py --verify-only
python3 hardware/kicad/qualification/issue-149-wing-silkscreen/audit-deliverables.py --verify-only
```

For a separate, empty output directory in an isolated checkout, the generation
sequence is `build-silkscreen.py`, `qualify.py`, `inspect-manufacturing.py`,
`render-review.py`, then `verify-silkscreen.py`. Preserve the frozen `inputs/` first.
Generation deliberately refuses existing PCB/ZIP/export/process destinations.
Do not run generation over accepted evidence. `qualify.py` makes runtime copies
with unchanged project and source-library table, then invokes CLI DRC/export.
Every CAD process has argv, UTC start/end, exit code, stdout and stderr under `processes/`.
No design settings or DRC exclusions are relaxed. Native source recovery also protects
zones, masks and every source element not explicitly listed in the geometry summary.

Gerber rendering is offline, filter-free and uses a white background. Source SVGs,
all nine layer PNGs, front legend, copper/hole composites and contact sheets are in
`{16,17}mm/preview-review/`. `visual-review.json` records the actual image inspection;
`manufacturing-checks.json` records parsed manufacturing checks. G90 header warnings
are expected and all absolute drill coordinates are independently matched.

`manifest.json` hashes this report and all qualification files except itself and the
later `publication.json`. The full inherited-file snapshot is a local-workspace audit:
on another checkout, use `audit-deliverables.py --verify-only --skip-workspace-baseline`
to check committed deliverables without requiring old untracked runtime installations.
The manifest remains verified in that mode; the skipped baseline is explicitly reported.

## Publication and fallback

Only this directory and `docs/issue-149-wing-silkscreen.md` are staged. The original
untracked #147 work is preserved and not bundled into this PR except the explicitly
frozen comparison inputs. `pr-draft.md` is the review description. `publication.json`
records publication outcome after the manufacturing commit, in a follow-up commit.

If push is unavailable, recover the already committed branch from the isolated Git:

```bash
git fetch ./.issue149-runtime/git issue-149-wing-silkscreen
git push origin FETCH_HEAD:issue-149-wing-silkscreen
```

Then create a Draft PR with `pr-draft.md`; do not merge. Publication and remote CI
results must be distinguished from local qualification results.
