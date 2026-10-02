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
| RP2040-minimal-derived material under `hardware/sensor-test/kicad/**` | BSD-3-Clause portions retain the notice in `LICENSE-RP2040-MINIMAL.txt`; project modifications are `CERN-OHL-P-2.0` |
| `hardware/layout/layout_source.json` and its generated `key_positions.csv` / `layout_preview.svg` | **REVIEW REQUIRED** — coordinates identify QMK Cantor as their source, but the precise copied expression and required GPL notices have not been established |
| KiCad cache/rescue libraries and copied footprints under `hardware/sensor-test/kicad/**` | **REVIEW REQUIRED** — exact upstream file provenance and notice obligations have not been established |
| `hardware/tscircuit/package-lock.json` | Dependency metadata; installed packages retain their individual upstream licenses and are not relicensed |

See [`hardware/lib/THIRD_PARTY.md`](hardware/lib/THIRD_PARTY.md) for the
canonical redistribution inventory and unresolved provenance work. Files marked
**REVIEW REQUIRED** are not asserted to be covered solely by a project license
and block a public-release readiness finding until resolved.

The 2026-10-02 follow-up audit could not recover exact upstream revisions from
the local repository. It therefore retained both **REVIEW REQUIRED** exceptions
above and all existing notices; it did not reclassify the coordinate tuples as
project-owned or assume that a generated KiCad cache/rescue file is free of its
input assets' license conditions.
