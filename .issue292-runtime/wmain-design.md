# Issue #292 Stage 1 — Wireless Main board: design study

Status: STUDY (no board implementation). Worker: Muse, 2026-11-19.
Successor to Main Rev.10 (wired, D-046/D-047). Design inputs: D-048
(NiMH AA x4 pod, external charging), D-049 (TMAG5253BA3 Wings, 3.3 V
Hall rail, EN per MUX bank, divider removed, rail-drop budget
<=50 mV class), D-050/D-052 (single nRF52840 module), D-053
(TM040040 trackpad in the central bay, dia.40 Main keep-out, antenna
home = south PETG zone), PO 2026-11-19 (case south outline
straightened; the band south of Main deepens to 13.802 mm from the
Main wall line, case frame).

Frames: KiCad board coordinates from the Rev.10 board file
(`hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb`,
extracted for this study; see plan.md). Case frame: case_x =
kicad_x - 100, case_y = kicad_y - 70 (+Y south). Trackpad centre =
shell (0,48) = KiCad (100,118); dia.40 keep-out = circle r20 at
(100,118).

## 1. Module selection

### 1.1 Signal budget the module must serve

From D-024 (common scheme) + D-049 + D-053:

| group | signals | count |
|---|---|---|
| Wing links (common) | MUX_A0/A1/A2 (out), MUX_OUT_A/B/C (ADC in) | 3 + 3 |
| Wing enables | HALL_PWR_EN, MUX_EN0, MUX_EN1 (out) | 3 |
| Trackpad | I2C SDA, SCL, DR interrupt (in) | 3 |
| Battery | VBAT sense (ADC in, gated divider) | 1 |
| Human interface | pairing/mode button, status LED | 2 |
| **Total** | | **15 GPIO, of which 4 ADC-capable** |

USB comes from the module's own USB pins (Section 3); SWD is
test-pad only. nRF52840 offers 48 GPIO / 8 AIN (Nordic PS), so any
full module passes; the XIAO standard's 11 edge GPIO do NOT (see
1.3).

### 1.2 Candidates

| module | size (mm) | antenna | GPIO | Japan cert | notes |
|---|---|---|---|---|---|
| Taiyo Yuden **EYSKDNZWB** | 9.6 x 12.9 x 1.3 | pattern, one end | 46 | maker datasheet: Japan certified (Taiyo Yuden lineup doc) | internal 32 kHz + DCDC LCs; Kaga FEI lists it as former name of current **ED2840AA2** |
| Taiyo Yuden EYSKBNZWB | 10.0 x 15.4 x 2.0 | PCB, one end | 46 | maker datasheet: FCC/IC/Japan certified | former name of EB2840AA2 (Kaga FEI table) |
| Raytac **MDBT50Q-1MV2** | 15.5 x 10.5 x 2.05 | ceramic chip, one end | 48 | Telec listed by maker approval sheet (Telec cert section) + Nordic module docs | variants: -P1MV2 PCB antenna, **-U1MV2 u.FL**; Zephyr board target exists (raytac_mdbt50q_db_40) |
| Seeed **XIAO nRF52840 Plus** | 21 x 17.8 | ceramic, one end | 20 (maker wiki) | **VERIFIED**: Japan Certificate of Construction Type **222-257139**, issued 2025-04-25, models "XIAO nRF52840-Plus / Sense-Plus", ceramic antenna 2.09 dBi, 10 mW (Seeed certificate file) | dev-board form: onboard USB-C, BQ25101 LiPo charger (must stay unused, D-048 forbids in-device charging), reset button, LEDs |
| Seeed XIAO nRF52840 (standard) | 21 x 17.8 | ceramic, one end | 11 edge + bottom pads | **UNVERIFIED at certificate level**: Seeed's wiki/SOM doc state a TELEC-inclusive cert pack exists for this model, but the only certificate retrieved in this study is the Plus one above (222-257139), which names Plus models only. Carried as a named risk, exactly as left open by Issue #288 | deepest stock of all candidates; PO has footprint assets (used socketed in Issue #288) |

