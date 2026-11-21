# Pilot B report — Issue #294 semantic review, wireless set (run with Issue #296 Stage B, 2026-11-21)

Procedure: `docs/review-procedure.md`. Scope: board-vs-case audit of
the wireless set at the files of record — here, the coordinate layer:
exact case-frame positions of the wireless Main's case-interface
points (JBATT / DLED / SW1), extracted from the board file of record
and validated against recorded kernel anchors, plus the findings
that fall out of those positions. Numbers are from the board file
(`.issue296-runtime/pilotb-coords.json`, extractor
`extract_main.py`) or the named study artifacts; nothing is estimated.

Input identity: wireless Main `wmain.kicad_pcb` on origin/main,
SHA-256 `75db72bc993a2e98a08b10df9c01e6d7a91fc4f9251ef173187ec200396b0d21`
(D-063). Transform board→asm: X = bx − 100, Y = by − 66.602.
Validation anchors (positive controls, procedure §1.4 analogue):
JBATT computes to asm (+24.0, +67.898) vs the centre study's recorded
(+24.0, +67.9) ✓; Main south edge computes to Y 67.900 vs the
south-notch record ✓; the 17R Wing fit in the same frame reproduces
its recorded outline bbox exactly (Stage B note, item 1) ✓.

## 1. NEW findings

- **R-294-46 (PC-4): SW1 is on Main's south edge, not in the centre
  bay.** Measured asm (−15.5, +67.898) (board (84.5, 134.5), pads
  BTN/GND). The Stage 1 case note's premise ("SW1's land is on the
  wireless Main (centre bay)") is wrong; its spine-plunger proposal
  survives only relocated to the shell south slope above this point.
  The footprint is a generic `TACT` placeholder and the part is
  DNP/hand-fit in the adopted configuration — case access cannot be
  finalised until a fitted part is settled (Main respin item).
  Classification: **true problem** (premise error in a consumed
  record + an open board item). Basis: board file (this run);
  D-058/D-063 configuration (SW1 DNP disposition, #292 order-prep
  record).

## 2. SAME-CLASS groupings

- R-294-46 groups with **PC-4 assembly-escape-shortfall** (seed:
  R-294-12, flipped-pose FFC service) — a case/service access point
  whose board-side premise did not hold. Handling then: recorded as
  a service procedure; here: proposal relocated + board item named.

## 3. SUPPRESSION breakdown

- accepted by D-xxx: 0
- in-progress under Issue: 0
- resolved-confirmed: 3 — the three coordinate records R-294-44
  (JBATT), R-294-45 (DLED) and the FFC-channel record R-294-47 are
  entered as resolved coordinate/fact records (they confirm recorded
  anchors or decision text; they are not problems). R-294-47's
  underlying question (which FFC serves the 11.5 mm channel) stays
  open as the named follow-up FFC-1 in the Stage B note — the ledger
  entry records the measured channel/span facts only.
- duplicates-merged: 0
- Reconciliation: raw observations 4 = new 1 + suppressed
  (resolved-confirmed) 3 + duplicates-merged 0 ✓

## 4. Needs-PO-judgment items

- None raised by Pilot B itself. (The SW1 fitted-part question is a
  board-respin scope item for the PO's next Main gate, stated in
  R-294-46; the Stage B package's own approval is the PO gate for
  this run.)
