# Wing tab vs battery bay — Z-clearance check (Issue #296, 2026-11-21)

Question: in plan, the Wing boards' inner north tabs overlap the Stage B
power-board rectangle (52.5 × 58.0; board edge at asm X ±26.25) — Wing
inner edge at X ≈22.50 inside the rectangle over Y −45.0..−8.7
(≈123 mm²/side; cells cleared by 0.251 mm in plan). Stage B recorded no
vertical relationship. This note establishes it, plus (PO additions
2026-11-21) the cell-removal envelope and Wing shape-change options.

Frames/sources: asm frame as in Stage B (X centred, +Y south). Case Z
throughout. Geometry from the geometry17 body set
(`he-piantor-raise/.issue248-runtime/phaseb/geometry17`, case Z = g17
Z − 2.65) at the Stage B poses (trays/Wings shifted ±9.5). Board-file
facts from the wireless Wing 17R file at commit `3fcad246f` (review
worktree checkout); board→asm transform fitted from the outline pair:
rotation −29.9960°, residual max 0.0007 mm. Scripts: `zcheck1..10.py`
in this directory. East (right) side measured; the west side is the
mirror pose in the same body set with the same Z stack.

## The Z stack in the overlap (case Z, mm)

| Feature | Z | Source |
|---|---|---|
| Bay floor (levelled) | −0.65 | Stage B item 2 |
| Power board top (0.8 board) | **+0.15** | Stage B stack |
| Cell bottom / top | +0.15 / 14.65 | Stage B stack |
| J_WING mating envelope bottom (g17 model, a solid block) | −0.15 | g17 body `underside-right-J_WING` |
| FH12 connector physical bottom (see §1) | ≈2.70 | board file + FH12 height 2.0 |
| U_MUX underside body bottom (g17 model) | 3.30 | g17 body `underside-right-U_MUX_C` |
| Wing board underside / top | **4.70 / 5.90** | g17 body `wing_right` @δ9.5 (board thickness field in the 17R file is also 1.2 — consistent) |
| Switch plate underside / top | 9.40 / 10.90 | g17 `plate-right` in the overlap column |

## 1. Wing side

- Board underside at the tab: **Z 4.70**, uniform (bare board in the
  column except as below). Board material in the overlap column:
  Y −45.00..−16.81 (the tab) plus a sliver at Y −9.19..−8.70.
- Underside features inside/near the column (g17 bodies @δ9.5):
  - **U_MUX body** (TMUX1208; the g17 body name is `U_MUX_C`, at the
    position the wireless file calls **U_MUX_B**, centre asm
    (28.0, −24.0)): body X 24.95..30.05, Y −27.30..−20.70, bottom
    **3.30**. It overhangs the power-board rectangle (edge 26.25) by
    1.30 mm in plan. Physical package (TMUX1208PWR, height ≤1.2) gives
    a bottom of ≈3.50; the 3.30 is the case-study body (with
    allowance). Either way it clears the power-board top by ≥3.15.
  - **J_WING envelope body**: X 25.62..47.38, Y −43.10..−34.95,
    Z −0.15..4.70, volume = its full bbox (a solid keep-out block, not
    the connector shape). Only its west 0.63 mm crosses the
    power-board edge (26.25). The physical connector (FH12-14S, board
    file: centre asm (27.00, −38.91), B side) bottoms at
    4.70 − 2.00 = **2.70** → clears the power-board top by **2.55**.
    The envelope's −0.15 bottom is the study's mating/FFC allowance,
    2.85 below the physical connector bottom.
  - Test pads **TP_W_GND / TP_W_H3V3** (17R file, B side, flush pads)
    at asm (23.00, −33.01) / (24.70, −33.01) — inside the rectangle in
    plan, at board underside 4.70 → 4.55 clear.
- 17R board-file census of the overlap quad (pads inside): J_WING
  5/16 pads, U_MUX_B 8/16 pads, TP_W_GND, TP_W_H3V3; **13 vias**;
  **≈95 track segments across 17 nets** (HALL_3V3 23, MUX_A1 10,
  WING_EN 10, H_C0_RAW 8, MUX_A2 7, H_B2_RAW 7, …). The tab is the
  connector + MUX_B + their fanout field — it is **not** empty board.
  J_WING sits at the tab's west end; its fanout runs through the
  whole tab latitude. The only measured empty Wing region nearby is
  the **south inner corner** (asm X 14..24, Y −8..−2): no pads, no
  tracks (§6).

## 2. Power-board side

