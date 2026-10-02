# Third-party redistribution inventory

This is the canonical inventory for third-party design assets committed to the
repository. Project licensing in `LICENSE.md` does not replace any upstream
license or notice.

## Audited assets

| Source project | Exact upstream revision / source | Committed path(s) | Relationship | License / required notice |
| --- | --- | --- | --- | --- |
| marbastlib | https://github.com/ebastler/marbastlib | `hardware/lib/third_party/marbastlib-he.pretty/SW_MX_HE_0deg_1u.kicad_mod` | Vendored verbatim | CERN-OHL-P-2.0; full upstream text retained at `hardware/lib/third_party/marbastlib/LICENSE` |
| Keebio-Parts.pretty | https://github.com/keebio/Keebio-Parts.pretty | `hardware/lib/third_party/keebio.pretty/USON-8_UX_2x3x0p6_WIN.kicad_mod` | Vendored verbatim | MIT; copyright and permission notice retained at `hardware/lib/third_party/keebio/LICENSE` |
| QMK `qmk_firmware` | revision `d9f6dd215f2c4d295c6ad85b1f602125c2d81db1`; `keyboards/cantor/keyboard.json` (blob `9065e11ae5906756501448a7efe5706f93e53f87`); equivalent `keyboards/beekeeb/piantor/keyboard.json` (blob `94463f6c6d84091e89e907942b4218c514257b81`); layout `LAYOUT_split_3x6_3` | `hardware/layout/layout_source.json`, generated `key_positions.csv`, and generated `layout_preview.svg` | The 42 baseline `(x, y)` tuple sequence corresponds to both named upstream layouts. Identifiers and subsequent 17.0 mm pitch, rotation, pivot, and gap transforms are project-specific, but do not relicense the baseline | GPL-2.0-only, conservatively applied to the coordinate source and generated outputs; text retained at `LICENSES/GPL-2.0-only.txt` |
| RP2040-minimal-design reference | https://github.com/tommy-gilligan/RP2040-minimal-design at `7a3e5234447a9e01624c6a8de12d510f9e0161a7` | Upstream files under `hardware/lib/reference/rp2040-minimal/` | Vendored reference | BSD-3-Clause; upstream notice retained at `hardware/lib/reference/rp2040-minimal/LICENSE.txt` |
| RP2040-minimal-design libraries and footprints | same repository and revision | Files enumerated in the blob-verification table below | Verbatim Git-blob matches | BSD-3-Clause; redistribution allowed with notice retained at `hardware/sensor-test/kicad/LICENSE-RP2040-MINIMAL.txt` |
| RP2040-minimal-derived working schematics | same repository and revision | `hardware/sensor-test/kicad/he-piantor-sensor-test.kicad_sch` and RP2040-derived portions incorporated into other working schematics | Derived/modified | Retain BSD-3-Clause notice for the reference-derived material; project modifications are additionally CERN-OHL-P-2.0 |

The marbastlib and Keebio footprint files remain unmodified. Any future
project-specific edit should use a separately named local footprint or carry
all notices required by its license. Package dimensions and the Keebio land
pattern still require checking against the Winbond datasheet before
manufacturing release.

## Verified RP2040-minimal Git-blob matches

PMO supplied authoritative external verification against
`tommy-gilligan/RP2040-minimal-design` revision
`7a3e5234447a9e01624c6a8de12d510f9e0161a7`. Local `git hash-object` produces
the same Git blob IDs:

| Upstream-relative and local filename | Git blob SHA | State |
| --- | --- | --- |
| `MCU_RaspberryPi_RP2040.lib` | `160483336b3889515a359615228dac1efe412b0e` | Verbatim |
| `RP2040_minimal-cache.lib` | `d4affb88f17632e3b310687a455f9524245ae3e2` | Verbatim |
| `RP2040_minimal-rescue.kicad_sym` | `7e858c4d003f8478eb7fc438ede32c36d665500d` | Verbatim |
| `RP2040_minimal.pretty/Crystal_SMD_HC49-US.kicad_mod` | `b367844910882cae9e299ebaef18f2de46c253f7` | Verbatim |
| `RP2040_minimal.pretty/RP2040-QFN-56.kicad_mod` | `e6eeeb3ffab4457c200a3efec1cd19f72867e652` | Verbatim |
| `RP2040_minimal.pretty/USB_Micro-B_Amphenol_10103594-0001LF_Horizontal_modified.kicad_mod` | `8b1f07c3552f8c49056a995a46f8392072ff3828` | Verbatim (the upstream filename includes `modified`) |

These exact matches resolve the former speculative KiCad-standard-library
provenance row. The working schematics are documented conservatively as
BSD-derived and modified; an exact line or embedded-symbol boundary is not
needed to retain the permissive BSD notice across the derived design. No
existing upstream notice was deleted or replaced.

## Layout license boundary and JITX impact

The QMK evidence resolves the repository, revision, source paths, layout, and
license provenance. The baseline tuples remain QMK-derived and are not asserted
to be solely project-owned or CERN-OHL-P-2.0 material. The project-specific
identifiers and transformations do not alter that conservative exception.

This GPL exception does not affect the current M1 JITX evaluation: the four-key
M1 electrical/evaluation design does not depend on the 42-key Cantor/Piantor
coordinate asset. No conclusion is made here about the source or license of the
future final 42-key JITX Rev.A geometry; that decision remains a future Human
Gate.

## Remaining review scope

There are no remaining **REVIEW REQUIRED** rows in this inventory for the two
provenance topics audited here. Public release still requires the separately
owned hosted-metadata review and Product Owner approval; this inventory does
not authorize a visibility change.

## Package dependencies

`hardware/tscircuit/package-lock.json` records npm dependency names, versions,
integrity hashes, and public registry URLs; it does not vendor package source.
Installed packages remain subject to their individual upstream licenses. A
release process should generate and review a dependency-license report whenever
the lockfile changes, but this is not a claim that lockfile entries are
project-owned content.
