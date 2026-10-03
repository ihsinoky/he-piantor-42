# EDA-002C1 M1 Component Source Manifest

This manifest records source provenance for M1 manufacturer-specific JITX
component models. The frozen electrical authority remains
`../tscircuit/src/evaluation/m1-four-key.tsx`; it is evidence for M1 semantic
ports and approved identities, not component-model source code. No
`hardware/layout/**` file was used.

Raspberry Pi, HRO, and Winbond documents were downloaded only to the ignored
`.sources/` cache and checked for the `%PDF-` signature. ST DS4260 Rev 7 was
read through the official manufacturer-hosted PDF using the web PDF reader;
local curl downloads timed out (the document itself is available). LCSC `parts2jitx-lcsc --pinout` was
used solely to cross-check the project-approved C-number, inventory, and pin
names. It was not used to ingest any footprint data.

| M1 role | Manufacturer / exact MPN | JLCPCB | Manufacturer source | Revision/date | Package / package source | Project evidence | Method / status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `U_MCU` | Raspberry Pi RP2040 | C2040 | https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf | build 3184e62-clean, 2025-02-20 | QFN-56 7 x 7 mm; printed pp. 607-608 package/“Recommended PCB Footprint”, pp. 611-614 pinout/tables | `parity/m1-parity-contract.json`, `../sensor-test/pinmap.csv` | **PASS:** project-authored Landpattern reproduces unequal side land lengths and 3.20 mm reduced ePad; all 57 physical ports explicitly mapped and tested; real build PASS. |
| `J_USB` | HRO TYPE-C-31-M-12 | C165948 | https://en.krhro.com/Product-Details/726.html → PDF Download (exact target below) | exact M-12 sheet dated 2020-12-08, PDF page 4 | recommended PCB layout, component side; do not use M-12A/B/C sheets | `parity/m1-parity-contract.json` only as independent cross-check | **PASS (manufacturer model):** public Landpattern/SMDPad/THPad/NPTHPad, 12 contact lands + four plated shell stakes + two NPTH; SHIELD maps four stakes. Structural tests and real build PASS. Frozen geometry differs; see discrepancy table. |
| `U_ESD` | STMicroelectronics USBLC6-2SC6 | C7519 | https://www.st.com/resource/en/datasheet/usblc6-2.pdf | DS4260 Rev 7, December 2021 | SOT23-6L; p. 1 functional diagram, p. 12 mechanical data | `parity/m1-parity-contract.json` | **PASS:** SOT23_6 explicitly parameterized from exact-part mechanical data, density C; all six physical pins mapped and tested; real build PASS. The requested usblc6-2sc6.pdf resolves in the web reader to a Y-grade document and is not the final source. |
| `U_FLASH` | Winbond W25Q16JVUXIQ | C2843335 | https://www.winbond.com/hq/support/documentation/levelOne.jsp?__locale=en&DocNo=DA00-W25Q16JV.1 → official PDF below | W25Q16JV Rev J, May 28, 2026 | UX = USON 2 x 3 x 0.6 mm; printed p. 5 pin map, p. 67 package, pp. 72-73 ordering | `parity/m1-parity-contract.json` only as independent cross-check | **PASS (manufacturer model):** SON generator, explicit package/lead tolerances and density C; eight signals plus 0.20 x 1.60 mm exposed metal mapped to separate EP port. Structural tests and real build PASS. Frozen geometry differs; see discrepancy table. |
| `Y1` | Abracon ABM8-272-T3 | C20625731 | https://abracon.com/Resonators/abm8.pdf | revised 2020-07-29 | SMD 3.2 x 2.5 mm; p. 2 recommended land pattern | `parity/m1-parity-contract.json`, `../sensor-test/bom.csv` | **PASS:** project-authored public JITX `Landpattern` with four manufacturer-specified 1.30 x 1.05 mm pads at 2.30 x 1.75 mm pitch; bottom-view order explicitly mapped and non-dry build passes. |
| `U_LDO` | Diodes Incorporated AP2112K-3.3TRG1 | C51118 | https://www.diodes.com/assets/Datasheets/AP2112.pdf | DS39724 Rev. 2-2, June 2017 | SOT25, datasheet pp. 2 and 14 | `parity/m1-parity-contract.json`, `../sensor-test/bom.csv` | **PASS:** JITX `SOT23_5` generator parameterized from the SOT25 drawing; explicit pin-to-pad mapping and real non-dry build pass. |
| `U_LOAD` | Texas Instruments TPS22919DCKR | C2149796 | https://www.ti.com/lit/ds/symlink/tps22919.pdf | SLVSEN5B, revised May 2019 | DCK SC-70-6; pin table p. 3; DCK0006A, 4214835/D (Nov. 2024), https://www.ti.com/jp/lit/pdf/mpds114f | `parity/m1-parity-contract.json`, `../sensor-test/bom.csv` | **PASS:** JITX `SOT23_6` parameterized from DCK0006A body/span/lead dimensions and pin map; physical NC and QOD are retained; non-dry build passes. |
| `U_MUX` | Texas Instruments TMUX1208PWR | C494728 | https://www.ti.com/lit/ds/symlink/tmux1208.pdf | SCDS389C, revised December 2018 | PW TSSOP-16; pin table p. 3; PW0016A, 4220204/B (Dec. 2023), https://www.ti.com/lit/ml/mpds361a/mpds361a.pdf | `parity/m1-parity-contract.json`, `../sensor-test/bom.csv` | **PASS:** JITX `SOIC` dual-column generator parameterized from PW0016A; all 16 physical pins including NC map explicitly; non-dry build passes. |
| `U_H0..U_H3` | Texas Instruments DRV5055A3QDBZR | C266128 | https://www.ti.com/lit/ds/symlink/drv5055.pdf | SBAS640C | DBZ SOT-23; pin table p. 3; DBZ0003A, 4214838/F (Aug. 2024), https://www.ti.com/cn/lit/pdf/mpds108g | `parity/m1-parity-contract.json`, `../sensor-test/bom.csv` | **PASS:** JITX `SOT23_3` parameterized from DBZ0003A and explicit VCC/OUT/GND map; non-dry build passes. |

