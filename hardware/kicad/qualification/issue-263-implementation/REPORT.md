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
