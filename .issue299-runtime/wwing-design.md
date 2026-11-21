# Issue #299 Stage 1 — Wireless Wing design study

**Status: Stage 1 study (design only — no layout, no order).**
Scope: wireless-variant Wing boards (16L / 16R / 17L / 17R) succeeding
Wing Rev.6: DRV5055A3 → TMAG5253BA3, HALL_5V → HALL_3V3, EN per bank.
All claims below cite file-level evidence in this repo or a named
primary datasheet. Companion data: `wwing-design.json`,
`rail-budget.py` / `rail-budget.txt` (this directory).

## 1. Circuit-reuse map (#288 Matrix → wireless Wing)

Wing Rev.6 census (extracted from each variant's `main.kicad_pcb`,
`hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-*/`):
**identical in all 4 variants** — 21× DRV5055A3QDBZR (groups A/B/C × 7),
3× TMUX1208PWR, 24× 100 nF (21 sensor + 3 MUX decoupling), 15 test
points, 1× FH12-14S-0.5SH(55) (`J_WING`). MUX wiring from placed pads
(16L): S1..S7 = sensors 0..6 of the group, pin 2 (EN) = `WING_EN`,
VDD = rail, outputs `MUX_OUT_A/B/C`; address pins common `MUX_A0..A2`.
`J_WING` pads (Wing-side numbering): 1 = rail, 2/4/8/10/12/14 = GND,
3/5/6 = MUX_A0/A1/A2, 7 = WING_EN, 9/11/13 = MUX_OUT_A/B/C — exactly
the D-024 content the wireless Main was built against (#292 REPORT
census: Main physical pads 14 = HALL_3V3, 8 = MUX_EN0/1 after the
FFC k→15−k reversal absorption; signal content identical).

| Block | #288 evidence | Wing disposition |
|---|---|---|
| TMAG channel: VCC ∥ 100 nF (GRM188R71C104KA01D, LCSC C45000) to GND; OUT direct to MUX S pin; EN to bank net; EP (pad 5) to GND | `issue-288-wmatrix/REPORT.md` §1–2; `manufacturing/BOM-jlcpcb.csv` (18× TMAG C22401868, 21× 100 nF); placed pads of U_HA0 in `wmatrix.kicad_pcb` | **Copy verbatim, ×21 per Wing.** The Rev.6 board already carries the identical 100 nF part at every sensor and MUX (24×, same MPN, extracted above) — only the net name changes HALL_5V → HALL_3V3. No series element on OUT in either design. |
| MUX bank wiring: TMUX1208PWR (C494728), S1..S6 sensors + S7 = GND offset ref + S8 = REF_RAIL on Matrix | #288 REPORT §1 (groups by column pair; addr 6 → GND, addr 7 → HALL_3V3/2 via shared 10k/10k) | **Copy the chip and the address map; do NOT copy the reference rows.** The Wing's groups are already fully populated 7/7 (S1..S7 = sensors, from Rev.6 pads) and the link has no free pin for a reference channel (14/14 assigned). Offset/gain reference remains a Matrix-eval-board function (D-049 condition 1 vehicle); product Wings rely on ratiometric closure + per-key endpoint calibration (§2.3). |
| EN per bank: Matrix drives EN_A/B/C as separate MCU nets; MUX EN pins tied to rail (MUXes always on) | #288 REPORT §1–2 | **Change, per D-049:** on the Wing there is exactly one enable net, `WING_EN` (= Main's MUX_EN0/1). It already drives all 3 MUX EN pins (Rev.6 pads); the swap additionally ties all 21 TMAG EN pins to it. "Bank" = the 21-key Wing bank — the decision record's own definition (`docs/decisions.md` D-024 record: "MUX_EN0 and MUX_EN1 select the 21-key bank"; #282 §3d per-bank row: 21 sensors on). Per-group EN inside a Wing is impossible without new link nets and was not adopted. |
| EN idle state: no pull-down on Matrix EN nets (BOM has none) | #288 BOM (resistors: shunt, divider, LED, CC only) | **Copy (none).** On the Wing, WING_EN is driven push-pull from Main whenever SYS is alive; the Wing rail itself is TPS22919-gated default-off, so sensors are unpowered whenever the system is off or the FFC is unmated. No floating-EN-with-power state exists. |
| Rail practice: dedicated sensor rail, MUX VDD on the same rail, 0R measurement shunt (Matrix-local LDO design) | #288 REPORT §1 | **Adapt:** the Wing has no regulator — HALL_3V3 arrives over the link from Main's TPS22919 (D-058). Wing-side rail practice copied = per-device 100 nF + zone distribution (§3). The Matrix's REF divider and shunt are eval-board furniture, not copied. |
| Test points: Matrix 25 TPs incl. raw sensor taps at donor positions | #288 REPORT §1 | **Copy the pattern:** Rev.6 already carries 15 TPs incl. raw taps (TP_H_*_RAW) and net posts (rail, EN, A0–A2, MUX_OUT_A/C, GND×4); keep the set, rename the rail TP. |

