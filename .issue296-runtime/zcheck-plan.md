# Z-check plan (Issue #296, Wing tab vs bay/power board)

Question from PMO: Wing inner north tabs overlap the power-board
rectangle in plan (X≈22.50 edge inside the 52.5×58 rect over
Y −45.0..−8.7, ≈123 mm²/side; cells cleared by 0.251 mm). Stage B
recorded no Z relationship. Establish it from geometry/files only.

Steps:
1. Wing side: 17R board file @3fcad246f (review worktree checkout) —
   footprints on the B side inside the tab region (asm X 22.50..26.25,
   Y −45.0..−8.7 → board coords via the recorded pose fit); board
   thickness from the file; seated underside Z from geometry17 body
   data (geom_v2.json / gyaku wing scripts).
2. Power-board side: top Z = floor −0.65 + 0.8 = +0.15; what stands on
   the E/W edge strips per #303 Stage 1 note (contacts N/S only, east
   edge = return pour, F1/J1/J2 south) + heights.
3. Bay wall in the overlap Y range: from geometry17 tray bodies +
   Stage B bay definition (cavity 56.5 wide) — wall presence + top Z.
4. Assembly order from the heights + insertion path.
5. Verdict + trim geometry if needed. Flag any clearance < 1.0 mm.