Top of the bare board **+0.15**. What stands on the E/W edge strips
(the strips under the Wing tabs), per the #303 Stage 1 design note:
- **East strip: the PACK_POS_RAW return pour only** — plain copper on
  the board surface, no parts, nothing above +0.15.
- **West strip: nothing** (pack − exits at the south-west corner).
- All contacts are at the N/S ends (contact faces ±26.00 from cell
  centres); F1 (PTC, 1206, ≈1.0 high), J1 (GH, 2.9 class), J2 pads and
  TP1/TP2 are all on the **south** side, outside the overlap Y range's
  strips. So under the tabs, the power board presents a bare surface
  at +0.15 everywhere.

## 3. Bay wall

- At the Stage B wall line (X 28.25..30.25, wall 2.0 in plan) the
  current tray contains **only the floor slab** (top −0.65) across the
  whole overlap Y range — there is **no raised wall** there today,
  and Stage B defines the bay wall in plan only (its height is a 3D
  item). Nothing stands between the Wing tab and the power board
  except the features in §1/§2.
- **Exception — a tray post inside the power-board rectangle:**
  existing tray material at X 22.73..26.25, Y −12.23..−8.70 rises from
  the floor to **Z 9.40** (plate-support height). It is inside the
  power-board outline and crosses the board's Z band (−0.65..+0.15):
  **the power board cannot seat while this post stands.** It sits at
  the block's south-east corner zone; Stage B's levelling list covers
  the block footprint (X ±24.25) but this post extends east of it
  (to 26.25). Disposition must be explicit in the bay re-form:
  remove/relocate the post (recommended — it is a plate-support
  feature, and the plate support scheme is being re-formed anyway),
  or notch the power board's east edge 3.52 × 3.53 — which would cut
  the return pour. Flagged as a Stage-2/3D input below.

## 4. Assembly order

**The power board must be placed BEFORE the Wing boards are seated.**
- Level insertion past seated Wings is impossible: at the Wing plane
  the free gap between the tab inner edges is 45.0 mm < board width
  52.5; the MUX bodies overhang both board edge strips (to X ±24.95,
  bottoms 3.30) while the board's lateral play in the cavity is only
  ±2.0 — it cannot clear both sides at once (would need width <49.9).
- Tilted insertion is impossible: passing the Wing plane needs
  ≥≈31° of tilt (projected width ≤45.0), i.e. a corner drop of
  ≈27 mm, but the bay depth below the Wing underside is only
  4.70 − (−0.65) = 5.35 mm.
- Required order: **power board → cells/contacts → Wing boards →
  plate** (the standing boards-then-plate order is preserved; the
  power board simply joins the "boards" step, first). Service order
  reverses: a Wing must be unseated before the power board can come
  out. The battery CELLS are unaffected — they insert/remove from
  above with the cover removed (§5).

## 5. Cell-removal envelope (PO addition)

Envelope used (stated explicitly): per cell — (i) axial slide
**2.0 mm toward the leaf-spring end** (Stage 1 allowance set:
0.75 mm/end contact allowance + button release), (ii) tip the freed
(button) end up, rotating about the spring-end **end-face contact
point**, to **35°**, (iii) lift out. Plus finger access: **10 mm-wide
zones on the outer (E/W) side of each outer cell, from the cell's
horizontal centreline (Z 7.40) up to the cover underside (16.65)**
— the standard pinch grip on the upper half of the cylinder. The
cover is treated as removed (it is a removable cover, D-062). The
middle cell has no side access (0.5 mm gaps); it is removed after an
outer cell, using the freed side — same envelope, translated.

Measured (east cell, the binding side; west mirrors):
- Cell swept volume vs Wing tab set (board + MUX body + J_WING
  envelope): **0.000 mm³**. The sweep never leaves X ≤ 22.25 (tipping
  is in the Y-Z plane); the plan gap to the tab edge stays 0.251.
- Finger zones vs tab set: **0.000 mm³**. The zones overlap the tab
  in plan (X 22.50..32.25) but are vertically clear: zone floor 7.40
  vs tab top 5.90 → **1.50 mm** — the tightest point of the envelope
  check, above the 1.0 flag line.
- Sensitivity 1 — pivot model: if the tip is instead modelled as
  **rolling on the bottom rim** of the spring end (pessimistic
  bound), the cell butt sweeps south and clips the Wing's **south
  inner corner** (not the north tab): 0.18 mm³ @10°, 1.99 @20°,
  **10.4 mm³ @35°**, at asm X 15.86..22.25, Y −6.68..−3.09,
  Z 4.70..5.90. Under the physical contact-point pivot it is 0.000
  at every angle.
