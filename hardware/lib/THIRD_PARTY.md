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

### 2026-10-02 provenance audit evidence

The audit stopped rather than inferring an upstream revision. The checkout has
no Git remote, and neither the import commits nor the imported files record an
upstream commit or tag. Network retrieval of the named repositories was also
unavailable in the audit environment. Consequently, an exact-revision claim
cannot be reconstructed from the repository alone.

For the layout, commit `c3a82cf` introduced `layout_source.json` naming only
`qmk/qmk_firmware`, `keyboards/cantor/keyboard.json`, and
`LAYOUT_split_3x6_3`. It did not record a revision. The current 42 tuples are
therefore still treated as potentially derived values. The later 17.0 mm
pitch, ±30 degree rotations, 34 mm inner-home gap, and transformation pivots
are local design parameters, but that fact does not establish the provenance
of the untransformed tuples or justify removing the QMK/Cantor boundary.
Beekeeb Piantor is documented by this project as the design inspiration and as
derived from Cantor; no Piantor source file or revision is recorded locally.
Whether the tuples are uncopyrightable facts/dimensions or copied expression,
and whether a GPL notice is required, remains **REVIEW REQUIRED** pending an
exact upstream comparison and qualified legal determination.

For the KiCad material, commit `cabdde3` imported every file listed below. The
working files are not present in the earlier vendored reference directory, so
their exact origin cannot be proven merely by comparing against that directory.
The retained BSD-3-Clause notice is not evidence of a particular revision.

| Working asset | Import state / local evidence | Provenance status and required notice |
| --- | --- | --- |
| `MCU_RaspberryPi_RP2040.lib` | Imported at `cabdde3`; SHA-256 `c6bd79c6015663e96df13aece795a20080df9de97ea215c8cb5bb55158c8e1e6` | **REVIEW REQUIRED**: RP2040-minimal vs. KiCad library origin and exact revision unproved; retain BSD notice and add any applicable KiCad notice after comparison |
| `RP2040_minimal-cache.lib` | Imported at `cabdde3`; SHA-256 `d7cfc65a0a255abf195b503284b2a5ea26512aa47811422716fa33afc5d81557` | **REVIEW REQUIRED**: generated cache containing mixed symbols is plausible but unproved; retain BSD notice; determine source and license per embedded symbol |
| `RP2040_minimal-rescue.kicad_sym` | Imported at `cabdde3`; SHA-256 `87ae4673d8ffee9d962d641ca8bc0436447b5814405c82b138488709a2667a6e` | **REVIEW REQUIRED**: likely generated rescue library, but exact inputs/revision are unproved; retain BSD notice and any notice required by each rescued symbol's source |
| `RP2040_minimal.pretty/Crystal_SMD_HC49-US.kicad_mod` | Imported at `cabdde3`; SHA-256 `0c057948eb59f84d286160ac652b325d275b6e0537ce100170004833b8a084b9` | **REVIEW REQUIRED**: exact repository, revision, and verbatim/modified state unproved; retain BSD notice pending comparison |
| `RP2040_minimal.pretty/RP2040-QFN-56.kicad_mod` | Imported at `cabdde3`; SHA-256 `46b0b39ad74cd771bdcd023e90a96fc7215a682a093b336e35e51e36ba5a4c10` | **REVIEW REQUIRED**: exact repository, revision, and verbatim/modified state unproved; retain BSD notice pending comparison |
| `RP2040_minimal.pretty/USB_Micro-B_Amphenol_10103594-0001LF_Horizontal_modified.kicad_mod` | Imported at `cabdde3`; filename itself indicates modification; SHA-256 `9d52cc87db7e6946b302184f4a8eb64e68c38344973a75ea533e94fb9216e802` | **REVIEW REQUIRED**: base asset, modifier, revision, and applicable KiCad/BSD notices unproved; retain BSD notice pending comparison |
| `he-piantor-sensor-test.kicad_sch` and RP2040 portions later copied into `integrated-sensor-test.kicad_sch` | The first file was imported at `cabdde3`; embedded RP2040 symbols, USB/flash rescue symbols, core circuit, and placement notes visibly correspond to the vendored reference schematic, but no machine-readable copy boundary exists | **REVIEW REQUIRED**: exact upstream revision and verbatim/modified boundaries unproved; retain BSD notice for upstream portions and CERN-OHL-P-2.0 for project modifications |
| `hall-front-end.kicad_sch`, `usb-power.kicad_sch`, `integrated-sensor-test.kicad_sch`, project/table files | Project working files introduced or subsequently edited in local history; they reference some imported libraries and the integrated sheet incorporates the RP2040 core | Project-authored portions are CERN-OHL-P-2.0; referenced/incorporated third-party portions remain subject to the unresolved rows above |

No existing upstream notice was deleted or replaced during this audit.

## Package dependencies

`hardware/tscircuit/package-lock.json` records npm dependency names, versions,
integrity hashes, and public registry URLs; it does not vendor package source.
Installed packages remain subject to their individual upstream licenses. A
release process should generate and review a dependency-license report whenever
the lockfile changes, but this is not a claim that lockfile entries are
project-owned content.
