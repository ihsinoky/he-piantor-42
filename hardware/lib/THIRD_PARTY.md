# Third-party redistribution inventory

This is the canonical inventory for third-party design assets committed to the
repository. Project licensing in `LICENSE.md` does not replace any upstream
license or notice.

## Audited assets

| Source project | Source URL | Exact committed path(s) | Upstream license | Redistribution | Notice status |
| --- | --- | --- | --- | --- | --- |
| marbastlib | https://github.com/ebastler/marbastlib | `hardware/lib/third_party/marbastlib-he.pretty/SW_MX_HE_0deg_1u.kicad_mod` | CERN-OHL-P-2.0 | Allowed when applicable notices are retained | Complete: full upstream text is at `hardware/lib/third_party/marbastlib/LICENSE` |
| Keebio-Parts.pretty | https://github.com/keebio/Keebio-Parts.pretty | `hardware/lib/third_party/keebio.pretty/USON-8_UX_2x3x0p6_WIN.kicad_mod` | MIT | Allowed with copyright and permission notice | Complete: upstream text and Keebio copyright are at `hardware/lib/third_party/keebio/LICENSE` |
| RP2040-minimal-design | https://github.com/tommy-gilligan/RP2040-minimal-design | all files under `hardware/lib/reference/rp2040-minimal/` except the local explanatory `README.md` | BSD-3-Clause | Allowed with the BSD copyright, conditions, and disclaimer | Complete for this directory: `hardware/lib/reference/rp2040-minimal/LICENSE.txt` |
| RP2040-minimal-design (copied/modified working design) | https://github.com/tommy-gilligan/RP2040-minimal-design | `hardware/sensor-test/kicad/he-piantor-sensor-test.kicad_sch`, `MCU_RaspberryPi_RP2040.lib`, `RP2040_minimal-cache.lib`, `RP2040_minimal-rescue.kicad_sym`, `RP2040_minimal.pretty/**`, and portions incorporated into the other project schematics | BSD-3-Clause for upstream portions; CERN-OHL-P-2.0 for project-authored modifications | Allowed if the BSD notice remains with redistributed source/binaries | Present at `hardware/sensor-test/kicad/LICENSE-RP2040-MINIMAL.txt`; exact per-file derivation still requires confirmation as described below |

The marbastlib and Keebio footprint files are vendored verbatim. Any future
project-specific edit should use a separately named local footprint or carry the
upstream notice and a clear modification notice, as its license requires.
Package dimensions and the Keebio land pattern must still be checked against
the Winbond datasheet before manufacturing release.

## REVIEW REQUIRED before public release

These items do not have sufficiently precise provenance to approve public
redistribution yet. No license is guessed, and no upstream file has been
changed to simplify the review.

| Claimed/source context | Source URL | Exact committed path(s) | License under review | Redistribution result | Missing evidence/action |
| --- | --- | --- | --- | --- | --- |
| QMK `qmk_firmware`, Cantor `keyboard.json` coordinates | https://github.com/qmk/qmk_firmware/tree/master/keyboards/cantor | `hardware/layout/layout_source.json`; generated `hardware/layout/key_positions.csv` and `hardware/layout/layout_preview.svg` | QMK is generally GPL-2.0-or-later, but the applicable per-file notice and whether copyrightable expression was copied were not verified | **Not established** | Compare against the exact upstream revision, record it, determine whether attribution/source-offer requirements apply, and add the required notice/license |
| KiCad libraries and RP2040-minimal-design | https://gitlab.com/kicad/libraries and https://github.com/tommy-gilligan/RP2040-minimal-design | `hardware/sensor-test/kicad/RP2040_minimal-cache.lib`, `RP2040_minimal-rescue.kicad_sym`, `RP2040_minimal.pretty/**`, and `MCU_RaspberryPi_RP2040.lib` | Likely a mixture of BSD-3-Clause source material and KiCad library terms; exact origin is unrecorded | **Not established per file** | Diff each file/symbol/footprint against the pinned RP2040-minimal and KiCad revisions, then record the applicable notices and modification status |
| RP2040-minimal-design | https://github.com/tommy-gilligan/RP2040-minimal-design | RP2040-derived portions of `hardware/sensor-test/kicad/*.kicad_sch` | BSD-3-Clause upstream portions plus CERN-OHL-P-2.0 project modifications | **Conditionally allowed, boundary unverified** | Establish the exact upstream revision and record which sheets/embedded symbols were copied or modified; retain both notices |

Because redistribution rights for the first two rows are not yet established,
this inventory triggers the public-release STOP condition. Resolve the evidence
and update this table before changing repository visibility.

## Package dependencies

`hardware/tscircuit/package-lock.json` records npm dependency names, versions,
integrity hashes, and public registry URLs; it does not vendor package source.
Installed packages remain subject to their individual upstream licenses. A
release process should generate and review a dependency-license report whenever
the lockfile changes, but this is not a claim that lockfile entries are
project-owned content.