## JLC lookup evidence

| C-number | Result |
| --- | --- |
| C2040 | RP2040 / LQFN-56 7x7 / 57 physical positions; matches manufacturer/package identity. |
| C165948 | TYPE-C-31-M-12 / SMD / 16 contacts including four EH shell stakes; lookup only, no footprint download. |
| C7519 | USBLC6-2SC6 / SOT-23-6L / six positions; exact functional labels now reconciled against ST DS4260 p. 1. |
| C2843335 | W25Q16JVUXIQ / USON-8-EP 2x3 / eight signals plus EP. |
| C20625731 | ABM8-272-T3 / SMD3225-4P / four positions. |
| C51118 | AP2112K-3.3TRG1 / SOT-25-5 / VIN, GND, EN, NC, VOUT. |
| C2149796 | TPS22919DCKR / SC-70-6 / IN, GND, ON, NC, QOD, VOUT. |
| C494728 | TMUX1208PWR / TSSOP-16 / all sixteen datasheet labels. |
| C266128 | DRV5055A3QDBZR / SOT-23 / VCC, OUT, GND. |

The lookup output is retained in the execution record; no distributor PDF,
footprint, or EasyEDA data has been added to this repository.

## Re-investigation and resolved primary sources (2026-10-03)

HRO's official page was fetched and its actual `pdfPreview(...)` / `modelSrc`
link followed. The current family drawing target is:
https://omo-oss-file110.thefastfile.com/portal-saas/pg2026081913505947704/cms/file/type-c-31-m-12%2612a%2612b%2612c%281%29.pdf
The first unencoded request returned HTTP 403; an encoded filename with a
browser user-agent and manufacturer referer succeeded. The PDF contains four
variants; **page 4, PART NO. TYPE-C-31-M-12, 2020-12-08** is the exact source.
The earlier statement that manual manufacturer transcription was prohibited
was incorrect: project-owned public JITX landpatterns are permitted.

Winbond's official `downloadV2022.jsp` record for
`/support/resources/.content/item/DA00-W25Q16JV_1.html` redirected to
`levelOne.jsp?__locale=en&DocNo=DA00-W25Q16JV.1`. Its `productUrl` links:
https://www.winbond.com/resource-files/W25Q16JV%20SPI%20RevJ%2005202026%20Plus.pdf
This PDF supplies the exact UX outline, complete signal pin table and valid
ordering scheme. D=2.90/3.00/3.10, E=1.90/2.00/2.10, A=.50/.55/.60,
b=.20/.25/.30, L=.40/.45/.50 mm, e=.50 BSC; the narrow exposed metal is
D1=.15/.20/.25 by E1=1.55/1.60/1.65 mm. No manufacturer PCB land drawing is
present, so the authorized dimensions-plus-SON-generator method is used.
EP geometry uses the stated nominal metal size, not the frozen footprint.

ST's product-family document `usblc6-2.pdf` covers the exact USBLC6-2SC6.
The older requested `usblc6-2sc6.pdf` returned a USBLC6-2SC6Y document to the
web reader. Official ST family PDF pages 1 and 12 confirm the required pin
map and package dimensions; repeated local downloads through global,
regional and canonical CD00050750 URLs timed out, but official PDF text and
page views were accessible via the web reader. This is a transport limitation,
not missing manufacturer data and not a geometry blocker.

## Independent frozen-geometry cross-check — differences remain for PMO

All nine manufacturer models pass **component-modeling** checks. This does
not establish M1 geometric parity. Neither frozen tscircuit file nor the
parity contract was changed. Before EDA-002C2 can claim full parity, PMO must
resolve these concrete differences; no top-level circuit has been started.

| Feature (mm) | Manufacturer model | Frozen M1 evidence | Result |
| --- | --- | --- | --- |
| HRO wide contact center magnitudes | 3.20 and 2.40 | 3.25 and 2.45 | different |
| HRO contact height | 1.14 = 1.64 minus .50 from layout datums | 1.45 | different |
| HRO locating NPTH diameter / separation | .60 / 5.78 | .65 / 5.78 | diameter differs |
| HRO shell center span / row separation | 8.65 / 4.18 | 8.64 / 4.18 | span differs |
| HRO upper shell copper / slot | .90 x 2.00 / .60 x 1.70 | 1.00 x 2.10 / .60 x 1.70 | copper differs |
| HRO lower shell copper / slot | .90 x 1.70 / .60 x 1.40 | 1.00 x 1.60 / .60 x 1.20 | both differ |
| HRO contact-center to locator row | 1.07 | 1.445 | different |
| Winbond signal lands / column span | IPC C: .7118034 x .22 / 2.7881966 | .8128 x .254 / 2.8956 | different generator lands |
| Winbond exposed land | nominal metal .20 x 1.60 | .254 x 1.651 | different land choice |

Source/package geometry is established for all four reopened components.
No manufacturer-source blockers remain. EDA-002C1 is a **done / accepted
candidate**, pending PR #36 PMO review. EDA-002C2 is **next / unblocked** for
follow-up evaluation; the differences above remain explicit parity acceptance
issues, not permission to change the frozen reference or D-014.
