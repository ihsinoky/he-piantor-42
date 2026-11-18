# Issue #275 Phase 2 — GH harness geometric check (flipped Main) — plan

PO direction (2026-11-18): Main is symmetrized + adopted (D-046, Rev.10).
Check GEOMETRICALLY whether a JST GH wire harness passes with Main flipped
(components down, Wing-link connectors on Main's underside, both connector
rows in the low tray plane, no rise to Main's top face). STUDY ONLY — no
board changes. If it passes, a GH conversion design follows (PO gate).

Configuration under test:
- Wing end: GH side-entry underside, as qualified in Wing Rev.4
  (JST SM14B-GHS-TB, #235 records).
- Main end: same GH side-entry family at the Rev.10 symmetric sites,
  underside (flipped pose).
- Harness: 14 wires/side, D-024 content, D-033 bound: AWG28+,
  insulation OD <= 1.0 mm, six GND returns separate, each wire <= 200 mm.
- Case: adopted low-deck production tree (plate top 10.90) incl. the
  D-046 flip pocket. 17 mm pitch primary, 16 mm check.
- Fly + its cable modelled in NORMAL pose (flipped-J4 is a Stage B named
  residual, out of scope; note interactions only).

## Verification extract — Q1 vertical budget at the Wing underside (measured first)

Numbers, each from two independent sources:

| Quantity | Value | Sources |
|---|---|---|
| Wing PCB underside Z (B) | **4.70** | (1) issue-263-lowdeck-production/README datum: "tray floor 1.60 ribbed, Wing PCB underside B=4.70, plate top 10.90" (4.70 + 6.20 = 10.90 ✓). (2) #248 frontier body set: Wing slab Z 7.35–8.55 at s=0; #261 audit applies s=−2.65 → 4.70–5.90 ✓ |
| Tray floor top Z | **1.60** | (1) production README datum above. (2) #261 REPORT bounds ladder lever: "tray floor 2.00 -> 1.60 ribbed" |
| Available gap under Wing PCB | **3.10** | 4.70 − 1.60 |
| GH mated plug envelope below PCB underside | **4.35** nominal; **4.85** reserved | #235 REPORT: JST catalog mated side-entry height 4.35 mm, axial length 7.15 mm, horizontal wire exit; project allowance +0.50 (assembled height/solder/placement) → 4.85 reserved. Old datum check: underside Z10, floor Z2 → nominal floor gap 3.65 ✓ matches #235 |
| Mated plug bottom Z (this case) | **0.35** nominal / **−0.25** reserved | 4.70 − 4.35 / 4.70 − 4.85 |

Cross-check via #261 bounds ladder: plate top = B + 6.20 (PCB 1.20 +
spacer 3.50 + plate 1.50, datasheet-fixed). GH row of the ladder: envelope
4.35 → plate-top equivalent 12.95 ⇒ B_min(GH, with allowance, 0.30 free
gap) = 1.60 + 4.85 + 0.30 = 6.75 → plate 12.95 ✓ consistent.
#248 Phase A B=7.35 decomposes as floor 2.00 + 4.85 + free gap 0.50 = 7.35
(pre-lever values) ✓ consistent.

**Q1 preliminary verdict: FAIL, hard.** Margin = 3.10 − 4.35 =
**−1.25 mm nominal** (−1.75 mm with the project's own 0.50 allowance).
Even with zero free gap and zero allowance the plug bottom (Z 0.35) sits
1.25 mm BELOW the tray floor top (Z 1.60): the mated plug intersects the
tray floor. The wire exit is horizontal (side-entry), so no additional
vertical demand below the plug — the plug body alone binds.
Per the brief: Q2's full wire audit at 10.90 is replaced by quantifying
this plug↔floor intersection + running the height-independent plan-view
fan check (Q3); the full audit runs at the Q4 passing height.

## Stages

- S0 (this file): plan + Q1 verification extract. COMMIT.
- S1 Q3: plan-view fan feasibility. Endpoint plan geometry: Wing GH
  mouths (Rev.4 pose, #235 placement records) and flipped-Main GH mouths
  at the Rev.10 symmetric sites (mainsym worktree records /
  issue-275-main-rev10 REPORT). Pin-order at each end as physically
  presented (D-032 discipline). Order-preserving test + approach-tail
  widths (OD 1.0 wires, #248 round-8/12 methods). State what changed vs
  #248 (no rise; coplanar endpoints) and what did not.
- S2 Q4: height search. Steps of ~0.5 mm plate height from 10.90 upward;
  at each step re-run only the binding checks: (a) Q1 arithmetic with
  allowance + 0.30 free gap; (b) at the first height passing (a), the
  FULL audit (S3 machinery) — if it fails, step up and repeat.
- S3 Full audit at the passing height: harness solids (14 swept OD-1.0
  wires/side + plug envelopes) vs all fixed bodies from the #261/#248
  frontier body set re-based to the test height (tray, Wing PCBs +
  underside reservations, plate, Main flipped + its underside
  reservations, Fly + cable normal pose, case joint screws).
  Repaired audit method (#248 round 10+): boolean Common volume PLUS an
  independent distance check (BRepExtrema) on every pair whose Common
  reads 0 but whose bounding boxes approach < 0.5 mm — no silent
  under-report. Gates: unexpected contacts 0; every wire <= 200 mm;
  service detach reserve measured and reported (old bound 30 mm,
  report-only).
- S4 Q5: one-page comparison note (flipped-GH at passing height vs
  adopted FPC at 10.90). Facts only.
- S5: gh-check.md + gh-check.json, final commit. Do NOT push.

## Invariants

- Measure before concluding; every claim carries a number and a source.
- Distrust the first pass: any "0 contacts" result gets the second-method
  check above before it is believed.
- GH pin content per D-024 is invariant; only geometry is under test.
