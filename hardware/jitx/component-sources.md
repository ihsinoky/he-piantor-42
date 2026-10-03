# EDA-002C1 M1 Component Source Manifest

This manifest records source provenance for M1 manufacturer-specific JITX
component models. The frozen electrical authority remains
`../tscircuit/src/evaluation/m1-four-key.tsx`; it is evidence for M1 semantic
ports and approved identities, not component-model source code. No
`hardware/layout/**` file was used.

Manufacturer documents were downloaded only to the ignored `.sources/` cache
and checked for the `%PDF-` signature. LCSC `parts2jitx-lcsc --pinout` was
used solely to cross-check the project-approved C-number, inventory, and pin
names. It was not used to ingest any footprint data.

| M1 role | Manufacturer / exact MPN | JLCPCB | Manufacturer source | Revision/date | Package / package source | Project evidence | Method / status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `U_MCU` | Raspberry Pi RP2040 | C2040 | https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf | revision not determined from extracted source | QFN-56 7 x 7 mm, §5.1, figures captioned “Top down view” and “Recommended PCB Footprint” (pp. 607-608) | `parity/m1-parity-contract.json`, `../sensor-test/pinmap.csv` | **IN PROGRESS:** official drawing supplies 0.4 mm pitch and reduced 3.20 mm ePad; all 57 physical-port names still require a completed manufacturer-figure reconciliation. |
| `J_USB` | HRO TYPE-C-31-M-12 | C165948 | No HRO-authorized package/land-pattern document or redistributable HRO/user KiCad footprint obtained. | unavailable | Non-standard USB-C receptacle | `parity/m1-parity-contract.json`, `../sensor-test/design.md` | **BLOCKED:** LCSC lookup confirms contacts and four shell stakes, but is not an authorized footprint source. EasyEDA/LCSC footprint ingestion, third-party footprints, and manual transcription are prohibited. |
| `U_ESD` | STMicroelectronics USBLC6-2SC6 | C7519 | https://www.st.com/resource/en/datasheet/usblc6-2sc6.pdf | unavailable: official endpoint timed out in this environment | SOT-23-6L | `parity/m1-parity-contract.json` | **BLOCKED:** manufacturer PDF could not be acquired and LCSC pinout provides pad numbers only; do not infer the mapping or dimensions. |
| `U_FLASH` | Winbond W25Q16JVUXIQ | C2843335 | https://www.winbond.com/hq/product/code-storage-flash/qspi-nor/w25q-jv/?__locale=en | unavailable: exact official UX package drawing not yet resolved | USON-8-EP 2 x 3 mm | `parity/m1-parity-contract.json`, `../sensor-test/design.md` | **BLOCKED:** exact manufacturer USON signal-pad and exposed-pad drawing remains unavailable. The frozen project geometry is corroborating evidence only and is not substituted for manufacturer package data. |
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
| C7519 | USBLC6-2SC6 / SOT-23-6L / six positions; manufacturer functional pin labels remain unavailable. |
| C2843335 | W25Q16JVUXIQ / USON-8-EP 2x3 / eight signals plus EP. |
| C20625731 | ABM8-272-T3 / SMD3225-4P / four positions. |
| C51118 | AP2112K-3.3TRG1 / SOT-25-5 / VIN, GND, EN, NC, VOUT. |
| C2149796 | TPS22919DCKR / SC-70-6 / IN, GND, ON, NC, QOD, VOUT. |
| C494728 | TMUX1208PWR / TSSOP-16 / all sixteen datasheet labels. |
| C266128 | DRV5055A3QDBZR / SOT-23 / VCC, OUT, GND. |

The lookup output is retained in the execution record; no distributor PDF,
footprint, or EasyEDA data has been added to this repository.
