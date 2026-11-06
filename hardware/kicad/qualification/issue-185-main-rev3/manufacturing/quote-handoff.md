# Main Rev.3 review / quotation package — Issue #185

Use only this directory's fabrication ZIP, BOM.csv, CPL.csv and paste/ with the
qualified board at ../inspection/final/main.kicad_pcb. Do not mix Rev.2 Gerbers
with this package. This is not manufacturing GO.

- 48 × 52 mm, four layers, 1.2 mm; minimum signal width/clearance 0.10 mm;
  113 vias with diameter/drill 0.60/0.30 mm. Retain assumed stackup/material
  inputs for engineering review; obtain actual guaranteed copper/plating data.
- Remove the epoxy-filled / copper-capped POFV option for this Rev.3 proposal.
  All 113 vias pass ≥0.10 mm annulus-to-pad clearance, with zero pad or paste
  overlap. Solder mask Gerbers retain component-land openings and tented vias.
  Confirm tenting, mask registration, tolerances and actual process in DFM review.
- Five boards; Economic PCBA; 58 assembled components per board, four bare
  testpads excluded from BOM/CPL. J1's 12 SMD contacts and four PTH shell legs
  remain in the same Economic PCBA process. No transfer to Standard PCBA.
- CPL origin: absolute KiCad (76,122) mm, X'=X−76, Y'=122−Y, top side,
  KiCad angles. All 58 positions were checked against the qualified board.
- BOM retains PR #176's repository MPNs: C26–C28 TDK C3225X7R1C226K250AC,
  R17 TNPW060354K9BEEA. The substitute parts discussed in PR #176's quotation
  comments are not adopted here. Procurement and acceptance need confirmation.
- Requote this package before claiming savings. PR #176's older POFV price and
  saved quote are not the price of Rev.3. Via plating charges may have a
  different basis; no fee reduction is inferred from removing POFV.
- Paste is faithfully exported, with no stencil optimization. Confirm stencil,
  testpad paste, shell soldering and assembly process with the manufacturer.

No manufacturer upload, communication, cart addition, order or payment occurred
in Issue #185. PO review / merge and manufacturer review remain outstanding.