- Sensitivity 2 — grip depth: a full-depth finger grip (zone floor
  lowered to Z 3.00) intrudes into the tab set by **519 mm³**
  (board 380, MUX body 47, J_WING envelope 92). Not required for the
  standard extraction, but it is the bound if the PO wants
  below-centreline access guaranteed.

## 6. Fix directions, side by side (PO addition)

For the **stated envelope (§5): no fix is needed** — δ stays 9.5,
outline stays 310, and the power-board outline (52.5 × 58.0)
survives as-is in every option below (the board never changes; under
(a) the bay widens with the outline).

If the PO wants the **rim-roll bound** (sensitivity 1) cleared:
| Option | Change | Result |
|---|---|---|
| (a) δ increase | δ 9.5 → ≈16.0 (+6.5/side, measured: clip 10.19 → 0.004 @+6, 0.000 @+7) | outline 310 → **≈323** |
| (b) Wing shape | trim the south inner corner (asm X 15.9..22.3, Y −6.7..−3.1 at δ=9.5) — measured **empty board** (no pads, no tracks in X 14..24, Y −8..−2) | δ and outline unchanged; reopens Gate 8 (outline identity) + edge-clearance re-check; J_WING, sensors, FFC geometry unmoved |
| (c) combination | unnecessary — (b) alone clears it | — |

If the PO wants the **full-depth grip** (sensitivity 2) cleared:
| Option | Change | Result |
|---|---|---|
| (a) δ increase | δ 9.5 → 19.25 (+9.75/side: tab edge 22.50 → 32.25 = finger-zone east edge) | outline 310 → **329.5** |
| (b) Wing shape | narrow the tab's west edge to the pad line ≈25.4 (+2.9; J_WING pads/envelope reach 25.62, MUX_B pads ≈25.5 — no more is available without moving J_WING, a link datum) | **insufficient alone** (zone reaches 32.25); reopens tab routing + Gates 3/4/8 |
| (c) combination | (b) + δ +6.85 | outline 310 → **323.7** |

What a tab shape change reopens, plainly: the tab carries J_WING and
U_MUX_B and ≈95 fanout segments; any west-edge trim beyond the empty
corner means re-routing the fanout and re-running Gates 3/4/6/8 on
17R + mirror check on 17L (16mm variants share the inner region
topology). The boards are unadopted and unordered, so this is cheap
in money; it costs a layout round and a re-review. A south-corner
trim (sensitivity 1, option b) is by far the smallest shape change:
empty board, outline gate only.

## Verdict

**Part 1 — static clearance: OK as-is, with two flagged inputs.**
- Wing board underside ↔ power-board top: **4.55 mm**.
- Lowest real component over the board: U_MUX body bottom 3.30 →
  **3.15 mm**; FH12 physical bottom ≈2.70 → **2.55 mm**. All ≥1.0.
- ⚠ **Flag 1 (<1.0 mm — Stage-2 input correction):** the case
  study's J_WING mating-envelope block bottoms at −0.15, i.e. it
  overlaps the power-board top (+0.15) by **0.30 mm** over a
  0.63 × 8.15 mm sliver at the board's east edge (Y −43.10..−34.95).
  The physical connector clears by 2.55, so this is an envelope
  definition issue, not a physical clash — but it must be
  dispositioned at Stage 2: either re-derive the FFC exit envelope
  from the physical connector + cable, or shift the power board west
  by ≥0.63 (east cavity clearance 2.0 → 1.37, west 2.0 → 2.63). A
  notch in the east edge is NOT recommended (return pour).
- ⚠ **Flag 2 (blocker for seating):** the existing tray post at
  X 22.73..26.25, Y −12.23..−8.70 (top 9.40) is inside the
  power-board outline — remove/relocate it in the bay re-form
  (§3). The west tray carries the mirrored feature by the tray
  pair's symmetry (Stage B pose definition); same disposition.
- Assembly: **power board first, then Wings** (§4) — record this in
  the assembly procedure inputs.

**Part 2 — removal envelope: CLEAR at δ=9.5, no δ growth required.**
Under the stated envelope (slide 2.0 + tip ≤35° about the contact
point + centreline pinch access), both the cell sweep and the finger
zones clear the Wing tabs with 0.000 mm³ intersection; the tightest
margin is 1.50 mm (finger-zone floor vs tab top). The power-board
outline survives unchanged. The two sensitivity bounds and their
priced fix directions are in §6 for the PO's choice if a stronger
envelope is wanted.
