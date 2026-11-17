## 7. Stage 2e — Wing notch redrawn: whole-span replacement, straight-line joints (Issue #273)

PO review of the Stage 2d figure (2026-11-18): the Wing notch
"does not look fixed" — both mouths carried an S-wiggle (dips at
case Y ≈ 32–34) and the simplification was not legible. Main
Rev.9 was adopted (D-044); Wing Rev.6 adoption was held for this
round. All four Wing variants were re-cut in place; Main Rev.9
is untouched.

### 7.1 Verification extract — what was actually saved in the 2d boards

The notch was measured from the saved `.kicad_pcb` Edge.Cuts
before any change, under one counting rule (element midpoint
inside the removed-vs-Rev.5 region buffered 1.0 mm):

| variant | notch-zone elements (2d, as saved) |
|---|---|
| 17mm-left | 16 (15 lines + 1 arc) |
| 17mm-right | 23 (21 lines + 2 arcs) |
| 16mm-left | 16 |
| 16mm-right | 23 |

Root cause: Stage 2d built `Wing = Rev.5 outline − keepout`.
Wherever the Rev.5 boundary lay Wing-side of the design chain,
the Rev.5 boundary survived verbatim — including its faceted
mouth arcs. The 2d dive straight was not in the saved boundary
at all: at both mouths the saved outline dipped to case
Y ≈ 32.43–32.49 (the flagged wiggle), up to 3.25 mm of Rev.5
floor stretch lay Wing-side of the design front line, and the
rise side carried a 6-facet bulge of up to 0.31 mm. The 2d
REPORT's zone counts (L 17) also differed from the recount
under the extract rule (L 16); the recount is used here for
both generations.

### 7.2 The 2e notch

The whole notch span of the Rev.5 outline was replaced by one
designed chain of **7 elements** (identical construction at
17 mm and 16 mm; the saved outline totals 329 elements —
325 lines + 4 arcs — against Rev.5's 336 lines):

dive mouth fillet → dive straight → dive corner arc → front
straight → rise corner fillet R0.55 → rise straight → rise
mouth fillet.

- The straights are the Stage 2d design lines (0.56 mm design
  offset from the tab features: wall-parallel dive, front
  parallel to the tab front, wall-parallel rise).
- Mouth transitions: each straight is EXTENDED until it meets
  the Wing's own long edge (the two "flanks" are one collinear
  edge line; assignment by segment containment), and a single
  tangent fillet is fitted there — dive mouth R0.30, rise
  mouth R1.00. No tangent-arc chains, no overshoot.
- One geometric finding: at the dive→front corner the two
  lines meet at a shallow 38° board wedge, and the 2d chain's
  R0.55 arc is a VOID-side fillet whose dive-line tangent
  point lies past the lines' intersection — a board built
  from it would fold back on itself in a thin cusp. (It never
  reached the 2d board; the keepout difference kept Rev.5's
  boundary there.) The 2e corner is the BOARD-side tangent
  arc: R0.225 (left) / R0.275 (right). The front→rise corner
  keeps R0.55 (its tangent points straddle correctly).
- Disclosure — left dive corner: the corner arc turns 142°
  inside a 1.39 mm run between the mouth fillet and the
  corner; the tangent point retreats 2.90 mm per 1 mm of
  radius, so a larger corner radius cannot coexist with a
  mouth fillet at this corner. The chosen pair (corner
  R0.225, mouth R0.30) is the max-min compromise. At high
  zoom the corner reads as a tight rounded knob; it is
  tangent-smooth — no S-wiggle and no sharp corner in any
  variant. The right corner is roomier (R0.275, same
  construction).
- Removed vs Rev.5: 12.962 mm² (left) / 12.747 mm² (right) —
  the front floor stretch and the rise bulge; copper there is
  pour fringe only (design-stage audit). Added vs Rev.5:
  20.048 mm² (left) / 12.303 mm² (right) — the straight dive
  line fills Rev.5's mouth scallops back in; the added region
  contains no copper. Pours refilled; fill delta
  17.73 mm²/layer (left) / 16.22 mm²/layer (right), confined
  to the removed+added region plus its 0.75 mm band, pour
  component counts unchanged; the Rev.5 FEM figures carry
  over (fringe holds no pad, via or track).

### 7.3 Results from the saved boards

| check | 17L | 17R | 16L | 16R | floor |
|---|---|---|---|---|---|
| seam min vs final Main Rev.9 [mm] | 0.5595 | 0.5593 | 0.5595 | 0.5594 | ≥ 0.55 |
| overlap [mm²] | 0 | 0 | 0 | 0 | 0 |
| notch-zone elements, extract rule (was §7.1) | 3 | 7 | 3 | 7 | — |
| outline symdiff vs design [mm²] | 0.0041 | 0.0030 | 0.0041 | 0.0030 | — |

(The zone count is taken over each board's own removed
region; on the left the dive half of the chain lies in the
added region and is not counted. The chain itself is 7
elements in every variant, §7.2.)

Gates (`gates-2e.json` per board, #263 yardsticks): material
DRC 0, DRC unconnected 0, copper-graph unconnected 0,
wrong-net contacts 0 — all four variants. Via-pad minima
unchanged from Rev.5: 16L 0.1032, 16R 0.1063, 17L 0.1252,
17R 0.1400 mm (floor 0.10). Non-outline census identical;
routing and footprints untouched; outline inside the D-037
silhouette at both pitches.

### 7.4 Case

CASE-DELTA: <pending>
FITTED-AUDIT: <pending>

### 7.5 Packages

Wing manufacturing packages regenerated from the final boards
(make-packages-2e.py): gerbers + drill + pos re-exported;
BOM/CPL re-verified (49 JLCPCB BOM rows, 49 CPL rows verified
against the fresh exports, FH12 = C5378715); FABRICATION.md
and quote-handoff.md updated to the 2e state. All packages
remain DRAFT / NOT FOR ORDER. The Main Rev.9 package stands
unchanged.

Figures (drawn from the saved board files):
`.issue273-runtime/fig-2e-full.png` (fitted layout) and
`fig-2e-notch.png` (notch zooms on the Stage 2d figure's axes:
Rev.5 grey dotted, 2d red dashed, 2e blue).