### 1.3 Verdicts

- **XIAO standard — rejected for the product Main.** Two independent
  reasons: (a) 11 edge GPIO < the 15-signal budget of 1.1; closing
  the gap needs its bottom pads (hand-solder class, and several are
  committed to its internal battery-sense/charger circuitry);
  (b) its own Telec certificate number remains UNVERIFIED (1.2).
  It remains the right bench module (Issue #287/#288 use).
- **XIAO Plus — fallback / prototype carrier.** Certificate
  VERIFIED and 20 GPIO pass the budget, but: dev-board baggage
  (LiPo charger to keep permanently idle, onboard USB-C that
  duplicates Section 3's connector), 21 x 17.8 mm does not fit any
  site on the unmodified outline (Section 4), and DigiKey stock was
  0 on 2026-11-19 (Seeed-direct channel not checked). Socketed use
  also adds ~2-3 mm of stack height under the bay panel — a fitted
  audit Stage 2 would have to clear; soldered modules (1.3-2.2 mm)
  sit inside the Rev.10 component-height envelope class.
- **MDBT50Q-1MV2 — fallback if the primary's channel fails.** Cert
  verified, cheapest ($6.15), Zephyr-supported, and the -U1MV2 u.FL
  variant is the antenna-freedom insurance. But at 15.5 mm long it
  fits NO site on the unmodified outline (Section 4); adopting it
  forces the north-tab outline change of Section 4.3.
- **EYSKBNZWB — rejected on size**: 15.4 mm long, same fit failure
  as MDBT50Q, without the u.FL escape variant.
- **EYSKDNZWB — RECOMMENDED (primary).** The only candidate that
  fits the unmodified Rev.10 outline (Section 4.2), maker-certified
  for Japan, 46 GPIO, internal clock/DCDC inductors (no external
  RF support parts), 1.3 mm tall. Its antenna end faces south in
  the chosen site, conforming to D-053's south PETG zone with no
  amendment. Two named risks, both gated in Stage 2 (Section 6):
  (R1) today's stock could not be retrieved (UNVERIFIED, not
  observed thin — see availability table); (R2) lifecycle rename —
  Kaga FEI (Taiyo Yuden's distributor) lists EYSKBNZWB as the
  former name of current product **ED2840AA2**; Stage 2 orders by
  whichever name is current and re-verifies pin compatibility
  against the EYSKDNZWB datasheet before layout.

### 1.4 Availability scan (observed 2026-11-19)

| SKU | channel | stock | price | lifecycle |
|---|---|---|---|---|
| EYSKDNZWB / ED2840AA2 | DigiKey JP / Chip1Stop | **UNVERIFIED** (no figure retrieved) | UNVERIFIED | Active under new name ED2840AA2 (Kaga FEI former/current table) |
| MDBT50Q-1MV2 | DigiKey Marketplace (3271-MDBT50Q-1MV2-ND) | 35 | $6.15 (+$25 flat shipping, ~14 d) | Active |
| MDBT50Q-1MV2 | TME (MDBT50Q-1MV2-TR) | 88-176 (snapshots 2026-10-07 / recent listing) | ~$7.86 @1 | Active |
| MDBT50Q-1MV2 | LCSC (C5118826) | 0 | — | listed, out of stock |
| XIAO nRF52840 | DigiKey | 2,075 | $10.38 (Issue #288 also observed DigiKey JP 2,025 @ JPY 1,711) | Active |
| XIAO nRF52840 Plus | DigiKey US / CA | 0 / 5 | $9.90-10.40 | Active (2025 model) |
| XIAO nRF52840 Sense Plus | DigiKey | 92 | $16.40 | Active |

Flag: every soldered-module channel is thin (tens) or unverified;
only the XIAO standard is deep. This is a hobby-quantity project
(1 Main + spares), so tens suffice — but the Stage 2 gate
(Section 6) re-verifies before layout starts, per the project's
part-selection stock rule.

## 4. Outline and keep-out map (from Rev.10 board data)

### 4.1 What carries over

Rev.10 outline (bbox KiCad x 64.107..135.893, y 75.732..137.900;
area 2,644.24 mm2; REPORT.md) and the three symmetric holes —
H1 (100, 79.268), H2 (68.107, 134.400), H3 (131.893, 134.400),
each with its dia.5 all-layer copper reservation (D-023 lineage)
— **survive unchanged in the recommended configuration**. No
keep-out below forces an outline change; the revolution is
internal placement: the dia.40 trackpad keep-out evicts the whole
central field of Rev.10 (U1 RP2040 at (100,119), U3, U4, U6+L1
power stage, most passives all sit inside r20 of (100,118)).

### 4.2 Keep-out / site map (KiCad mm)

| zone | geometry | consequence |
|---|---|---|
| Trackpad keep-out | circle r20 @ (100,118) | no components; the pad's FFC disconnect lands in the north slivers (y 98..103, x 84..91 or 109..116 — the only free strips between circle rim and the J2/J3 tab tops at y=103.196) |
| **Module site (SW pocket)** | x 69.5..79.1, y 118.4..131.3 (9.6 x 12.9, antenna end south) | bounded by: J2 FH12 body south reach y=117.87 (0.53 clear), west outline slant (0.74 clear at NW corner), H2 dia.5 reservation (0.9 clear), trackpad circle (0.9 radial clear at NE corner). C18 (78.5,126) and U5 (82,126) area re-planned around it. Mirror site at SE exists; SW chosen so the SE south edge stays free for the battery connector |
| Antenna shadow | board strip south of module, y 131.3..137.9, x 69.5..79.1 | no copper pour / no components (maker layout rule for the pattern antenna); radiates into the straightened south band (13.802 mm deep, case frame) and the PETG south wall — D-053 conformance |
| Battery connector | south edge at ~(124, 136), facing south | outside the circle (dx=24), 8.05 from H3 centre (reservation r2.5), clear of the antenna shadow; shortest pod-cable entry |
| South band (case) | case Y 67.9..81.7 in front of Main's south edge | kept free of tall Main-side features: the only south-edge items are the low battery connector and the antenna shadow — the band stays usable for the pod cable dress |
| USB-C | north wall — see Section 3 | NOT on the outline: the receptacle sits on a short internal bracket/riser at the freed J4/Fly seat (J4 was at (100,90)); no outline change |

Why the module cannot go north or east on this outline (measured,
not remembered): the north apex is a converging triangle — the
NW/NE outline edges run (82.144,103.196)->(102,75.732) and mirror;
at y=100 the free strips beside the circle are 6.8 mm wide, at
y=103 they are 4.7 mm. A 15.5 mm module fails there, fails in the
SW/SE pockets (max N-S span 13.1 mm between the FH12 body reach
y=117.87 and the H2/H3 reservation), and fails east/west of the
circle (J2/J3 tabs). Only the 12.9 mm EYSKDNZWB fits, in the SW
pocket, at >=0.5 mm clearances.

### 4.3 The rejected outline change (fallback only)

If the EYSKDNZWB channel fails its Stage 2 gate, the fallback
(MDBT50Q-1MV2) forces exactly one outline change: a symmetric
**north tab**, north edge at KiCad y=70.0 (case Y 0.0), x 86..114
(28 wide), sides vertical to their intersections with the existing
slants at y~97.9; added area ~+420 mm2 (+16%); holes unchanged.
The tab would host the module + a tab-mounted USB-C at the north
wall, with the module's chip antenna facing north — which then
also needs a D-053 note amending the antenna home from "south
PETG zone" to "un-plated PETG wall zone" (the north wall is the
same PETG, outside the aluminium plate span), or the -U1MV2 u.FL
variant with its antenna element in the south band. Recorded here
so the fallback is a decision, not a surprise.
