# License map

This is a mixed-license repository. A more-specific entry below overrides a
broader path entry. Third-party material is never relicensed by this map.

## Project-authored material

| Path | License | License text |
| --- | --- | --- |
| `hardware/**` | CERN Open Hardware Licence Version 2 — Permissive (`CERN-OHL-P-2.0`) | [`LICENSES/CERN-OHL-P-2.0.txt`](LICENSES/CERN-OHL-P-2.0.txt) |
| `mechanical/**` | `CERN-OHL-P-2.0` | [`LICENSES/CERN-OHL-P-2.0.txt`](LICENSES/CERN-OHL-P-2.0.txt) |
| `manufacturing/**` | `CERN-OHL-P-2.0` | [`LICENSES/CERN-OHL-P-2.0.txt`](LICENSES/CERN-OHL-P-2.0.txt) |
| `firmware/**` | MIT | [`LICENSES/MIT.txt`](LICENSES/MIT.txt) |
| `task/**` | MIT | [`LICENSES/MIT.txt`](LICENSES/MIT.txt) |
| `docs/**`, `.github/**`, root documentation, and project-authored scripts outside the hardware/mechanical/manufacturing trees | MIT | [`LICENSES/MIT.txt`](LICENSES/MIT.txt) |

The hardware license covers project-authored hardware source, design documents,
and generated design/manufacturing artifacts. The MIT license covers
project-authored software, firmware, scripts, dashboard code, and documentation,
except where a file is part of a hardware design source or a more-specific
notice says otherwise.

## Exceptions and third-party material

The following paths retain their upstream licenses and notices:

| Path | Upstream license/status |
| --- | --- |
| `hardware/lib/third_party/marbastlib-he.pretty/**` and `hardware/lib/third_party/marbastlib/LICENSE` | `CERN-OHL-P-2.0`; upstream copyright and notices retained |
| `hardware/lib/third_party/keebio.pretty/**` and `hardware/lib/third_party/keebio/LICENSE` | MIT; Keebio copyright and notice retained |
| `hardware/lib/reference/rp2040-minimal/**` | BSD-3-Clause; Raspberry Pi Ltd and Tommy Gilligan notice retained in `LICENSE.txt` |
| `hardware/sensor-test/kicad/MCU_RaspberryPi_RP2040.lib`, `RP2040_minimal-cache.lib`, `RP2040_minimal-rescue.kicad_sym`, and `RP2040_minimal.pretty/**` | Verbatim from RP2040-minimal-design revision `7a3e5234447a9e01624c6a8de12d510f9e0161a7`; BSD-3-Clause notice retained in `LICENSE-RP2040-MINIMAL.txt` |
| RP2040-minimal-derived working schematics under `hardware/sensor-test/kicad/**` | Upstream-derived portions remain BSD-3-Clause with `LICENSE-RP2040-MINIMAL.txt`; project modifications are additionally `CERN-OHL-P-2.0` |
| `hardware/layout/layout_source.json` and its generated `key_positions.csv` / `layout_preview.svg` | QMK-derived baseline coordinate sequence, GPL-2.0-only; exact revision and paths are recorded in `layout_source.json`, and the license text is [`LICENSES/GPL-2.0-only.txt`](LICENSES/GPL-2.0-only.txt). Project-specific identifiers and transforms do not relicense the baseline tuples |
| `hardware/tscircuit/package-lock.json` | Dependency metadata; installed packages retain their individual upstream licenses and are not relicensed |

See [`hardware/lib/THIRD_PARTY.md`](hardware/lib/THIRD_PARTY.md) for the
canonical redistribution inventory, exact revisions, Git-blob evidence, and
notice requirements. The QMK-derived layout assets and BSD-derived working
designs are explicit exceptions to the general project-authored hardware row.
