# Issue #296 north-flush revision — plan note (2026-11-21)

PO instruction: the case's north edge must be FLUSH (ツライチ) — a
straight, flat north face. The current curve on the north side is not
wanted; remove it.

## Step 1 — identify the curve (measure before changing)

From the delivered renders, the visible curve is in PLAN: the north
outline of the left/right halves (strip + tray + plate stack) arcs
away from the centre battery bay instead of running straight. The
bay north wall itself is already straight at Y −64.37 (X ±30.25).

Measure, per part and for the fused assembly (STL vertex analysis +
BREP section checks):
- Y_north(X) = min Y at each X (1 mm bins) for every part; which
  parts form the exterior north boundary in which X spans.
- The deviation of Y_north(X) from (a) the constant −64.37 and
  (b) the chord between its endpoints, per span.
- North face profile: at sample X stations, outer Y as a function
  of Z (is the face also sloped/curved in profile?).

## Step 2 — re-form

Target: one straight flush north face at Y = −64.37 across the
assembly (the existing outline limit; bbox stays 310 × 146.1 class).
Method decided from the measurements: clip what bulges north of the
plane (expected: nothing — −64.37 is already the min), fill the
sagging spans forward to the plane on the exterior parts (trays /
strips / shell as applicable), keeping interior cavities, the Wing /
plate envelopes and all Stage-3D features untouched. Where a fill
would collide with an interior feature (Wing north tips at −61.60,
plate, Fly gable), the wall thickens only where the interior allows;
any span that cannot reach the plane is reported, not forced.

Wait — re-read the brief: "north face at case Y −64.37; overall
outline stays 310 × 146.1 class". Filling to −64.37 across the full
width keeps the bbox (depth already set by the bay wall). But check
the interior: the angled halves' cavities (Wing boards, plates) sit
close under the current north edges; a full-width fill to −64.37
may not be geometrically free everywhere. Measurements decide the
fill envelope per span; collisions resolved by wall-thickness only
where the cavity permits, else flagged in the addendum.

## Step 3 — re-verify (numbers, revised model)

- Battery removal sweeps ×3 (slide 2.0 + tip 35°) vs case + Wings.
- Fly/USB gable vs the flush face: mouth protrusion (was 0.16),
  opening position, mated plug vs tray/plate = 0.000.
- Cover: lid, north skirt, 2 screws at (±24.25, −63.37).
- Full interference table re-run (same set as verify_case3d.py);
  accepted items re-confirmed (J_WING envelope ∩ E/W sill 42.38/side
  artifact class; finger-zone bounds).
- Z ≤ 22.00; cover top 16.65; outline re-stated; Y_north(X) flatness
  table (max deviation from −64.37 across the width).

## Step 4 — renders + records

Re-render top + perspective-open (+ closed if visibly changed) over
the goal files; addendum in case-3d.md; Issue #296 comment; GOAL.md
line; commits on issue-296-stageb (checkpoint per step).

## Addendum 2026-11-21 (later PO instructions, same revision)

### Curve identification — measured (BREP slab sampling)

- Tray north wall + strip form ONE vertical north face,
  Z −2.65..22.00 (tray face band −2.65..10.90, strip 10.90..22.00,
  identical Y at every station). Its plan trace is a circular arc:
  two-point solve through (32, −55.26) and (118, −64.37) with centre
  on the centreline gives centre ≈ (0, −768), R ≈ 713; sag vs the
  −64.37 plane: 8.9 mm at |X|=32, 5.6 at |X|=77, 0 at |X|=118.
  Beyond |X|≈118 the outline is the angled end edge (not the arc).
- Strip = thin rim band only (material within ~3 mm of the face,
  top flat at 22.00 everywhere along it). The visible slope surface
  south of it is the tray's moulded top.
- Shell-central: north boundary is a V of two straight diagonals
  from (0, −0.37) — NOT curved. Top ridge descends 22.00 (Y≈0) →
  15.11 (Y=27) → 11.10 (Y≥32, trackpad seat floor inside Ø44.6) /
  10.90 (Y≥67).

### PO intended profile (2026-11-21, replaces the slope-cover concept)

1. North band at Z22.00, full width, south to just before the keys.
2. Centre + south at plate top Z10.90; D-053 trackpad intact.
3. Transition: slope where space allows, cliff acceptable.
4. North face flush at Y −64.37 (this revision's original brief).

### Design decisions taken (measured basis)

- Keycap envelopes from the built plates: 21 keys/side, pitch
  17.00, grid angles L 30° / R 60° (per-key angles for the 3 thumb
  keys). Cap = 16.5 mm square at each key's angle (17-pitch class;
  g17 switch envelope is 15.8 — caps assumed 16.5; Junana physical
  measurement still open → sensitivity noted in the addendum).
  Band south edge = capline − 1.0 mm clearance, per 1 mm column;
  cap-free columns take the nearest cap column's line (constant
  extension). Pressed state lowers caps only (plan-invariant);
  verified with solids at top 22.00 (unpressed) and 19.00 (pressed
  model, 3.0 travel) — both must be 0.000 vs the case.
- Halves: transition = CLIFF at the key line (run available =
  the 1.0 mm clearance only).
- Centre: SLOPE from the bay south wall face (Y −0.37, Z 22.00)
  to (Y 20.0, Z 10.90) — run 20.37, 28.6° — landing 5.7 mm north
  of the trackpad island edge (Y 25.7). Applied to shell-central
  (incl. the strips' south lobes, transferred to the shell) via a
  Y-Z profile cut, trackpad island exempted by a Ø47 keep-disc at
  (0, 48).
- Battery lid: top raised 16.65 → 22.00 (underside 15.15 and all
  skirts unchanged; screw holes lengthened) so the band is
  continuous over the bay; lid stays vertically removable
  (footprint |X| ≤ 30.25 vs plateaus |X| ≥ 30.25 — lift test in
  verification).
- Strips replaced by band plateaus (Z 10.90..22.00, face → key
  line, trimmed by the tray plan silhouette). Old strip material
  south of the key line (east-of-bay connector south part) is
  removed; the flank transition there is plateau cliff + the
  existing tray slope. Strip lobes south of the bay (X ±10..30.25,
  Y ≥ −0.37) transfer to shell-central and take the centre profile.
- Fly: shift a further 8.17 mm north → centre (38, −60.11), mouth
  exactly flush with the new face (0.00 proud; the previous 0.16
  proud cannot stand at the outline limit). Pocket / USB opening /
  plate rim notch shift with it. EZmate ≈ 96.8 mm ≪ 170.
- Forced local adjustments: DLED light pipe re-trimmed to the
  slope surface at (−4, 13) → top Z 14.71; SW1 plunger re-trimmed
  to the 10.90 surface at (−15.5, 64.50) → stem 7.2..10.9, head
  10.9..12.1. DLED hole re-cut after the slope fuse.

