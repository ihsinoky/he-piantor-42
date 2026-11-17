# Issue #263 — Board implementation round: REPORT

Architecture: D-042 as amended (2026-11-17). Wing Rev.5 (FH12-class
ZIF underside at the Rev.4 GH site) + Main Rev.8 (J2/J3 → ZIF),
cable = stock Molex Premo-Flex 152660149 folded on the printed jig
(Issue #264). Conductor order arrives reversed (k → 15−k), absorbed
in the Main Rev.8 footprint assignment.

**Headline outcome: the Wing side implements cleanly to one
residual open per variant; the Main side cannot be built at the
#261 poses — every ZIF signal pad falls OUTSIDE the Rev.7 board
outline (0.55–3.14 mm). This is a specification-level finding for
PMO/PO decision (options in §3.3). No yardstick was relaxed.**

## Stage 1 — ZIF part finalisation: PASS

Part: **Hirose FH12-14S-0.5SH(55)** — 14 pos, 0.5 mm pitch, bottom
contact, front-flip ZIF, SMT R/A, height 2.0 mm, 0.5 A/contact, Au.
DigiKey HFJ114CT-ND / HFJ114TR-ND. Cable compatibility confirmed:
Molex 152660149 (Premo-Flex 15266, Type A same-side contacts,
0.27 mm thick) vs FH12 FFC/FPC acceptance 0.30±0.05 mm — compatible;
127 mA/Wing ≪ 0.5 A rating. Contact resistance 50 mΩ max; mating
cycles 20 (accepted consumable premise, D-042).
Stock (dated web checks 2026-11-17): DigiKey in stock 4,996
(crawl 2026-11-09; OEMsTrade snapshot CT 5,930 + TR 4,000);
Unikeyic 2,742 (2026-11-12). Need 4/keyboard; ≥10× guideline
(40–80) PASS on those figures. **JLCPCB overseas stock NOT
confirmed — re-verify at order time** (standing flag). No LCSC
C-number for the 14S variant surfaced in public search.
Footprint authored from the FH12 catalog land table
(`connector/`, with provenance + uncertainty note): signal pad
length and MP geometry are engineering reconstructions —
**verify against Hirose drawing CL586-0533-0 before order release.**

## Stage 2 — Wing Rev.5: NEAR-PASS (1 open per variant)

Poses verified in case frame from built boards
(`pose-verification.json`): envelope centres (±27.0, −37.5) exact
vs #261 spec; mouths (±27.0, −34.3) vs slot −34.2. A footprint
frame error (mouth facing away from Main) was caught and fixed
during the round; the fix is recorded in the stage notes.

| variant | unconnected | wrong-net | material viol. | via-pad min | width floors |
|---|---|---|---|---|---|
| 16L | 1 | 0 | 2 (dangling) | 0.1013 | PASS |
| 16R | 1 | 0 | 0 | 0.1072 | PASS |
| 17L | 1 | 0 | 3 (dangling) | 0.1252 | PASS |
| 17R | 1 | 0 | 1 (dangling) | 0.1301 | PASS |

The single open in every variant is one J_WING GND pad whose pour
island is pinched off by neighbouring fanout tracks (17R: pad 4,
island 0.65 mm²). Closure attempts: KRT standard + escalation
'board' routes, plane-repair A* (reports NO PATH), cleanup cycles,
via-hop search (island too small for a 0.60/0.30 via). The neck is
set by the zone rules (min thickness 0.30, clearance 0.15), which
were NOT relaxed. Via-pad floor 0.10 PASS everywhere; the 0.125
target is met by the 17 mm pair only. Native Wing ERC unavailable
(inherited — no native Wing schematic), stated, not waived.
Wing-side FEM extraction could not complete: the solver asserts
all J_WING source pads share one component, which the isolated
GND pad breaks. Configuration Vfar therefore stands on the #264
system model (§3.4), disclosed as inherited.

## Stage 3 — Main Rev.8: FAIL at the spec poses (spec conflict)

### 3.1 The finding

At the #261 poses, **all 28 ZIF signal pads lie outside the Rev.7
Main outline** (signed distance of pad centres beyond the slanted
edges: J2 +0.55…+2.99 mm, J3 +1.24…+3.14 mm). KRT states it
plainly in its log: "28 target pad(s) at/over the board outline —
unreachable, SKIPPED", so no copper was ever drawn to the pads;
DRC consequently reports 28 unconnected pads and 3 edge-clearance
violations (0.173 / 0.000 / 0.000 vs the 0.200 rule). Rev.7's GH
connectors sat ~5 mm further inboard and were clear. #261's fitted
audit checked the connector envelopes against case bodies (contact
audit) but never against the board outline — the gap surfaces
exactly at this implementation round, as its REPORT anticipated
("bounded implementation-round task").

On-board at the spec poses would need the outline extended
≈4.1 mm beyond both slanted edges in the connector zones (max pad
excursion 3.14 + pad half-diagonal 0.77 + 0.20 clearance).

### 3.2 What was completed anyway

- Pin assignment: pad n ← D-024 signal (15−n) at J2/J3; schematic
  net labels swapped pairwise to match; **ERC 0** after the swap.
- **Assignment verification (position space): PASS** — lanes
  tracked by case-frame position through the recomputed #264
  five-fold transport (reversal confirmed) land on the correct
  D-024 signal at the Main pads, both sides, both pitches
  (`main-rev8/assignment-verification.json`); net sets equal
  Rev.7 per connector.
- Build defect found and fixed: Rev.7 kept copper (V5V2) passed
  under the FH12 fitting pads (shorts). build-main now removes
  any kept copper colliding with the new pads (+0.10 mm) before
  routing; shorts are gone in the final audit.
- Copper-diff locality, disclosed: 902 of 1167/831 track objects
  differ from Rev.7; changed-copper bbox 41.6 × 41.1 mm — **not a
  local change** (the Rev.7 lesson repeats: a connector swap on
  this board is a re-route).
- Via-pad min 0.1596 mm PASS (≥0.125 target).

### 3.3 Options for the pose conflict (PMO/PO decision)

(a) **Extend the Main outline** with tabs under both ZIFs
    (≈+4.1 mm past the slanted edges in the connector zones).
    Keeps the spec poses, the #264 fold plan and the case entry
    slots. Cost: the tray pocket for Main must be re-audited
    (pocket was cut for the Rev.7 outline + clearance) — Stage 4
    fitted audit must be re-run with the extended board solid.
(b) **Move the ZIFs inboard** to the nearest on-board poses
    (~5–7 mm toward centre). Breaks the #264 fold-plan landing by
    more than the S1 absorber range (±4 mm) and the case entry
    slots; fold plan + slot rework required.
(c) **Rotate the ZIFs** to lie along the slanted edges. Mouth
    headings change; fold plan rework; landing geometry must be
    re-derived.
Recommendation: (a) — it preserves every audited element of
#261/#264 and confines the change to the board outline + one
case-pocket re-audit.

### 3.4 Electrical (inherited model, disclosed)

Rev.8-native resistance extraction was not run (board unrouted at
the pads). The configuration's Vfar stands on the #264 system
model: loop 203.8 mΩ (assumed lanes) / 234.0 mΩ (pessimistic) →
**Vfar 4.786 / 4.782 V ≥ 4.60 V at 127 mA/Wing**, with Rev.7-class
Main copper terms (common 49.491 mΩ class). The paper guarantee
stays open by PO's acceptance; physical closure = pre-fold lane
measurement ≤1.30 Ω/lane (see package notes). Rev.8 extraction
must be re-run after the §3.3 decision lands a routed board.

## Stage 4 — Case production tree

`hardware/case/issue-263-lowdeck-production/` (README + audit
re-run). The #264 nominal fitted audit was re-run unchanged and
reproduces: gate 1 = 0 unexpected contacts at nominal (both
cables, all non-tray bodies; cable-vs-cable 0), sensS clean,
sensN's two named grazes only at a mis-set detent; service PASS
with #264's one named residual; gates 4/5 by inheritance; gate 7
print envelopes PASS. As-built connector envelopes match the
audited spec (Stage 2/3 pose records). **Caveat:** if §3.3 option
(a) is chosen, the Main pocket fit must be re-audited with the
extended board solid before printing trays. Gate 6 (Junana)
remains OPEN — keytop 22.00 provisional.

## Stage 5 — Manufacturing packages (DRAFT)

Per-board packages (gerber/drill/CPL/BOM + FABRICATION.md) under
`main-rev8/manufacturing/` and `wing-rev5-*/manufacturing/`,
generated by `make-packages.py`. All are **DRAFT — NOT FOR
ORDER** while the gates above are open; the Main package exists
for frame/CPL continuity only. The FABRICATION notes carry the
FFC purchase spec (152660149 ×2), the pre-fold measurement
procedure (≤1.30 Ω/lane, detent table) and the jig data pointer
(`hardware/case/issue-264-stockffc/sources/`).

## Draft decision text (for PMO to record; decisions.md untouched)

D-043 (draft): Main Rev.8 connector placement — the #261 poses
are infeasible on the Rev.7 outline (all ZIF pads off-board,
0.55–3.14 mm). Adopt option (a)/(b)/(c) of Issue #263 REPORT
§3.3 and re-run the affected audits (case pocket for (a); fold
plan for (b)/(c)) plus Rev.8 resistance extraction before the
Main manufacturing package leaves DRAFT.

## Remaining before an order

1. **PMO/PO decision on §3.3** (Main pose conflict) + follow-up
   round: routed Rev.8, DRC/ERC 0, resistance extraction, and
   (option a) case-pocket re-audit.
2. Wing Rev.5: close the last GND island per variant (fanout
   respin of the connector neighbourhood or a rule-preserving
   repair), then re-run qualify + FEM extraction.
3. Junana cap measurement (PO-side) — fixes final shell heights
   (gate 6) in every configuration.
4. FH12 footprint verification against Hirose CL586-0533-0.
5. ZIF stock re-verification at order time (JLCPCB overseas).
6. PO order GO.

---

# Follow-up round (2026-11-17) — PO option (a) executed

PO decision (2026-11-17): option (a) — extend the Main outline
with tabs under both ZIFs; spec poses, the #264 fold plan and the
case entry slots unchanged. Tab design: computed from the built
pad bounding boxes + footprint courtyard, then enlarged to the
footprint SILKSREEN rectangle after DRC showed silk_edge_clearance
x2 (Rev.7's final DRC was clean, so silk had to be clean too).
Final tab depths past the Rev.7 slanted edges: **J2 4.738 mm,
J3 4.721 mm** (silk-governed: silk corner excursions 4.59/4.57
+ 0.15 allowance); worst pad-corner board-edge clearance
**0.7241 mm**; silk t-ranges inside the tab t-ranges; outline =
14 segments, verified closed chain with both tabs present.

## F0 — Main Rev.8 routed: CLOSED (with documented residuals)

| Gate | Result |
|---|---|
| Unconnected (audit physical analysis) | **0** |
| Native DRC errors | **0** |
| ERC (kicad-cli sch erc, labels swapped) | **0 violations** |
| Via-pad audit min | **0.1596 mm** (floor 0.10) |
| Wrong-net contacts | 0 |
| DRC warnings remaining | 60 lib_footprint_issues (inherited library notices) + 2 silk_over_copper (inherited) + **5 track_dangling** (below) |
| Copper-diff vs Rev.7 | NOT local: 1,467 of 1,406 Rev.8 tracks differ from the Rev.7 set (full re-route; changed bbox 56.2 x 40.8 mm). Disclosed, as in round 1. |

Closure path (routing is stochastic per roll; re-rolling is the
project's established closure method): 6 standard rolls all
stopped at unconnected 4 (last-mile ZIF escapes: J3.7 GND pour
tap, J2.10 MUX_A1, J3.4 MUX_OUT_B, J3.8 MUX_EN1); 5 escalation
('board') rolls all stopped at unconnected 2 (J3.10 MUX_A1,
J3.8 MUX_EN1, all-layer physical analysis); 4 KRT completion
passes on the best roll converged 2 -> 1 (J3.8 alone, invariant
across every roll and pass — its escape is fenced by the
GND/MUX_A1 fanout knot SW of the J3 pad row); a local rip-up of
7 knot segments (4 GND fanout + 3 MUX_A1, GND pads stay
plane-connected, MUX_A1 kept its via + pad stub) + one further
completion pass closed the board. One 0.1348 mm MUX_A0 sliver
left dangling by the F3 land correction was deleted afterwards.

The 5 remaining dangling WARNINGS (no errors): GND 4.0 mm
trunk end (119.2, 112.3); GND 5.4 mm (103.4, 103.9); GND
4.67 mm (100.5, 109.3); MUX_EN1 B.Cu 2.6 mm stub remnant
(96.5, 118.3) (the branch itself is connected via its
(97.2, 118.3) junction); GND 0.05 mm mid-chain dot
(125.0, 112.9) inside the live J3.11 feed chain. The tree's
cleanup.py was tried and REJECTED for this board: its prune
mis-trimmed the GND trunk and produced 448 clearance errors on
its working copy; the audited board was restored untouched and
the trims above were done by hand with junction checks.

### Resistance extraction (Rev.8-native, as-routed board)

Method identical to the Rev.7 qualification (centreline positive
model + GND sheet FEM from issue-240 scripts, terminals adapted:
branch loads at J2.14/J3.14 = HALL_5V per the reversal
assignment). Corner: 125 C, actual widths -20%, assumed 35 um
sheet / 20 um barrel. Extraction ran on the final routed board
before the F3 land correction; the correction touches only pad
end margins (no track/via/zone geometry), effect <0.1%.

| Quantity | Rev.8 | Rev.7 class | Target |
|---|---|---|---|
| Input loop (pos 4.79 + GND 32.21 mOhm) | **37.0 mOhm** | 49.09 | <=50 PASS |
| Rail common loop (pos 65.12 + GND 10.50) | **75.6 mOhm** | 49.49 | <=50 **MISS** |
| Branch loop J2 (pos 105.48 + GND 8.70) | **114.2 mOhm** | 20.96 | <=50 class **MISS** |
| Branch loop J3 (pos 235.49 + GND 5.36) | **240.9 mOhm** | 43.05 | <=50 class **MISS** |

Cause: the HALL_5V feeds to the ZIFs run long 0.10 mm-class
escapes (26.8 mm of 0.10 mm HALL_5V track on the board vs
39.8 mm at 0.5 mm); J3's path is the longest. The <=50 mOhm
values are model targets from the Rev.7 design, not operating
limits — the operating criterion is Vfar:

**Vfar (Rev.8-native) = 4.754 V (J3, worst) / 4.770 V (J2)** at
127 mA/Wing, design corner (rail 5.2 V -2%, -0.05 V dynamic,
common switch 0.25 Ohm, #141 Wing drop, #264 FFC cable term
0.2409 Ohm loop incl. 50 mOhm/contact model). Target >=4.60 V:
**PASS**, margin 154 mV. (Formula verified by reproducing
#264's published 4.786 V from the Rev.7 inputs exactly.)

## F1 — Wing Rev.5 island closure: 1 of 4 closed, 3 evidenced blockers

The predecessor's "one GND island per variant" was a
simplification; the DRC-authoritative items differ per variant.
Local repair only (no placement moves, no rule relaxation);
methods: shaped 0.30 mm pour bridges (validated at 0.10 mm
clearance) and plane-repair A* (0.11 mm-clearance obstacle
model, via transitions allowed) at 0.05 mm full-board and
0.025 mm windowed grids.

| Variant | Item | Outcome |
|---|---|---|
| 17mm-left | HALL_5V island {U_MUX_B.13}, F.Cu point-touch neck at (128.131, 39.32) pinched by MUX_A1 (y=39.1) | **CLOSED** by plane-repair A* at 0.025 mm window grid (path found, components 2->1). DRC required_unconnected 0, wrong-net 0, via-pad min 0.125198 (unchanged). Pre-existing warnings unchanged (3 dangling + 2 silk). |
| 16mm-left | J_WING.13 **MUX_OUT_C** pad (115.252, 30.621, B.Cu); nearest same-net copper 6.888 mm (whole pad->via leg missing — not an island stitch) | **BLOCKED.** KRT escalation rolls + plane-repair A* NO PATH at both grids. The pad's B.Cu escape is fenced by the neighbouring fanout combs and the diagonal trunk tracks; a via escape is blocked by the 0.5 mm-pitch pad field (via obstacle model). Needs a fanout/placement change — outside local repair. |
| 16mm-right | GND island {J_WING.8}, 0.532 mm2, gap 0.401 mm pinched by the MUX_A2 diagonal (81.2,26.6)->(83.3,28.7)->J_WING.6 | **BLOCKED.** Straight bridge intersects MUX_A2 (clearance 0.000); plane-repair NO PATH at both grids incl. via transitions (its via model needs 0.435 mm from any pad — the island's only via sites are inside the connector fanout field). |
| 17mm-right | GND island {J_WING.4}, 0.654 mm2, gap 0.401 mm pinched by the MUX_A0 fanout (via (81.3,26.9) -> (81.6,27.4) -> (81.6,28.1) -> J_WING.3) | **BLOCKED.** Same evidence class as 16R: bridge crosses MUX_A0; plane-repair NO PATH at both grids. |

Via-pad minima after the round (floor 0.10, none worse):
16L 0.1013 / 16R 0.1072 / 17L 0.1252 / 17R 0.1301 mm.
Residual possibility, stated honestly: the A* via model
(0.435 mm pad buffer, 0.11 mm clearance) is slightly more
conservative than the 0.10 mm yardstick; a hand-placed via at
exactly-0.10 rules in the 16R/17R islands is not disproven,
only unproven by two independent searches. Closing any of the
three blockers most likely requires re-spinning the connector
fanout neighbourhood (a placement change) — PMO/PO decision.

## F2 — Case re-audit with the extended Main: tray relief OK; WING SEAM CONFLICT

Method: #261 audit body set (fitlibF.bodies_at(17, -2.65));
board->case transform from the H1/H2/H3 washer anchors —
residuals 0.000 mm (pure translation (-100, -70)); extended
board solid vs every non-board-attached body, compared against
the Rev.7 board solid as baseline.

- **Tray pockets:** the ONLY grown tray intersections are the
  tab corners: **+3.94 mm3 (tray-left; case X -28.96..-26.44,
  Y 46.57..49.92, Z 4.70..5.90)** and **+3.61 mm3 (tray-right;
  X 26.44..28.82, Y 46.57..49.68)**. Case delta = a local pocket
  relief of exactly those volumes; it cuts into existing tray
  material only, so the **D-037 silhouette is NOT exceeded**.
  (Baseline note: the Rev.7 board solid already intersects the
  tray solids by 95.3/78.9 mm3 in this study body set — the
  set's board/tray models overlap by design at the support
  ledges; only the GROWTH is attributable to the tabs.)
- **Wing/Main seam — FAIL:** the tabs overlap the Wing boards'
  inner corners. Checked twice: against the study Wing solids
  (+54.8/+53.8 mm3) and against the **true Wing Rev.5 outlines**
  placed at the fitted poses (J_WING anchor at the verified
  envelope centres, rotation fit -30.5/+30.5 deg, section
  symdiff 2.9% of outline area): **plan overlap 46.7 mm2
  (right) / 47.5 mm2 (left), bite up to 1.95 mm** into the Wing
  outline. Seam gap Rev.7 edge <-> Wing outline = **1.516 mm**;
  the FH12 pad corners reach ~4.0 mm past the Rev.7 edge, so
  even a zero-clearance minimal tab bites ~1.3 mm — **tab
  shrinking cannot fix this**. Root cause: the #261 audit
  verified the ZIF envelopes (Z 5.9-7.9, above the board band)
  against case bodies but never board-outline vs board-outline
  at the seam; the #261 Main ZIF poses are inconsistent with
  the Wing outlines at board level. This is the same class of
  miss as round 1's pads-off-board finding, one level up.
- Fitted audit inheritance: the #264 fitted audit (gate 1 = 0,
  service PASS with the named drape residual) audited cables vs
  bodies; board solids there are the study set, so its result
  is unchanged by this round. It does NOT cover the seam
  conflict above (board-vs-board was never in its body pairs).

Options (PMO/PO decision; worker recommendation first):
(i) **Notch the Wing inner corners** in the tab zones (Wing
Rev.5 respin scope grows; the Wing outline is the fitted-seam
counterpart and its corner carries no keys — the overlap zone
is the corner margin; needs a Wing re-audit + re-route of the
affected corner nets, and 3 Wing variants still have their F1
blockers in the same neighbourhood, so one respin could close
both). (ii) Move the Main ZIFs inboard (round-1 option (b);
breaks the #264 fold-plan landing — fold plan rework).
(iii) Rotate the ZIFs along the slanted edges (round-1 option
(c); fold-plan rework). (iv) Accept a reduced tab (pads-only,
no silk margin) AND notch the Wing corners by the remaining
~1.3 mm — a smaller Wing change than (i) but the Main silk
then overhangs the board edge in the tab zone (silk_edge DRC
waiver needed).

## F3 — FH12 footprint verification: CORRECTED (one deviation)

Official source: Hirose FH12 series catalog (hirose.com,
Nov.1.2), the document the footprint itself cites, drawing
CL586-0533-0. Confirmed matching pads.json: CL No. 586-0533-0;
A=6.5, B=10.1, C=11.1, D=7.57 mm; land width 0.3 +/- 0.03;
pitch 0.5 +/- 0.05; metal mask 0.25 +/- 0.03, t=0.15; height
2.0 mm; FFC acceptance 0.30 +/- 0.05; 0.5 A/contact; 20 cycles.

**Deviation found and corrected:** signal land LENGTH —
catalog recommended land pattern = **1.3 +/- 0.1 mm**; the
footprint used **1.50** (that figure is the catalog's FFC-side
contact-exposure dimension, misapplied as the land length).
Correction: centre-anchored size-only change 1.50 -> 1.30 in
the .kicad_mod source and in every embedded J2/J3/J_WING
footprint (28 pads per Main file, 14 per Wing file; pad centres
unmoved). Post-correction audits: Main unconnected 0 / DRC
errors 0 / via-pad 0.1596 (one 0.1348 mm MUX_A0 sliver left
dangling by the shrink was deleted); Wing audits unchanged
(17L still 0; via-pad minima not worse). The audit flag
"unexplained_transfer_changes: 1" on the Wing variants is this
correction — explained here. (Process note: this correction
was recorded as applied in an earlier checkpoint of this round
before it had actually been executed; the discrepancy was
caught by re-reading the .kicad_mod during package review and
the correction was then applied and re-audited as above.)

**Still flagged (narrowed):** the MP fitting-land geometry —
the catalog text does not resolve it beyond the D=7.57 centre
span; the footprint's MP placement (+/-4.70, y=+1.20,
0.9 x 1.3) remains a reconstruction. Also recorded:
pads.json housing_depth 6.4 vs the catalog cross-section total
depth 5.6 for bottom contact (6.2 is the top-contact figure);
this touches only the #261 audit envelope lineage, not the
footprint.

## F4 — Packages regenerated

make-packages.py re-run on the final boards (Main from
inspection/final, Wings from their main.kicad_pcb); all five
FABRICATION.md status blocks rewritten to the states above.
Status remains **DRAFT, NOT FOR ORDER** (see the remaining
list).

## Draft decision text (for PMO to record; decisions.md untouched)

D-043 (draft, supersedes the round-1 draft): Main Rev.8 with
option-(a) tabs is routed and closed (unconnected 0, DRC errors
0, ERC 0, via-pad 0.1596 mm); extraction on the as-routed board
gives input loop 37.0 mOhm, common loop 75.6 mOhm (target
<=50 MISS), branch loops 114.2/240.9 mOhm (Rev.7-class MISS),
Vfar 4.754 V (PASS vs 4.60). The option-(a) tabs CONFLICT with
the Wing Rev.5 inner corners (bite <=1.95 mm; seam gap
1.516 mm) — disposition required before the board set is
fit-released: (i) Wing corner notch respin (worker-recommended;
can also close the F1 fanout blockers), (ii)/(iii) Main ZIF
re-pose with fold-plan rework, or (iv) reduced tab + smaller
notch + silk waiver. Wing Rev.5: 17L closed; 16L/16R/17R each
retain one evidenced local-repair blocker in the connector
fanout neighbourhood. FH12 land length corrected to the
official 1.3 mm pattern; MP geometry flag remains.

## Remaining before an order (final, follow-up round)

1. **PO disposition of the Wing/Main seam conflict** (F2
   options (i)-(iv)); if (i)/(iv): Wing respin + re-audit, and
   the tray pocket relief (3.94/3.61 mm3) added to the case
   tree (inside the D-037 silhouette).
2. Wing Rev.5 blockers (16L MUX_OUT_C leg; 16R/17R GND
   islands) — expected to be addressed by the same fanout
   respin as item 1 if option (i)/(iv) is chosen; otherwise
   they remain open blockers for those variants.
3. Junana cap measurement (PO-side, parts on hand unconfirmed)
   — fixes final shell heights (gate 6 OPEN in every study;
   keytop 22.00 provisional).
4. FH12 MP fitting-land geometry flag (narrowed, F3) — obtain
   the full manufacturer drawing or accept the reconstruction
   at order release.
5. ZIF stock re-verification at order time (JLCPCB overseas
   stock of FH12-14S-0.5SH(55) was not confirmed in this round;
   DigiKey/UniKeyic stock was >=10x in round 1).
6. PO order GO. (Also open, non-order-blocking: measurement B
   for the Fly DB upstream resistance, before assembly.)
