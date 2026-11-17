# Issue #270 Stage 2a — Candidate C revised: 60° trapezoid tabs + matched Wing notches (2D design)

PO decision (2026-11-17): candidate C, revised together with the
Wing — Main tab walls at ~60°, Wing inner-corner notches reworked in
the same pass so the Main↔Wing seam reads as ONE designed joint
(matched angles, uniform gap). This stage is 2D only: no board or
case files were modified. Figures: `fig-s2a-layout.png`,
`fig-s2a-zoom-j2.png`, `fig-s2a-zoom-j3.png`. Numbers: `stage2a.json`
(scripts `s2a_extract.py`, `s2a_design.py`, diagnostics `s2a_diag*.py`).

## The 60° — definition

**60° is the angle between the tab side wall and the board's slanted
edge line.** The tab front edge is parallel to that edge, so the wall
also makes 60° with the front edge (acute angle between the lines).
Equivalently, in the trapezoid itself: interior angle at the base
corners = 60°, at the front corners = 120°. The definition is applied
identically at both sites (each site measured against its own slanted
edge), so the two tabs are mirror-symmetric in shape.

## Main tab spec (identical both sites, per-site edge frame (t,d))

Frame: t along the site's Rev.7 slanted edge, d = outward normal
(the stage-1 `sites.json` frames). Each tab is centred on its current
tab centre (J2 t_c = 42.973, J3 t_c = 24.993).

| Parameter | Value |
|---|---|
| Depth D (front edge at d = D) | 4.738 mm (both sites; J3 was 4.721) |
| Front length L_f (at d = D) | 16.689 mm |
| Wall angle to edge/front line | 60° (base interior 60°, front interior 120°) |
| Wall run per side r = D / tan 60° | 2.735 mm |
| Base width (at d = 0) | 22.160 mm |
| Wall length D / sin 60° | 5.471 mm |

Per-site (t,d) corners — front (t_c ± 8.345, 4.738), base
(t_c ± 11.080, 0):

- J2: front t ∈ [34.628, 51.317], base t ∈ [31.893, 54.052]
- J3: front t ∈ [16.648, 33.337], base t ∈ [13.913, 36.072]

New Main outline = Rev.7 outline ∪ the two trapezoid blobs (same
construction as stage 1). ZIF poses unchanged. Board area
2623.1 → 2642.6 mm². A front length of 15.689 mm was also evaluated
and rejected: it cuts 1.00 mm² off the Rev.8 front corners for no
benefit (pad clearance identical, tray delta only 0.6 mm³ lower).

## Wing notch spec (all four variants, fitted case frame)

New notch = current Wing outline minus the 0.55 mm offset region of
the new Main outline. The notch floor is therefore the exact offset
of the new tab:

- front run parallel to the tab front at **0.55 mm**;
- both wall runs parallel to the tab walls (60°) at **0.55 mm** —
  the faces are matched-angle, not just equidistant at one point;
