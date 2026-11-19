# Issue #292 Stage 2a — Wireless Main module selection study

Status: STUDY (no layout). Worker: Muse, 2026-11-19.
Trigger: PO reopened the module basis (2026-11-19). D-055 chose the
Raytac MDBT50Q-1MV2 as a fallback under the old constraints; since
then the north tab is accepted, USB may live on a daughterboard,
and SWD via PO's nRF52840 DK (PCA10056) is the service path. The
candidate field is therefore wider than Stage 1 assumed. Chip is
fixed: nRF52840 (D-052). All stock figures observed 2026-11-19
(crawl dates noted where the listing extract is older).

## Signal list the module must serve (Stage 1 study §1.1, + SWD)

Wing links: MUX_A0/A1/A2 (out), MUX_OUT_A/B/C (ADC in), HALL_PWR_EN,
MUX_EN0, MUX_EN1 (out) = 9; trackpad I2C SDA/SCL + DR = 3; battery
sense AIN = 1; button + LED = 2; SWDIO/SWDCLK (+RESET) = debug pads.
**Total 15 GPIO of which 4 ADC-capable**, plus module power pins.
USB on the module is a PLUS (daughterboard link simplification),
not a gate — SWD is the service lifeline (PO input 2026-11-19).

## Survey (maker lineups; disposition one line each)

| maker / module | SoC | disposition |
|---|---|---|
| Insight SiP **ISP1807-LR** | nRF52840 | SHORTLIST — see gates |
| Raytac **MDBT50Q-1MV2** (+ -P1MV2 PCB-ant, -U1MV2 u.FL) | nRF52840 | SHORTLIST — see gates |
| Ezurio (Laird) **BL654** 451-00001 int. / 451-00002 MHF4 ext. | nRF52840 | SHORTLIST — see gates |
| Fanstel **BT840** (BT840F/E siblings) | nRF52840 | SHORTLIST — see gates |
| u-blox **NINA-B306-00B** | nRF52840 | gate fail (cert number) — below |
| Taiyo Yuden **ED2840AA2** (ex-EYSKDNZWB) | nRF52840 | gate fail (availability) — below |
| Seeed **XIAO nRF52840 Plus** | nRF52840 | gate fail (availability) — below |
| Seeed XIAO nRF52840 (standard) | nRF52840 | gate fail (cert unverified, Stage 1 §1.3) |
| Panasonic **PAN1780** (ENW89854A1KF) | nRF52840 | gate fail (cert) — below |
| Fanstel BM840 | nRF52840 QFAA | same channel profile as BT840, smaller (TELEC 201-220130); folded into the BT840 row as its small sibling — not separately scored |
| Minew MS88SF2-class | nRF52840 | surveyed out: no franchised JP-reachable channel with observable stock, cert evidence not in maker EN docs |
| Fujitsu Components FWM7BLZ-class | nRF52840 | surveyed out: direct-sales channel only, stock not observable |
| Holyiot 18010-class | nRF52840 | surveyed out: marketplace channels only, TELEC evidence not verifiable |

## Hard gates (fail = out; evidence recorded)

### Gate 1 — Japan certification (maker document / MIC, number recorded)

