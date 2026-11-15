# Round 12 design note - flat fan-turn reserve + neck reshape

## Route topology (per side, 14 strands, order preserved everywhere)
Wing outlet -> corridor (own X order) -> NECK (reshaped, see below)
-> southbound row run -> FAN TURN (flat, corridor height)
-> northbound row run -> rise -> round-9 on-axis G stations (unchanged) -> Main inlet.

## Fan turn (order-preserving by construction; NOT concentric, NOT nested-U)
- All strands at corridor height band: crowns Z <= 11.55 (hard cap), turn in plan (XY).
- Strand i (X_i = X_0 + 1.25*i at row entry): U-turn = two R5 quarter arcs + east straight L_i.
  - Turn start staggered in Y (staircase fan): Y_i = Y_t - i*g, g >= 1.05 (fan pitch in Y).
  - Leg A: southbound at X_i to Y_i. Quarter arc R5 -> eastbound at Y_i - 5.
  - East straight L_i >= 0. Quarter arc R5 -> northbound at X_i + 10 + L_i, from Y_i - 5... exit Y back at Y_i level.
  - Exit order: X'_i = X_i + 10 + L_i; require X'_{i+1} - X'_i >= 1.05 -> L_{i+1} - L_i >= -0.20.
  - Choose L_i non-decreasing (L_i = L_0 + max(0, ...) TBD by screen) -> exits at >=1.25 pitch.
  - Arc cost per strand: pi*5 = 15.708 (two quarters = one half circle) + L_i + stagger extra 2*(i*g) in legs.
- Screen decides g, L_0, turn side (east vs west mirror per side L/R).

## Neck reshape (unfreeze steps 1-2, LEDGER)
- Replace narrow pack window (~3.2 x 2.2 at Y~-14, 28 passes, mean 0.76) with a
  WIDE FLAT channel in tray/shell local geometry at the neck only:
  - Two stacked single rows: inbound row Z = z1, outbound row Z = z2, z2 - z1 >= 1.05.
  - Each row: 14 strands at 1.25 pitch -> span 16.25; channel clear width >= 17.3 (0.5 margin/side).
  - Channel clear height: z2 - z1 + 1.0 (wire OD) + 0.3 top/bottom clearance.
  - Crossings in plan at the wall: outbound strand i passes over inbound strand i (same X,
    order preserved) -> separation purely in Z >= 1.05. No diagonal braiding.
- Exact free section to be MEASURED from frozen round-9 solids before fixing z1/z2/width;
  if width < 17.3 available, fall back: pitch 1.10 -> span 14.3, width >= 15.3 (still >=1.0+margin pair dist in-row? in-row pitch IS pair distance: 1.10 ok, margin 0.10).

## Service (30.20 mm release)
- Fan reserve slides: the whole southbound+turn+northbound loop translates; moving part =
  loop south of neck fixed plane; slide corridor screened by exact Common at sampled offsets
  (0, +10, +20, +30.20 mm along release direction) vs fixed bodies + own fixed parts.

## Length budget (analytic, per strand, must be <= 200 - tails 7.30 = 192.70 routed)
- Itemise: outlet->neck, neck->turn legs (incl. stagger 2*i*g), fan (pi*5 + L_i),
  northbound run, rise, G feed (round-9 values), tails 3.90 + 3.40.
- Round-9 routed reference: 198.366 - 7.30 = 191.066 total incl tails; margin is thin ->
  fan placement must recover length vs round-9 pack path; report delta per zone.

## Screens (all with EXACT Common for fixed bodies from the start)
(a) centreline all-pairs min dist per zone >= 1.0 + margin target
(b) per-stage inversions = 0 at cuts: outlet, neck-in, neck-out, turn-in, turn-out, rise, G
(c) exact Common probes: strand sample points vs fixed solids in neck/turn/rise zones
(d) analytic length <= 192.70 routed, per-strand table
(e) service motion exact Common at sampled slides