- front-corner arcs R0.55 (the offset's round joins);
- at the two mouths the floor blends back into the existing Wing
  edge. Stage 2b may add fillets of R ≤ 1.0 at the mouth corners:
  filleting there removes Wing material only, so the gap can only
  grow — re-verify in 2b.

Uniformity, measured: of the Wing boundary facing the tab within
1.2 mm (26.5 mm L / 26.3 mm R), **20.7 mm (L) / 21.3 mm (R) runs at
0.55 ± 0.01 mm** (front run + both wall runs + corner arcs); the
remainder is the two mouth blends where the gap opens back up to the
existing edge. Minimum gap anywhere = 0.550 mm.

**Pairing caveat (must be recorded):** the new Main outline on its
own overlaps the CURRENT Wing outline by 0.016 mm² (L) / 0.069 mm²
(R) at the notch mouths — the trapezoid's base flare reaches the
current notch entries. The two boards are designed as a pair: Main
with the 60° tabs must not be built against an unmodified Rev.5
Wing, nor the re-notched Wing against a Rev.8 Main (that pairing
would leave a wider, non-uniform gap). Adoption, if approved, is as
a Main + Wing outline pair.

## Checks

### Seam and pads (both pitches; construction identical, results identical)

| Check | 17 mm L | 17 mm R | 16 mm L | 16 mm R | Yardstick |
|---|---|---|---|---|---|
| Seam (new pair) | **0.550** | **0.550** | **0.550** | **0.550** | target ≥ 0.52, floor 0.50 (current 0.5215 / 0.5221) |
| Overlap (new pair) | 0 | 0 | 0 | 0 | 0 |

Main-side (pitch-independent): pad-corner clearance **0.8364 mm**
(worst J3.14; ≥ 0.82 class, floor 0.70 — equals stage-1 C, up from
the as-built 0.8197 because J3's depth is now also 4.738); pads
uncovered 0; silk containment unchanged (min dist 0.15 mm, 0
uncovered — same as current and stage-1 C).

### Wing notch vs Wing copper (all four variants)

The additional material removed by the re-shaped notch (beyond the
current notch) intersects **no track, via or pad, and no footprint
courtyard, in any variant**. Nearest copper to the removed region:
1.9 mm (17L), 10.5 mm (17R), 1.9 mm (16L), 6.6 mm (16R) — comfortably
beyond the 0.6 mm clear zone the current notch was verified with.

Removed-area delta vs the current notch: **+1.25 mm² (L) /
+1.88 mm² (R)**, identical at both pitches (the notch-zone geometry
is the same; the variants differ elsewhere). Total notch removal vs
the un-notched Rev.5 outline at 17 mm: 63.5 → 64.8 mm² (L),
62.6 → 64.5 mm² (R).

### Main tab edge vs Main copper

Outline removed vs Rev.8: 0.006 mm² (chord-approximation residue of
the outline extraction, spread over the whole perimeter — the
trapezoids are supersets of the rectangular tabs in the tab zones).
Copper cuts **0**; min edge-to-copper clearance **0.284 mm** (same
as stage-1 C; current Rev.8: 0.226). No re-route implied.

### Case / tray

Both new outlines remain inside the D-037 silhouette (Main and all
Wing variants). Main growth ∩ tray (stage-1 harness, current tabs =
3.284 / 3.004 mm²): new 4.796 (L) / 4.617 (R) mm² → tray pocket
relief delta **+1.81 mm³ (L) / +1.94 mm³ (R)** vs the current tabs
(total +3.75 mm³; stage-1 C was +1.45 total — the 60° flare adds
growth beside the tabs, part of which lands in the pockets). The
Wing only shrinks, so no Wing-side tray change.

## Validation anchors

- Extraction reproduces the current seam 0.5215 / 0.5221 and overlap
  0 at BOTH pitches (16 mm variants share the (±27, −37.5) envelope
  anchor and ±30.5° rotation per `pose-verification.json`).
- Stage-1 control numbers re-derived where shared: pad clearance
  0.8364 and copper clearance 0.284 match stage-1 candidate C
  exactly (same front geometry); silk 0.15 matches current.

## Stage 2b inputs (if PO approves)

1. Main: replace both tab rectangles with the trapezoid spec above
   (Edge.Cuts only in the tab zones; expect DRC re-run + extraction
   unchanged elsewhere — the tabs are outline-only, copper untouched).
2. Wing (×4): redraw the notch floor per the offset spec above
   (front/wall runs at +0.55 from the new tab, R0.55 corner arcs,
   mouth blends; optional R ≤ 1.0 mouth fillets). No copper moves:
   the notch stays ≥ 1.9 mm from the nearest copper.
3. Case: add +1.81 / +1.94 mm³ to the tray pocket reliefs.
4. Re-run the fitted audit with the new pair; adopt as a pair
   (pairing caveat above).