| candidate | verdict | evidence |
|---|---|---|
| ISP1807-LR | **PASS** | Insight SiP datasheet §8.1: "Japan: TELEC Certified, n° **020-200037**" |
| MDBT50Q-1MV2 | **PASS** | Raytac Approval Sheet Ver.L §9.3 TELEC certificate (BLE 1M/2M + 802.15.4); FCC ID SH6MDBT50Q; construction-type number is printed in the §9.3 certificate image — record the digits from the certificate at layout (only gate entry without digits in hand; the certificate itself is in the maker's own approval sheet) |
| BL654 | **PASS** | Ezurio Regulatory Information v2.3 §5: Japan (MIC) **201-180112** for both 451-00001 and 451-00002; MIC-listed external antennas named (FlexPIFA 001-0022, NanoBlue, FlexNotch, mFlexPIFA) |
| BT840 | **PASS** | Fanstel Product Specifications Ver.1.28: Japan TELEC **201-190710/00** (BT840/F/E) |
| NINA-B306 | **FAIL (number)** | u-blox Product Summary UBX-17052930 lists "Japan (MIC)" among type approvals, but no certificate number could be recorded from maker documents in this study; the gate requires the number |
| ED2840AA2 | PASS on cert (MIC 005-103104, Stage 2 gate record) — fails Gate 2 | |
| PAN1780 | **FAIL** | Panasonic's own pre-certification list for PAN1780 = FCC / ISED / CE only (maker comparison + Product Specification Rev.1.6 §6 shows no MIC entry) |
| XIAO Plus | PASS on cert (222-257139, Stage 1) — fails Gate 2 | |

### Gate 2 — Availability (observed 2026-11-19, 2+ channels, >> 5+spares)

| candidate | verdict | channels observed |
|---|---|---|
| ISP1807-LR-RS | **PASS (deep)** | DigiKey **13,850 in stock** @ $13.65 (1+, crawl 2026-11-18/19); Mouser ISP1807-LR-ST/-RS **In Stock** (359-ISP1807-LR-ST) |
| BL654 451-00001 | **PASS (deep)** | Mouser **15,850 in stock** @ $13.14 (814-451-00001, crawl ≤12 d); 451-00002: Mouser 1,209 + 5,000 incoming; DigiKey franchised listing |
| MDBT50Q-1MV2 | **PASS (thin)** | DigiKey Marketplace **35** @ $6.15 (+$25 flat shipping, ~14 d, crawl 2026-11-18); SparkFun WRL-21605 **In Stock** @ $8.95 (crawl 2026-11-18). TME reel listing re-checked 2026-11-19: **0 stock, MOQ 1,500, special order** — the Stage 1 TME figure (88–176) no longer stands. LCSC C5118826 own stock **0** |
| BT840 | **PASS (weak evidence)** | DigiKey (1914-1018) and Mouser (308-BT840) both list the module **In Stock** (JSON-LD offers, crawls 2026-11-06/17); numeric counts not exposed in the listing extracts. Fanstel direct: $6.88 @1 |
| ED2840AA2 | **FAIL** | Stage 2 gate G1 (2026-11-19): no stock figure retrievable at DigiKey / Mouser / LCSC / TME / Chip1Stop |
| XIAO Plus | **FAIL** | DigiKey US 0 / CA 5 (Stage 1, 2026-11-19); no second channel with observed stock |

### Gate 3 — Signal sufficiency (counted from the candidate's pin table)

Need: 15 GPIO / 4 AIN + SWD + RESET.

| candidate | verdict | count |
|---|---|---|
| ISP1807-LR | **PASS** | 46 GPIO incl. 8 ADC (maker datasheet); USB present; SWD pads present |
| MDBT50Q-1MV2 | **PASS** | 61-pad table read in full from Approval Sheet §2.5: 48 GPIO, AIN0–7 subset, SWDIO pin 51 / SWDCLK pin 53, RESET pin 40 (P0.18) |
| BL654 | **PASS** | full nRF52840 GPIO set exposed (datasheet: all chipset functionality); USB present on 451-00001 |
| BT840 | **PASS** | full QIAA GPIO set (48) per Fanstel spec |

### Gate 4 — Antenna (documented keep-out the Main+tab+case can honour, or external in the south PETG zone)

| candidate | verdict | arrangement |
|---|---|---|
| ISP1807-LR | **PASS** | built-in antenna; datasheet §4.3 keep-out = metal exclusion zone from the antenna edge to the board edge, all layers (except mechanical LGA pads). Honourable in the SW pocket with the antenna edge on the south outline |
| MDBT50Q-1MV2 | **PASS** | chip antenna; datasheet §2.3 no-ground area in the antenna position on EACH layer, module toward board edge. Needs the module at an outline edge (tab or pocket end). -U1MV2 variant: u.FL → certified-external placement in the south zone (DigiKey Marketplace 79 observed for -U1MV2) |
| BL654 | **PASS (best freedom)** | 451-00001 printed antenna at module edge; **451-00002 + MIC-listed FlexPIFA** puts the antenna element itself in the south PETG zone on an MHF4 lead — the only candidate whose certified antenna can live exactly in the D-053 zone |
| BT840 | **PASS** | PCB trace antenna at module edge, Fanstel layout guide keep-out; BT840E u.FL variant certified with ANT060 |

**Survivors: ISP1807-LR, MDBT50Q-1MV2, BL654, BT840.**
