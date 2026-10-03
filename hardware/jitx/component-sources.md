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
| `U_MCU` | Raspberry Pi RP2040 | C2040 | https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf | revision not determined from extracted source | QFN-56 7 x 7 mm, datasheet §5.1 and Figure 167 (pp. 607-608) | `parity/m1-parity-contract.json`, `../sensor-test/pinmap.csv` | **BLOCKED:** LCSC lookup confirms all 57 physical positions, but the available extracted manufacturer pages do not provide auditable text/table association for every recommended-land-pattern dimension. No geometry is guessed. |
| `J_USB` | HRO TYPE-C-31-M-12 | C165948 | No HRO-authorized package/land-pattern document or redistributable HRO/user KiCad footprint obtained. | unavailable | Non-standard USB-C receptacle | `parity/m1-parity-contract.json`, `../sensor-test/design.md` | **BLOCKED:** LCSC lookup confirms contacts and four shell stakes, but is not an authorized footprint source. EasyEDA/LCSC footprint ingestion, third-party footprints, and manual transcription are prohibited. |
| `U_ESD` | STMicroelectronics USBLC6-2SC6 | C7519 | https://www.st.com/resource/en/datasheet/usblc6-2sc6.pdf | unavailable: official endpoint timed out in this environment | SOT-23-6L | `parity/m1-parity-contract.json` | **BLOCKED:** manufacturer PDF could not be acquired and LCSC pinout provides pad numbers only; do not infer the mapping or dimensions. |
| `U_FLASH` | Winbond W25Q16JVUXIQ | C2843335 | https://www.winbond.com/hq/support/documentation/?__locale=en&keyword=W25Q16JV | unavailable: direct revision URLs returned 404/timeouts | USON-8-EP 2 x 3 mm | `parity/m1-parity-contract.json`, `../sensor-test/design.md` | **BLOCKED:** exact manufacturer USON signal-pad and exposed-pad drawing unavailable. The frozen project geometry is corroborating evidence only and is not substituted for manufacturer package data. |
| `Y1` | Abracon ABM8-272-T3 | C20625731 | https://abracon.com/Resonators/abm8.pdf | revised 2020-07-29 | SMD 3.2 x 2.5 mm, datasheet outline drawing, p. 2 | `parity/m1-parity-contract.json`, `../sensor-test/bom.csv` | **BLOCKED:** manufacturer PDF is cached, but no documented JITX generator or authorized KiCad conversion source was found for the non-standard four-pad crystal footprint. No custom pad locations are transcribed. |
| `U_LDO` | Diodes Incorporated AP2112K-3.3TRG1 | C51118 | https://www.diodes.com/assets/Datasheets/AP2112.pdf | DS39724 Rev. 2-2, June 2017 | SOT25, datasheet pp. 2 and 14 | `parity/m1-parity-contract.json`, `../sensor-test/bom.csv` | **PASS:** JITX `SOT23_5` generator parameterized from the SOT25 drawing; explicit pin-to-pad mapping and real non-dry build pass. |
| `U_LOAD` | Texas Instruments TPS22919DCKR | C2149796 | https://www.ti.com/lit/ds/symlink/tps22919.pdf | SLVSEN5B, revised May 2019 | DCK SC-70-6; datasheet p. 3 pin table, manufacturer package drawing not acquired | `parity/m1-parity-contract.json`, `../sensor-test/bom.csv` | **BLOCKED:** pin functions are verified, but package dimensions/land pattern are supplied through a separate manufacturer package document that could not be acquired; installed JITX has no SC-70-specific generator. |
| `U_MUX` | Texas Instruments TMUX1208PWR | C494728 | https://www.ti.com/lit/ds/symlink/tmux1208.pdf | SCDS389C, revised December 2018 | PW TSSOP-16; datasheet p. 3 pin table, manufacturer package drawing not acquired | `parity/m1-parity-contract.json`, `../sensor-test/bom.csv` | **BLOCKED:** pin table is verified, but PW geometry/land pattern are in a separate package drawing that could not be acquired; installed JITX has no TSSOP-specific generator. |
| `U_H0..U_H3` | Texas Instruments DRV5055A3QDBZR | C266128 | https://www.ti.com/lit/ds/symlink/drv5055.pdf | SBAS640C, revised June 2026 | DBZ SOT-23; datasheet p. 3 pin table, manufacturer package drawing not acquired | `parity/m1-parity-contract.json`, `../sensor-test/bom.csv` | **BLOCKED:** manufacturer confirms the pinout, but not the exact package dimensions in the acquired datasheet text; do not use an uncited generic SOT geometry. |

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
