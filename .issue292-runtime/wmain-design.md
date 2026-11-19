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

## 2. Power tree

Pack (D-048): NiMH AA x4 — fresh ~5.8 V, nominal 4.8 V, end of
discharge ~3.6-4.0 V. The TPS63070-class input lineage
(2.0-16 V, cold start >=3.0 V; Issue #280 aa-sizing) covers the
whole range with margin — the 2xAA rejection there (fresh 2.9 V
< 3.0 V cold start) does not apply at 4 cells.

```
NiMH x4 --[battery conn, SE south edge]-->+--> TPS63070 --> SYS 3.3 V
USB-C VBUS --[diode-OR, no back-feed]---->+   (buck-boost,    |
                                              output re-set   +--> module VDD (direct)
                                              5.2 V -> 3.3 V) +--> TPS22919 --> HALL_3V3 --> J2/J3 branches
                                                              +--> load switch --> PAD_3V3 (trackpad)
Pack + --[gated 1M/1M divider]--> module AIN (VBAT sense)
```

- **One converter, re-set.** The qualified TPS63070 stage
  (U6 lineage) is kept; only its output setpoint changes
  5.2 V -> 3.3 V. D-026's forced-PWM requirement is dropped —
  it served the 5.2 V / 254 mA ripple budget; wireless loads are
  mW-class bursts, so power-save mode is correct here and
  protects the away-state floor.
- **AP2112K LDO (U4 lineage) is deleted.** It existed to make
  3.3 V for the RP2040 from the 5.2 V rail. The module runs
  directly on SYS 3.3 V (all candidates accept 1.7-3.6 V).
- **Wing Hall rail**: SYS -> TPS22919 (U5 lineage, default-off,
  HALL_PWR_EN) -> two branches at the switch output (D-024
  pattern) -> J2/J3 pin 1. Burst regime per D-049/#282: one
  bank of 7 TMAG5253 on at a time per Wing, one Wing at a time
  (Section 5), peak 20 mA class, window 0.35 ms class.
- **Trackpad feed**: SYS -> its own small load switch ->
  PAD_3V3. The pad's internal sleep (40 uA class, D-053) is the
  normal discipline; the switch lets firmware hard-off the pad
  in the away state, buying the favourable end of D-053's
  runtime bounds (-0.4 d vs -0.5 d).
- **Battery sense**: gated divider (1M/1M, GPIO-gated in the
  XIAO READ_BAT pattern) from pack+ to a module AIN: 5.8 V max
  -> 2.9 V at the ADC, ~0 uA when gated off. Firmware
  thresholds: low warning 4.2 V (1.05 V/cell), critical 3.8 V
  (0.95 V/cell); the converter still cold-starts at 3.0 V, so
  warnings precede any brown-out by a wide margin.
- **No charge path exists.** VBUS reaches the converter input
  only through a diode-OR (or load-switch OR); a blocking
  element on the pack line makes back-feed into the NiMH
  impossible by construction (D-048: external charging only).
- **Runtime delta vs Issue #284**: the model (B1: 0.533 Wh/day,
  16.2 d on the pack) assumed a flat eta=0.85 converter. This
  tree keeps the same converter family at the same assumption
  class (TPS63070 at 4.8->3.3 V, mA-class loads: ~85-93%
  datasheet class), so **the 16.2-day figure stands**; with the
  trackpad's D-053 accounting, 15.7 days. No new term is
  introduced: the deleted LDO was inside the old model's Main
  overhead, and its removal is upside, not booked.

## 3. USB-C role (Fly daughterboard deleted)

**Recommendation: a bare USB-C receptacle belonging to Main** —
the module's native USB is the product's firmware lifeline
(DFU/UF2-class updates, bench logging), and the nRF52840's USB
is already paid for in every candidate module.

- Receptacle: 16-pin USB-C, ESD array on D+/D- (USBLC6-class),
  5.1 kohm CC pull-downs (the keyboard is a sink/UFP), VBUS
  into the Section 2 diode-OR. Differential routing per D-019
  rules.
- Placement: at Main's north apex, on a **mini-tab <=10 mm wide
  x <=12 mm deep** (added area <=120 mm2, holes unchanged), its
  mouth at the north wall — the wireless case (already a new
  design: pod, straightened south, Fly seat deleted) puts its
  USB opening there, where the Fly mouth sat in the wired case
  (D-037/D-035 arrangement). If Stage 2's fitted audit prefers
  zero outline change, the bounded alternative is a minimal
  carrier at the freed Fly seat plugging the existing J4
  EZmate footprint (D-035 interface, qualified) — one of the
  two, decided by that audit, not by taste.
- SWD test pads are retained (Rev.10 TP1-TP4 precedent) as the
  recovery path if USB DFU is ever bricked.
- Rejected: **header-only debug interface** — saves ~$0.6-1.0
  of parts and makes every firmware update depend on a probe;
  disproportionate for the product's lifeline. Rejected:
  **keeping a Fly-style daughterboard** — an extra board and a
  ~10-cycle EZmate interface (D-035 record) buying nothing now
  that the MCU has native USB.

