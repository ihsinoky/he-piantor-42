# Issue #248 Phase B — Round 12

**PROVISIONAL on plateau Z24.65 / q=1.50. NOT RELEASED.**

## Verdict — the flat order-preserving fan turn is impossible; no candidate built

PO's round-12 mandate (flat reserve, order-preserving fan-shaped turn, neck
channel reshape under unfreeze steps 1–2, OD1 gates standing) was screened.
The screen fails at the turn, with proof-standard evidence in three
independent forms. The neck, by contrast, turns out to be essentially free —
the round-9 window was route-imposed, not solid-imposed (see ledger).

### Proof 1 — planar U-turns of a parallel row necessarily reverse order

For two same-direction semicircular U-turns (radii r, r+Δρ; centres offset
d, entry pitch p=1.25), non-crossing requires nesting, d ≤ |Δρ|. The centre
offset obeys |ΔC| = |p − Δρ| (for the order-preserving sign of Δρ), so
nesting requires |Δρ| ≥ |p − Δρ|, i.e. Δρ ≥ p/2 = 0.625 — which forces the
exit pitch p − 2Δρ ≤ 0. Hence any family of pairwise-disjoint planar
semicircular U-turns exits in reversed (or degenerate) order; an
order-preserving (inversions = 0) flat 180° turn of the 14-strand row does
not exist. The only escapes are turn reversal (round-9 family), Z-separation
(round-11 family, closed by proof in round 11), or crossings.

### Proof 2 — numeric scan of the mandated fan family

Fan as mandated (two R5 quarter arcs + straight per strand, Y-stagger g,
west shift 10+L, Z-ramp exit 5.1→4.0), new zone only (Wing outlet to the
round-9 after[2] handoff), centreline all-pairs, right side:

| g | L | min distance | pairs < 1.0 (of 91) |
|---|---|---|---|
| 1.05 | 0 | 0.000 | 61 |
| 1.05 | 4 | 0.000 | 64 |
| 1.50 | 0 | 0.000 | 55 |
| 1.50 | 4 | 0.000 | 66 |
| 2.00 | 0 | 0.000 | 75 |
| 2.00 | 4 | 0.000 | 81 |
| 2.50 | 0 | 0.000 | 78 |
| 2.50 | 4 | 0.000 | 76 |

Worst pair throughout: pins 2–3, arc2–arc2 — the equal-R5 arc intersection
predicted analytically (intersection at ≈139° lies on both arc2 spans for
g=1.05). Clearing arc2–arc2 needs g ≳ 6, i.e. a 78 mm stagger band; the
available band is ≲36 mm and is further capped at the east edge by the
U_HC1 underside bound (X 32.3–36.9, Y −4.18..0.46, Z 3.95–7.35): strands
1–2 cannot run the Z5.1 row north of Y ≈ −4.7. Length was not the fan's
problem (v1 finished max 180.265 mm); topology is.

### Proof 3 — the wide-row concentric fallback fails on radius and length

Single-centre concentric turn of the uncompressed row (the only disjoint
planar family): centre inside the row span leaves 8 strands with radius
< 5 (R ≥ 5 violated); centre outside the span (XC = 13.875, min radius
exactly 5.0) gives pin 1 an arc of π·21.25 = 66.76 mm and a finished
length of 220.54 mm > 200. The round-9 funnel existed precisely to buy
turn-radius economy (pack span 3.03 → radii 5.03–8.06); a wide row cannot
afford a disjoint planar turn.

### Neck ledger — the window was route-imposed; almost nothing to reshape

Exact-Common band probes against the frozen round-9 solids (17 mm;
probe validated on a sanity band, wing_right 600.0 mm³):

- Neck row band (Y −16..−12 across the Y=−14 cut, X 17.9–36.1,
  Z 4.55–5.65): only **tray-right 0.016 mm³**. A single local tray cut of
  ~0.02 mm³ class (unfreeze step 1) would clear the wide channel at the
  neck plane.
- Corridor band (Y −24.5..2.5, same X/Z): tray-right 0.297 mm³;
  underside-right-U_HC1 10.758 mm³ (the fixed sensor bound above — not
  reshapable, it caps the northern reach instead).
- Turn/outbound bands (X 3–37) contain tray-right 32.699 / 43.116 mm³ —
  these volumes sit in the western pack/splice region the wide route does
  not use; band-level presence only, not path-resolved.

Fixed-body changes consumed: **none** (no build). POM notch: not consumed.
The reshaped channel the mandate priced is therefore nearly free — but it
cannot rescue the design, because the binding constraint is the turn,
upstream of the neck.

### Gate table — round 12

Screen stage only; build stage not entered (screen not clean). Gates 1–8
not run. Baseline unchanged: round-9 candidate, true strand–strand 110
(repaired audit), gates 2/4/5/6/7/8 PASS, longest finished 198.366 mm.

### Remaining blockers / what a successor must satisfy

The reserve problem is now closed from three sides: assignment-only
(rounds 8–9, floor 110 true), vertical (round 11, proof), flat
order-preserving (this round, proof + scan). Any successor must either
(a) accept turn reversal and re-sort the outbound family across a
Z-separated wide frontage — noting the re-sort then faces the same
funnel economics in reverse plus round 9's compressed after[2] handoff
(pitch 0.26–0.36, inherited with the frozen G feed) — or (b) change the
service mechanism or interconnect, which is outside the frozen set and a
PO decision. The neck is not the constraint; the turn is.

