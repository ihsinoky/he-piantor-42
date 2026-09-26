# Third-party hardware sources

## marbastlib HE footprint

Source: https://github.com/ebastler/marbastlib

Vendored file:
- `hardware/lib/third_party/marbastlib-he.pretty/SW_MX_HE_0deg_1u.kicad_mod`

Upstream description: footprint for Cherry-MX-style Hall-effect switches including Gateron Magnetic Jade, with an SOT-23-3 Hall sensor placed under the switch.

License: CERN Open Hardware Licence Version 2 - Permissive (CERN-OHL-P-2.0).

The upstream file is currently included verbatim. Project-specific changes, if needed, will be made in a separately named local footprint so the upstream notice remains clear.


## Keebio W25Q16 USON footprint

Source: https://github.com/keebio/Keebio-Parts.pretty

Vendored file:
- `hardware/lib/third_party/keebio.pretty/USON-8_UX_2x3x0p6_WIN.kicad_mod`

Upstream tags this footprint specifically for `W25Q16JVUXIQ`.

License: MIT.

The upstream footprint is vendored verbatim together with:
- `hardware/lib/third_party/keebio/LICENSE`

Package dimensions and land pattern will be cross-checked against the Winbond datasheet before PCB manufacturing release.
