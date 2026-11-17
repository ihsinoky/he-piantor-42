# Issue #270 Stage 2c plan — connector-aligned tab (2D study only)

PO request 2026-11-18: tab front edge should be parallel to the FH12 connector's
own edge (connector long axis), instead of parallel to the board slanted edge.
PO clarification: figures = 外形図, clean 2D top-view outline line drawings.

## Steps
1. MEASURE from Rev.9 board files (issue-270-main-rev9/main-rev9):
   - J2/J3 FH12 footprint rotation (long axis / mouth line direction)
   - board slanted-edge angle at each site
   - current tab front angle (= slanted edge per 2a/2b)
   - angular difference connector vs tab front; pad-field extents vs connector
2. DESIGN candidate tab per site: front edge parallel to connector long axis,
   transitions back to slanted edge both sides with fillets. Outline only;
   connector + copper unchanged.
3. CHECK (2a/2b yardsticks):
   - pad-corner-to-outline clearance floor 0.70 (Rev.9 value 0.8364)
   - containment inside D-037 silhouette
   - Wing notch = exact 0.55 offset of candidate tab -> seam 0.550, overlap 0
     at 17mm and 16mm fitted poses (reuse stage1/2a harness)
   - Wing copper intersection of re-derived notch (expect none)
   - case tray relief delta vs Rev.9 relief
   - Main copper cuts (expect 0; min edge-to-copper clearance)
4. FIGURES (2D outline line drawings, no shading):
   - fig-2c-full-current.png / fig-2c-full-candidate.png: FULL Main outline,
     both tabs + both connectors, same scale
   - fig-2c-zoom-j2.png / fig-2c-zoom-j3.png: zoom per site, current vs
     candidate, connector outline + angle lines visible
   - fig-2c-overlay.png if cheap
   Save in .issue270-runtime/, copy to goal files/.
5. stage2c-design.md: measured angles, candidate spec per site, check table,
   honest costs, feasibility statement.
6. Checkpoint-commit study files. Do NOT push. No board edits.
