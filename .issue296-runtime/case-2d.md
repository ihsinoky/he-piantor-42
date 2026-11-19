# Issue #296 — Wireless case design, Stage 1: 2D approval package

Status: FOR PO 2D APPROVAL. No 3D modelling started (project gate).
Figures: `case296-2d-topview.png`, `case296-2d-sections.png`
(goal files/). Scripts: `.issue296-runtime/checks.py` (build123d kernel
checks), `.issue296-runtime/figures.py`. Frame for all figures: X centred
on the case, Y from the NEW north edge, +Y south; Z from the case bottom.

## Design inputs consumed (not re-derived)

- Current case: #263 production tree (plate top Z10.90, keytop datum
  Z22.00, outline 291 x 146.1, tray floor top Z1.60 ribbed datum).
  North slope cover group is a distinct part over the plate's north.
- D-060: AA x4 one row, axes E-W, field 202 x 14.5, open-top tray,
  bay 212 x 16.5, growth +17, thin power board 0.8 = tray floor,
  pack stack 15.3, no lid, slide switch at the tray end.
- D-053: trackpad island Ø44 on shell-central, centre asm (0,48),
  surface Z12.70, zero height raise; Main keeps Ø40 keep-out.
- South straightening (case-south-notch study): centre-south edge to
  the peak line; Main south edge -> case edge 13.802mm; antenna home =
  south PETG band, no metal/shielding features in the band.
- Board ghosts from kernel data: `issue-261-lowdeck-full/preview.step`
  solids (Wing slabs X ±(1.0..142.24), Y(asm) -61.6..77.38; Main slab
  X ±37.89, Y(asm) 2.27..67.90 — south edge 67.900 matches the
  south-notch record exactly).

## Kernel-verified checks (checks.py, build123d)

- **C1 — tray width vs cell diameter: D-060's field is MARGINLESS.**
  At the recorded field width 14.5 against the BK-3MCD max diameter
  14.5, interference = 0.0000 mm3 with **0.00mm clearance per side** —
  any cell at max diameter plus any print tolerance jams. Proposed
  correction (drawn in the figures): channel inner width **15.6**
  (0.55mm/side, kernel interference 0.0000), so the bay becomes
  **212 x 17.6** and growth **+18** (outline 291 x 164.1). This is a
  deviation from D-060's +17/16.5 figures, proposed at this gate.
- **C2 — length chain exact:** 4 x 50.5 + interfaces 6.0 (0.75 outer,
  1.5 per middle back-to-back pair) + walls 4.0 = **212.0** = D-060 bay
  X. Flag: spring travel 0.75/interface vs cell length tolerance
  (±0.5 class) leaves 0.25mm worst-stack margin — leaf-spring working
  range must be specified ≥1.0mm at power-board design.
- **C3 — height stack (solids):** floor top 1.60 + board 0.8 + cell
  Ø14.5 → **cell top Z16.90, 5.10 below the 22.00 datum**. With the
  band rim proposed at Z13.6, cells protrude **3.3mm above the rim** —
  exposed by design (D-060 open-top), seated in a 15.6-wide channel.
- **C4 — cable route:** tray east-end exit -> diagonal inside route ->
  JBATT (Main south edge, board-frame (124, 134.5), case-frame approx
  X +24): polyline **161mm, ~171mm with slack**. D-060's "~150mm" was
  estimated for the centred +54 block tray; the row tray's end exit
  runs ~14% longer. Cable is cut to length; corrected figure recorded
  here. JBATT's exact case-frame position is a Pilot B (Issue #294)
  kernel-audit item.
- **C5 — antenna band:** Main south edge -> straightened edge 13.802;
  less the 2.0 wall → **~11.8mm clear PETG zone**. Case-side rule
  carried from the board's edge-fix: no screws, inserts, shielding or
  other metal features inside this band.
- **C6 — tray span / band ends:** bay 212 of 291 leaves **39.5mm of
  band at each end**. The extension band is new material north of the
  existing north wall; structure proposal: the band is a full-width
  shallow channel (floor continuous with the tray floor at the 1.60
  datum, rim Z13.6) tied into the existing north wall along the full
  291 width — the tray opening interrupts only the band's own rim,
  not the existing wall, so the 212 span does not rely on the rim for
  stiffness; the floor + the two end cheeks (39.5 each) carry it.

## Case-side proposals (for this gate)

- **Slide switch:** on the tray's east end wall, top-accessible,
  in series with the battery cable (power-study S1). Drawn in the
  top view. Zero board change.
- **Pairing button access:** SW1's land is on the wireless Main
  (centre bay, currently DNP/unplaced). Proposal: a Ø3 plunger hole
  in shell-central's spine at SW1's placed position, pressed with a
  fingertip-sized recess — position fixed at the 3D stage from board
  data. **Board implication flagged:** SW1 must become a placed,
  fitted part (or a defined test-pad + case switch) at the next Main
  respin; the case cannot invent access to an unfitted land.
- **LED visibility:** DLED (0603, Main north edge, board-frame
  (95, 83)) sits under shell-central — bench-grade visibility is NOT
  sufficient for the PO-requested power/battery indication. Proposal:
  a Ø2 light-pipe from DLED to the spine surface beside the trackpad
  island (visible while typing), exact take-off point at the 3D stage
  from board data. The shared-LED on-demand scheme itself is
  unchanged (zero board delta for 1-colour).
- **Trackpad island join:** the Ø44 flattened island is a local
  re-profiling of shell-central (surface spread across the Ø40 disc
  measured 10.9..14.27 in the #290 study; island flat at Z12.70) — no
  separate part, no join line; the island rim blends into the spine
  slopes. In plan the island's south rim extends ~2.1mm past the Main
  board's south edge — Z-separated from the antenna band (shell above,
  band at case-bottom level), no conflict.
- **Receiver storage (consideration only, NOT designed in):** the
  39.5mm band ends could physically hold a Unifying-class receiver
  (~15 x 9 x 6mm) in a shallow slot. Noted per the issue input; no
  geometry proposed at this gate.

## Open items

1. C1 correction (+18 / bay 17.6) — PO approval at this gate; D-060
   amendment if approved.
2. JBATT and DLED/SW1 exact case-frame positions — Pilot B kernel
   audit (Issue #294) alongside the 3D stage.
3. SW1 fitted-part decision (board respin item, see above).
4. LED light-pipe vs window — choice at this gate or deferred to 3D.
5. Junana keycap physical measurement still open — shell heights
   remain at the provisional 22.00 datum (inherited gate).
6. Power-board design (contacts ≥1.0mm spring range per C2, return
   pour, PTC, switch land) — separate work item feeding the 3D stage.
7. Outline depth bookkeeping: arrangement study used a 145.6 base
   (291 x 162.6 for +17); production record is 146.1 — figures use
   146.1. Reconcile in the 3D stage's outline construction.
