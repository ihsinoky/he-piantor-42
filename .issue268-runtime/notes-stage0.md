# Issue #268 — stage 0 notes (baseline + design decisions)

## Rev.3 baseline (measured from board/m1-matrix18.kicad_pcb)
- 2 layers, outline bbox x 35.975..164.025, y 59.975..140.025 (128.05 x 80.05 mm), 65 footprints.
- Rules: min track 0.10, min clearance 0.10, min via dia 0.60.
- J_WING = JST BM14B-GHS-TBT top-entry GH (BOM C265384), F.Cu at (100,133) rot 0.
  Pads along X at y=133, pin1 x=108.125 -> pin14 x=91.875 (pitch 1.25). MP pads (90.025/109.975, 136.35), no net.
- Pad->net = D-024 canonical: 1 HALL_5V, 2 GND, 3 MUX_A0, 4 GND, 5 MUX_A1, 6 MUX_A2,
  7 WING_EN, 8 GND, 9 MUX_OUT_A, 10 GND, 11 MUX_OUT_B, 12 GND, 13 MUX_OUT_C, 14 GND.
- No native KiCad schematic exists for the Matrix (JITX-generated board; Rev.3 tree has none)
  -> ERC gap is inherited; state it in REPORT.
- Local lib: Wing129 -> ../PCBA.pretty (connector.kicad_mod = the GH footprint).

## Wing Rev.5 arriving-order assignment (verified from built board wing-rev5-17mm-left/routed.kicad_pcb)
- J_WING = FH12 on B.Cu (layer 2); pad n -> D-024 signal n (identical table to Matrix Rev.3 above).
- Main Rev.8 J2/J3: F.Cu, pad n <- signal (15-n) (reversal absorbed at Main, D-043). J2 pad1=GND, pad14=HALL_5V.

## FH12 footprint (corrected, from issue-263-implementation/connector/)
- Signal pads 0.30 x 1.30 (land length corrected per CL586-0533-0), pitch 0.5,
  local frame: origin at pad-row centre, +X toward pin 14, mouth toward +Y,
  pads at local y=-1.00, MP pads 0.90x1.30 at (+/-4.70, +1.20), NC.