## 2. Sensor swap study — DRV5055A3 (SOT-23) → TMAG5253BA3 (X2SON-4)

### 2.1 Pin-map translation (from placed footprints, cross-checked to datasheets)

DRV5055 DBZ (Rev.6 `hall` footprint, U_HA0 local frame):
pad 1 = VCC (−1.016, +0.95), pad 2 = OUT (−1.016, −0.95),
pad 3 = GND (+1.016, 0); pads 1.309 × 0.46 mm, 0.95 mm pitch column.
Datasheet SBAS640C pin functions agree (1 VCC / 2 OUT / 3 GND).

TMAG5253 DMR (wmatrix `TMAG5253BA3_X2SON-4`, U_HA0 local frame):
pad 1 = VCC (−0.25, −0.70), pad 2 = GND (−0.25, +0.70),
pad 3 = EN (+0.25, +0.70), pad 4 = OUT (+0.25, −0.70),
pad 5 = EP/GND (0, 0), 0.80 × 0.60. Lands 0.22 × 0.40 mm,
columns ±0.25, rows ±0.70. Datasheet SBASAI5E Table 5-1 agrees
(1 VCC / 2 GND / 3 EN / 4 OUT) and drawing DMR0004A gives the same
land geometry.

**The two presentations are not rotations of each other.** The DRV
puts VCC/OUT on one column and GND alone opposite; the TMAG is a
2×2 quad (VCC/OUT on one diagonal, GND/EN on the other) plus a
centre EP that must be soldered to GND (DMR0004A note 3). Per the
Wing Rev.2 lesson, Stage 2 copies the #288 footprint verbatim and
re-derives each site's rotation from the channel's routing
presentation, then proves pad↔net assignment from placed pads
(the #288 `verification-s2.json` method: assignment extracted from
the placed board, 0 errors) — never from footprint symmetry.

### 2.2 Land pattern proposal (Stage 2 starting point)