## 5. Wing-link electricals (3.3 V design)

### 5.1 Pin assignment — content invariant, rail renamed

The FH12/FFC link keeps D-024's signal content exactly; only
pin 1's rail changes identity (5.2 V design -> 3.3 V):

| FH12 pin | wired (D-024) | wireless |
|---|---|---|
| 1 | HALL_5V | **HALL_3V3** |
| 2,4,8,10,12,14 | GND (six returns) | unchanged |
| 3,5,6 | MUX_A0/A1/A2 (common) | unchanged |
| 7 | per-Wing enable (J2: MUX_EN0, J3: MUX_EN1) | unchanged |
| 9,11,13 | MUX_OUT_A/B/C (common ADC) | unchanged |

The conductor-order reversal of the stock FFC (k -> 15-k,
D-042 amendment) is absorbed in the footprint assignment
exactly as in Rev.8/Rev.10. The divider removal (D-049) touches
only Main's ADC input network (the RC filter stays, the divider
ratio goes) — it frees no link pin, and none is needed.
**The interconnect hardware carries over unchanged**: FH12-
14S-0.5SH(55) bottom-contact at all four sites (D-043), stock
Molex 152660149 folded FFC + printed jig, pre-fold lane
acceptance <=1.30 ohm (see 5.2 for why it need not tighten).

### 5.2 Far-Wing rail budget (successor to the 4.60 V guarantee)

Design peak: one MUX bank on = 7 x TMAG5253BA3 @ 2.6 mA typ
(Issue #282, 3.3 V) = 18.2 mA + MUX quiescent -> **20 mA class**,
one Wing enabled at a time (D-024 discipline retained). The old
guarantee (farthest sensor >= 4.60 V at 127 mA continuous,
D-026) is retired with the 5 V rail; its successor is the
D-049 rail-drop budget <=50 mV.

| element | resistance | drop @ 20 mA |
|---|---|---|
| FFC loop (1 supply lane + 6 return lanes in parallel; expected lane 0.075-0.10 ohm, D-042 amendment) | 0.10 x (1 + 1/6) = 0.117 ohm | 2.3 mV |
| Main branch (Stage 2 design target, cf. Rev.10's extracted J3 branch 240.9 mOhm) | <=250 mOhm | 5.0 mV |
| FH12 contact pair (class) | ~60 mOhm | 1.2 mV |
| **Total, expected** | | **~8.5 mV — PASS, 6x margin** |
| Total at the legacy lane acceptance limit (1.30 ohm) | 1.30 x 1.167 + 0.31 ohm | **36.5 mV — PASS** |

The budget passes even at the acceptance limit because the
burst peak (20 mA) is 6.4x below the wired design load
(127 mA). Recommendation: **keep the <=1.30 ohm pre-fold lane
acceptance unchanged** — no build-guide rework; margin at the
limit is 1.37x, at expectation 6x. Ratiometric closure: sensor
supply and the module's ADC reference share the 3.3 V domain,
so the residual drop appears as <=0.26% of span (8.5 mV /
3.3 V), inside the setup-calibration absorption already
assumed for the TMAG's +/-15% sensitivity tolerance (#282).

## 6. Stage 2 outline and gates

Stage 2 = layout of this design as a new qualification tree
(Rev.10 lineage), then the standard package (BOM/CPL per #267
conventions, DRAFT / NOT FOR ORDER). Gates:

- **G1 (before layout)**: EYSKDNZWB / ED2840AA2 channel
  verification — stock at >=2 channels, and pin/datasheet
  compatibility of the current-name part against the
  EYSKDNZWB datasheet. On failure: fall back to Section 4.3
  (MDBT50Q-1MV2 + north tab) as a recorded decision, not an
  improvisation.
- **G2**: fitted audit against the wireless case — trackpad
  underside vs the dia.40 keep-out, battery pod, straightened
  south band, USB mouth alignment, shell-lift disconnect for
  the trackpad FFC.
- **G3**: DRC 0 / ERC 0 / unconnected 0; via-pad minimum vs
  the project's 0.10 mm floor yardstick, reported as a number.
- **G4**: extracted-resistance re-computation of Section 5.2
  from the placed board (branch loop target <=250 mOhm;
  far-Wing drop <=50 mV at 20 mA).
- **G5**: SW-pocket clearances re-verified from placed data
  (module courtyard vs J2 body, H2 reservation, circle,
  outline: each >=0.5 mm) and the antenna shadow kept copper-
  free on all layers.
- **G6**: power evidence — converter cold start at a 3.6 V
  pack, VBUS-OR no-back-feed verified at test points, gated
  divider draw ~0 in sleep.
- **G7**: FH12/FFC carry-over re-verified by pad-net census
  against Section 5.1 (the Rev.10 method).
- **G8**: firmware bring-up outline only (custom board
  definition for the module under nRF Connect SDK / ZMK;
  Unifying device stack per Issue #280/#287) — code is not a
  Stage 2 deliverable.