- Housing depth: catalog bottom-contact 5.6 (pads.json's 6.4 is pre-correction lineage; envelope only).

## Rev.4 design decisions
- FH12 mounted on B.Cu (same as Wing Rev.5), anchor at old GH site: footprint origin (100,133),
  mouth facing +Y (south edge at y=140.025; housing front reaches ~137.6, on-board).
- Pad-1 side: pad 1 at +X (east), pad row descending toward -X, matching the old GH layout AND
  the Wing mouth-frame chirality: u=(pad1->pad14)=(-1,0), m=(mouth)=(0,+1), f=-Z (B.Cu)
  -> (u x m).f = +1, same as Wing Rev.5 (measured u=(-0.866,0.5), m~(0.5,0.866), f=-Z -> +1).
  Main J2 (F.Cu) chirality will be computed in the verification script for the connection check.
- Pad nets: pad n <- D-024 signal n (unchanged from Rev.3). MP pads: no net (as Rev.3).
- Re-route connector neighbourhood only; disclose copper-diff extent by measurement.

## Manufacturing package (per PMO additional requirement, 2026-11-17)
- JLCPCB-ready, NOT KiCad-native: BOM.csv in project format (Comment,Designator,Footprint,LCSC Part #)
  with real LCSC codes carried from the Rev.3 BOM; only J_WING line changes:
  FH12-14S-0.5SH(55) with placeholder C-HIROSE-FH12-14S (do NOT invent a code).
- CPL-jlcpcb-gerber-frame.csv (Designator,Mid X,Mid Y,Layer,Rotation), gerber frame =
  KiCad frame via (X, -Y); Matrix offset vs KiCad-frame CPL = (+36.000000, -140.000000) (PR #220 method,
  Rev.3 NOTES). All rows except J_WING carry over; J_WING row recomputed (bottom layer, body centroid =
  housing centre, local +1.40 from pad-row origin, documented like the Rev.3 GH centroid note).
- Include CPL-jlcpcb-gerber-frame-NOTES.md + quote-handoff.md (Rev.6 exemplar) in the package.
- FABRICATION.md marked DRAFT / NOT FOR ORDER.

## Placement correction (stage 1 build)
- FootprintLoad + SetLayer(B_Cu) does NOT mirror geometry; the Wing boards' B.Cu footprints are
  truly flipped. Fix applied: Flip() about the anchor -> rot 180, IsFlipped=True.
- Final pose (measured): anchor (100,133) B.Cu; pad1 (103.25,132.0) east, pad14 (96.75,132.0);
  MP pads y=134.2 (mouth south, board edge 140.025; housing front ~137.2, on-board).
- Mouth-view handedness (script mouthview.py; viewer at mouth, up = toward board):
  Wing 17L LEFT, Wing 17R LEFT, Main J2 LEFT, Main J3 LEFT, Matrix Rev.4 LEFT -> congruent.
- Zone deletion (Z2 = x 85..115, y 129.5..140.03): 111 link-net items removed (ledger step1.json).

## Update (PMO, 2026-11-17): FH12 LCSC code CONFIRMED
- Hirose FH12-14S-0.5SH(55) = LCSC C5378715 (Extended, stock 3,907, ~$0.53/pc; auto-matched
  in the Main/Wing PCBA quotes). Use C5378715 in the Rev.4 BOM - no placeholder.

## Continuation assessment (second worker, 2026-11-17)
- Uncommitted board = build2.py output of run2.sh's last attempt: all 9 link nets have
  A* routes drawn (step2.json), but the script's own GND connectivity DIAG failed
  (goalTot 0/520) and it saved a "partial" board.
- CALL: KEEP the uncommitted board as working state (coherent, complete-looking routing;
  nothing corrupt). The custom DIAG is not authoritative - KiCad DRC/connectivity decides.
  If DRC shows GND truly unconnected, fix GND locally; else proceed to gates.

## Stage 3 (continuation worker): routing completion
- Previous worker's A* connected every J_WING pad to *a* surviving fragment, but the
  Z2 deletion had also severed U_MUX_C's HALL_5V/MUX_A2/WING_EN and split GND into
  east/west comps + 5 isolated pad stubs (its own DIAG failed on GND; run2.sh retried 6x).
- GND stubs were trapped by the signal-escape via wall (vias at y=130.75, 0.5mm from each
  GND lane; a 0.30 track needs 0.55 clearance, has 0.50). Fix: 0.15mm necks in-lane
  y131.00->129.90 (clearance 0.125 to flanking vias), then 0.30 A* bridges north of the wall.
  NOTE: pad-10 (98.75) neck initially met the y=130.20 bus only by a 0.025mm graze;
  bus extended to x=98.78 for a full-width joint (0.12 clearance to MUX_OUT_A jog).
- Bridges driven by capsule union-find (validated 1:1 vs kicad-cli DRC counts);
  build2's endpoint-only component model fragmented and wasted attempts on 0.0/0.1mm
  micro-bridges - duplicates cleaned (GND x7, HALL x8 stacks, A2 gap x7).
- Vestigial A2 via at (103.60,128.40) deleted: its two B.Cu tracks already joint there;
  F.Cu spur (failed route tail) deleted. A2 diagonal restored after finding it carried
  the east B.Cu chain (fixup2 error, reverted in fixup3).
- Dangling cleanup: EN spur trimmed onto its via (107.50,126.35); GND chain-B micro
  segments deleted; necks trimmed onto their crossing bus tracks.
- FINAL DRC (kicad-cli, severity-all): 0 errors, 0 unconnected, 1 warning:
  track_dangling on HALL_5V F.Cu 0.20mm at (112.6,127.2) - Rev.3-original bus tail;
  its Rev.3 continuation (108.1,131.7)->(112.6,127.2) was deleted in stage 1 by design
  (Z2). Tail is connected copper (east HALL bus). No other-net copper within 2.6mm on
  either layer to terminate it on; deleting the arm would remove ~15mm of original
  power copper feeding real pads. Disclosed in REPORT.