**Adopt the #288 land pattern unchanged**: TI DMR0004A example
layout (lands 0.22 × 0.40, NSMD preferred, EP 0.80 × 0.60 soldered
to GND, stencil per the drawing's example stencil design). Rationale:
(a) it is the TI drawing, not a house invention; (b) the #288 board
is the D-049 condition-2 yield vehicle — if its yield data forces
any land/stencil change, one change propagates identically to both
boards; diverging the Wing land now would invalidate the transfer.
JLCPCB practice notes for X2SON at this size: no-lead package —
no visual joint inspection (JLCPCB X-ray is not part of the
economic flow), so the yield gate is electrical (the Matrix board's
18/18 channel extraction + bench readback), and paste volume on the
EP is the float/tilt risk the stencil example controls. Stage 2
must gerber-diff the Wing paste apertures against the #288 set
before package freeze.

### 2.3 Output / reference implications for the Main side

Both sensors are **ratiometric ∝ VCC** (#282 datasheet table:
DRV5055 A3 25 mV/mT @5 V ratiometric; TMAG BA3 15 mV/mT @3.3 V
ratiometric, VQ = VCC/2). There is no fixed-reference surprise:
- The DRV-era divider (6.8k/10k, ×0.595) exists only because the
  5 V-domain output could exceed the ADC domain. At 3.3 V the TMAG
  swing (1.83 → 2.70 V over the recorded 12 → 70 mT field) is
  native to the ADC range; D-049 deletes the divider, the RC node
  filter stays (#292 §5.1). Source resistance at the ADC node
  collapses ~4 kΩ → ~10 Ω (TMUX RON 9 Ω typ @3.3 V + TMAG ROUT
  1.27 Ω, #282 §3b), so per-step settling stops being a scan term.
- What does NOT cancel: the sensor's local VCC is HALL_3V3 (after
  the TPS22919 + FFC drops of §3), while the module ADC references
  its own SYS_3V3 domain. The residual is a pure scale error
  δ/3.3 V — 0.73 % at the expected drop — inside the per-key
  endpoint calibration that already absorbs the TMAG's ±15 %
  sensitivity spread (#282 §2). The Matrix board's REF_RAIL channel
  exists to *measure* this class of error on the bench (its XIAO
  ADC domain is unrelated to its LDO rail); the product chain
  needs no link pin for it.
- EN thresholds: VIH = 0.65 × VCC ≈ 2.15 V at 3.3 V — Main's
  3.3 V-domain GPIO drive clears it with the rail drop included
  (far-end VCC ≥ 3.25 V in every §3 corner). Shutdown draw 8 nA typ
  per sensor (EN low) — 0.17 µA per Wing, negligible vs the model.

### 2.4 Keep-out / height / sensing-plane deltas (inside the switch footprint)

| Item | DRV5055A3 (Rev.6) | TMAG5253BA3 | Delta |
|---|---|---|---|
| Package | SOT-23 2.9 × 1.6 mm class, **1.12 mm max height** (DBZ0003A) | X2SON 1.40 × 1.10 mm, **0.40 mm max height** (DMR0004A) | −0.72 mm profile; footprint area shrinks ~3× |
| Hall element, plan | package-centred ±50 µm (SBAS640C Fig. 6-5) | package-centred ±25 µm (SBASAI5E Fig. 8-3) | sensing centre stays at the site centre — Rev.6 field coordinates carry over 1:1 |
| Hall element, Z above seating plane | 650 ± 80 µm | 130 ± 15 µm | **element sits 0.52 mm closer to the board** (0.52 mm farther from the switch magnet) |
| Solder keep-out | 3 gull-wing lands | 4 lands + centre EP, all under the body outline | no keep-out growth; EP via-in-pad rules per DMR0004A note 6 (fill/plug/tent if used) |

The Z delta is the one physical change the field record does not
already cover: `docs/hall-acquisition.md` §1's 12 → 70 mT was
recorded at the DRV element plane. Moving the element 0.52 mm away
from the magnet reduces the presented swing somewhat (direction:
less saturation risk, slightly less span) — quantifying it is
exactly D-049 condition (1), measured on the #288 board with the
real stack, whose sensor sits at the same 130 µm plane. No Wing
layout choice can change it; it is recorded here so Stage 2 does
not treat the DRV-era span as a placed-board expectation.

## 3. Rail + link budget at 3.3 V (recomputed from tree figures)

**Census (per Wing, from §1):** 21 TMAG + 3 TMUX1208 on HALL_3V3.
**Burst discipline (D-024/D-049):** one Wing enabled at a time;
that Wing's whole 21-sensor bank is on for its 7 address steps.
Burst current: typ 21 × 2.6 mA + 3 × 0.1 mA = **54.9 mA**;
datasheet-max 21 × 5 mA + 0.3 = **105.3 mA** (TMAG ICC 2.6 typ /
5 max mA @3.3 V, SBASAI5E via #282 §1; MUX at the #288 droop
basis of 0.1 mA each — conservative vs its ~10 nA-class IDD).

> **Basis correction recorded:** the #292 Stage 1 study costed its
> far-Wing budget at "one bank of 7 sensors / 20 mA class"
> (`.issue292-runtime/wmain-design.md` §5.2) and the as-built
> REPORT at 28 mA. That conflicts with the decision record's bank
> definition (21-key bank, decisions.md D-024 record; #282 §3d/§4
> model: 21 on). The budget below uses the 21-sensor bank. The
> correction does not indict the adopted Main: its extracted branch
> copper (0.09 Ω) is a minor term either way, and the ≤50 mV class
> still passes at production lanes (below). Stage 2 must not
> inherit the 7-sensor figure.

**Chain elements** (script: `rail-budget.py`, output
`rail-budget.txt`): TPS22919 RON 90 mΩ typ @3.6 V (TI SLVSEN5B;
135 mΩ used as a max-class bound) → Main branch copper 0.090 Ω
(extracted as-built, #292 REPORT) → FH12 mated pair → FFC loop
(supply lane R + 6 GND lanes ∥ = R × 7/6; expected lane 0.075–0.10 Ω
per the D-042 amendment record; #292 counted one FH12 pair, this
budget counts both mated pairs at the same 60 mΩ class — the
conservative direction) → Wing distribution: HALL zone pour on
F.Cu + 0.30 mm branches, GND zone on B.Cu (extracted from Rev.6
16L `main.kicad_pcb`: F.Cu HALL_5V zone, 478.6 mm of 0.30 mm
segments, B.Cu GND zone), Stage-1 bound ≤25 mΩ effective,
farthest sensor U_HA4 at 102 mm (16 mm) / 108 mm (17 mm) from
J_WING — Stage 2 replaces the bound with an extracted computation
(the #292 G4 method).

| Corner | Drop @ typ burst | Drop @ max burst | Verdict vs ≤50 mV class |
|---|---|---|---|
| Expected lanes 0.10 Ω, RON typ (R = 0.442 Ω) | **24.2 mV** (far VCC 3.276 V) | **46.5 mV** (3.253 V) | PASS / PASS (max corner margin 1.08×) |
| Expected lanes, RON max-class 135 mΩ (R = 0.487 Ω) | 26.7 mV | 51.2 mV | PASS / at the line (+1.2 mV) |
| Proposed wireless lane acceptance 0.30 Ω (R = 0.675 Ω) | 37.1 mV | 71.1 mV | PASS / over — scale error 2.15 %, calibration-absorbed |
| Legacy wired lane acceptance 1.30 Ω (R = 1.842 Ω) | 101.1 mV | 193.9 mV | over — function unaffected (far VCC ≥ 3.11 V ≫ 1.65 V floor), error budget blown |

**Budget fixing (D-049 left the successor metric "≤50 mV class,
to be fixed at variant design time" — this study fixes it):**
the wireless far-point budget is **≤50 mV at typ burst current
with production lanes** — met at 24.2 mV (2.1× margin). The
datasheet-max-current corner is dispositioned as a ratiometric
scale error ≤1.6 %, absorbed by per-key endpoint calibration
(the same mechanism that absorbs the ±15 % sensitivity spread);
it is not a functional limit in any corner (worst far VCC
3.11 V vs the 1.65 V sensor floor and the 2.15 V EN threshold).
**Stage 3 action:** give the wireless build its own FFC lane
acceptance of **≤0.30 Ω/lane** in the build guide (production
lanes measure 0.075–0.10 Ω, so this is 3× headroom, not a
tightening of practice — the 1.30 Ω figure was set for the
wired 127 mA design load and is simply the wrong inheritance).

## 4. Runtime-model delta check (D-050 basis: 16.2 d; 15.7 d with trackpad)

The #284 model (`.issue284-runtime/mcu-power.md` §b: 42 channels,
14 MUX steps, 0.35 ms sensor window) takes its sensor term from
#282's per-bank configuration: 21 sensors on per burst, one Wing
at a time, 2.6 mA typ, window 0.35 ms (45 µs tON + 14 × 20 µs
steps, #282 §4). This design is that configuration, part for
part: same sensor, same per-Wing bank EN, same MUX/address scheme,
same decoupling. **Delta: none.** The Wing adds no always-on load
(MUX IDD ~10 nA class; sensor shutdown 8 nA × 21 ≈ 0.17 µA per
Wing, both inside the model's rounding). The 16.2-day figure
(15.7 with the D-053 trackpad accounting) stands; the §3 basis
correction touches a voltage budget, not an energy term — the
model already charged the true 21-sensor bursts.

## 5. Variant plan (16L / 16R / 17L / 17R)

- **Shared (one design, four placements):** the complete schematic
  content — channel circuit, MUX scheme, connector, decoupling,
  TP set — is variant-independent (Rev.6 census is identical in
  all four, §1). Stage 2 should generate all four from one
  parametric source, as Rev.6 was generated, not hand-fork.
- **Per-variant:** only the field geometry (16 vs 17 mm pitch),
  the outline/notch/mirror (inherited from the corresponding
  Rev.6 board, deviation target 0.0000 mm on sensor sites), and
  the resulting routing. Left/right are distinct boards (not a
  flip pair) exactly as in Rev.6.
- **Effort shape:** schematic work is done once; layout risk
  concentrates in the first variant routed (expected: 16L, the
  Rev.6 study donor); the other three inherit its channel escape
  patterns by symmetry/pitch transform, each still gated
  individually (field deviation, DRC, via-pad minima, assignment
  extraction).
- **Flip preservation (D-046/D-051):** flipped installation flips
  the **Main**, not the Wings. Its only electrical consequence is
  the EN0↔EN1 swap, verified from pad-net data in the #275 record
  and firmware-absorbable; the Wing presents the identical
  interface in both poses — `WING_EN` is just whichever Main
  output arrives, and the FFC reversal is absorbed in Main's
  footprint assignment (#292 §5.1), not the Wing's. The swap
  changes nothing on the Wing: same connector pose (bottom-contact
  FH12 at the Rev.6 site), same nets, same bank structure. One
  Stage 2 check: the TMAG footprint rotation at each site must be
  chosen against the Rev.6 site presentation (which already
  encodes the flip-qualified geometry), not re-derived.

## 6. Availability scan (observed 2026-11-20)

Per-build need for the full run = 4 variants × 5 boards = 20 Wing
boards → TMAG 420 pcs, TMUX 60 pcs, FH12 20 pcs. The 10× rule is
applied to those figures. Numeric JLCPCB stock is not exposed by
the public LCSC/JLCPCB pages or the jlcsearch index (stock: null,
checked 2026-11-18/11-07/11-11) — the same limitation the #288
package recorded; numeric counts below are the project's last
quote-screen/record observations, and the standing rule from
#288 applies: **re-check numeric stock on the JLCPCB quote
screen before any order.**

| Part | LCSC | Status today (2026-11-20) | Last numeric observation | Need / 10× | Flag |
|---|---|---|---|---|---|
| TMAG5253BA3IQDMRR | C22401868 | LCSC **InStock** $0.4214; JLCPCB **InStock**, Extended | 2,981 pcs (JLCPCB quote screen, 2026-11-19, #288 quote record); #288 Stage 1 separately recorded 1,126 the same day — treat the lower as governing | 420 / 4,200 | **FLAG: below 10× of the full-run need** on either observation (2.7–7.1×). Not a Stage 2 blocker (design only); it paces Stage 3 — order the sensor quantity early or accept per-variant batches (105 pcs/batch; 10× = 1,050, straddled by the observations). Also the #282 trap stands: pin **BA3** explicitly — the BA1 sibling sits on an adjacent code. |
| TMUX1208PWR | C494728 | LCSC **InStock** $0.3008 | not numerically observed | 60 / 600 | Numeric unverified; commodity TI part already carried on the #288 BOM — re-check at quote. Low concern. |
| FH12-14S-0.5SH(55) | C5378715 | jlcsearch lists it, $0.5416 (checked 2026-11-11) | 3,907 pcs (JLCPCB, 2026-11-17 project record) | 20 / 200 | OK — 19× the 10× threshold at last count. |

## 7. Risk register for Stage 2

| # | Risk | Exposure | Mitigation / sequencing |
|---|---|---|---|
| R1 | **D-049 condition (2) — X2SON yield at JLCPCB** lands after Wing layout and forces a land/stencil change | Land pattern is the single most rework-expensive item: 21 sites × 4 variants, inside the switch footprint, with field coordinates frozen | Stage 2 copies the #288 land verbatim (§2.2) so any change is one footprint edit + regeneration, not a redesign. Sequence Stage 2 as: footprint/land freeze LAST among schematic-level decisions; route one variant (16L) first; hold the other three until either the Matrix yield data lands or PO accepts the residual risk explicitly. |
| R2 | **D-049 condition (1) — measured travel curve/noise** disappoints (element plane −0.52 mm, §2.4; noise 1.4×) | Would reopen the sensor choice itself (D-049), invalidating all Wing layout | Not layout-mitigable; it is a PO gate on adoption/order, not on design. Stage 2 proceeds in parallel per the issue's gate note; no Wing-specific spend before the Matrix data. |
| R3 | Budget-basis drift: a downstream stage re-inherits the #292 7-sensor/20 mA figure | Rail or lane-acceptance decisions made on a 3×-low current | §3 records the correction with its sources; Stage 2's extracted-resistance gate recomputes from placed data at 54.9/105.3 mA. |
| R4 | TMAG stock pacing ( §6 flag) | Stage 3 order stalls or splits | Decide batching at Stage 3 with a fresh quote-screen count; consider securing the 420-pc sensor quantity ahead of the Wing order itself (PO gate). |
| R5 | Per-site footprint rotation errors (quad package, diagonal pin pairs) | Dead or cross-wired channels that DRC cannot see | #288 method as a hard gate: channel assignment extracted from placed pads per variant, 0 errors tolerated; EP-to-GND verified per site. |
| R6 | FFC lane acceptance inheritance (1.30 Ω wired figure) | Error budget blown at otherwise-good builds (§3) | Stage 3 build-guide action: wireless acceptance ≤0.30 Ω/lane (§3). No board change. |
| R7 | Via-pad minima in the denser TMAG escape field (X2SON lands at 0.5 mm column pitch vs SOT-23 0.95 mm) | Floor-class sites like #288's disclosed 0.1002 mm minimum | D-021 rules unchanged; report the minimum as a number per variant with item-level disposition (issue pass condition); the sensor field gets the containment-class review, never a wholesale disposition. |

**Stage 1 conclusion:** the wireless Wing is a part-for-part
sensor/rail swap on a frozen Rev.6 skeleton, reusing the #288
channel design wholesale. Nothing in the study blocks Stage 2.
The two open items that can still move the design are both
D-049 conditions discharged by the #288 board — land pattern
(R1) above all — and Stage 2 should sequence around them as
registered above.
