# Issue #248 Phase B — Round 7

**PROVISIONAL on plateau Z24.65 / q=1.50. NOT RELEASED.**

## Stage 0 — before conductor solids

Copilot’s full second opinion was read first and copied to [sources/second-opinion-copilot-round7.md](sources/second-opinion-copilot-round7.md). Current Issue comments are preserved in sources/issue248-round7.json. Its suggestions are hypotheses, not measured CAD results. BASE is exclusively frozen round5/. Frozen round6/ and round6-sha256.json preserve the preceding full package; rounds 3–5 are untouched. All round-5 BRep operands were recovered by exact serialized hashes into runtime/round7/frozen-operands; no STEP recovery or fixed-body repair is needed.

### 1. Native maps and centreline inversion analysis

Both native J2/J3 rows have increasing pin number in local u. Their assembly poses differ: the global Main row vector per pin is (−0.625,+1.082532,0) on the left and (−0.625,−1.082532,0) on the right. Wing global X also decreases with pin on BOTH sides. Thus global-X endpoint permutation is the identity (0 inversions), not reversal (91). Substituting Main local u for assembly X produces the advisor’s erroneous reversal conclusion. Main exit tangents are mirrored; projecting onto the endpoint lateral normals (+0.5,−0.866025,0) left / (+0.5,+0.866025,0) right gives the same endpoint order as the Wing normal (+1,0,0). This does not prove that an arbitrary intervening 3D route needs no frame rotation: the route’s transported frame must be checked.

The declared stage ranks below use increasing assembly X, ties within 1e−8 mm resolved by Z then cavity. Tied X groups and every coordinate are disclosed in stage0-round7.json. The bundle has multiple Z rows: a projected inversion is NOT itself proof of a physical collision. The reserve is a travel-direction reversal: its local lateral normal changes sign. Do not add its projected inversions to an axial-twist budget. The actual round-5 traversal has its rise AFTER the reserve, contrary to the upstream-rise assumption in the advice.

| Stage in traversal order | Left order | Δ inversions | Right order | Δ inversions |
|---|---|---:|---|---:|
| outlet | 14,13,12,11,10,9,8,7,6,5,4,3,2,1 | 0 | 14,13,12,11,10,9,8,7,6,5,4,3,2,1 | 0 |
| corridor | 14,13,12,11,10,9,8,7,6,5,4,3,2,1 | 0 | 14,13,12,11,10,9,8,7,6,5,4,3,2,1 | 0 |
| reserve_in | 4,11,7,14,3,10,6,13,2,9,5,12,1,8 | 40 | 14,7,10,3,13,6,9,2,12,5,8,1,11,4 | 33 |
| reserve_out | 1,8,5,12,2,9,6,13,3,10,7,14,4,11 | 84 | 11,4,8,1,12,5,9,2,13,6,10,3,14,7 | 84 |
| rise_base | 5,10,1,6,11,2,7,12,3,8,13,4,9,14 | 37 | 1,11,6,2,12,7,3,13,8,4,14,9,5,10 | 40 |
| rise_top | 5,10,6,1,11,7,2,12,8,3,13,9,4,14 | 4 | 1,6,11,2,7,12,3,8,13,4,9,14,5,10 | 4 |
| fan | 5,10,6,1,11,7,2,12,8,3,13,9,4,14 | 0 | 1,6,11,2,7,12,3,8,13,4,9,14,5,10 | 0 |
| Main_row | 14,13,12,11,10,9,8,7,6,5,4,3,2,1 | 57 | 14,13,12,11,10,9,8,7,6,5,4,3,2,1 | 61 |

The independent 1001-point-per-strand baseline centreline screen finds 85 same-side pairs below OD1 on each side. It is a cheap screen, not the exact contact count: frozen round-5 exact audit reports 163 strand pairs total. Contact witnesses in stage0-round7.json locate them along the actual paths. Native endpoints remain bound to immutable pinmap-round4.json / round5/pinmap-round5.json.

### 2. Fixed-body twist envelope

stage0-envelope-17.json and stage0-envelope-16.json contain exact distances from existing fixed solids to 36 zero-thickness circular cross-sections per pitch. No new solid is generated for this screen. Full 14-wide diameter14.65 mm fails all 18 tested sections in both pitches. Half-width diameter7.30 mm clears 10/18 sections: six lie in the existing POST-reserve rise and four at X±5/Y−22 or−12/Z5.8. These are necessary cross-section clearances only; the best tempting upstream station has only 0.15 mm distance to the fixed tray floor. At the actual low reserve leg X±10.85 all tested half-ribbon sections are blocked by Wing/tray geometry. The X±5/Y−7 sections are tray-blocked. The full-station interval, inlet approaches, two half-ribbon coexistence, and service boundaries must be checked; cross-section PASS is not an envelope PASS.

### 3. Analytic lengths and curvature

Unchanged sourced tails are Wing3.90 + Main3.40 =7.30 mm. For a constant-rate half-turn at radius r and axial run L, length is sqrt(L²+(πr)²) and curvature radius is (r²+(L/π)²)/r. Entrance/exit angular-rate blending adds constraints. At r6.825/L20 the edge-wire excess is 9.32 mm, refuting the quoted ≈0.5 mm. Adding a full-width helix to equal-length round-5 axial runs exceeds 200 mm at every tested L12.727–30 (longest201.01–206.34 mm), even before blends. This is a screen of this replacement scheme, not a lower bound on all possible reroutes. The half-width replacement screen is length-plausible (197.05–197.53 mm); it does not include the 7+7 group exchange.

Two independent 7-wire flips give [7…1,14…8], not [14…1]; 49 cross-group inversions remain. Therefore the proposed two half-ribbons require an additional group-exchange construction or a jointly rotating packed section. A pure helix also has non-axial endpoint tangents unless its angular rate is blended to zero.

A 14-radius coplanar nested U has13×1.05=13.65 mm spread and π×13.65=42.882740 mm outer-minus-inner length. This verifies the advisor’s differential, but DOES NOT establish length impossibility: longer base wires can take shorter radii and a full path must be evaluated. Z-spread is tested as the requested fallback, retaining the existing fourteen low-pack reserve lanes and all fixed case/channel geometry. A true transported ribbon through the return hairpin needs a frame alignment of about50°, not an assumed180°. The first centreline prototype (central return R7.15) was rejected before solids after sampled edge curvature R4.795; its source/log remain in runtime. The next prototype enlarges only routing curvature, not any fixed body. Length and R≥5 screens remain binding.

Stage-0 verdict: **(a) pure-reversal claim REFUTED in verified assembly endpoint frames; (b) zero-contact claim UNPROVEN and not implied by a reversal count; (c) radial length differential VERIFIED, universal length-unaffordability NOT PROVED.** No strand solids may be swept until a complete candidate passes analytic length and bend screening.

### Complete candidate screen before solids

The stacked low/high two-row crossing prototype was rejected without sweeping: longest finished200.260842 mm; released return fillets have negative tangent slack on all14 strands (−1.250446…−0.077952 mm). It also retains60 sampled close pairs at the Main fan. The radius certificate exposed a separate sampling hazard in the R8.2 return candidate: pin2’s continuous lower bound4.973302 mm invalidated its sampled R5.086848 result. That candidate was rejected. See sources/round7/rejected-r8p2-curve-certificates.json.

The selected **diagnostic** fallback uses R8.5 central return bends and the original14 reserve lanes, with Z spread before inlet compression and an ordered transported return. It has a complete finished upper bound186.056270 mm (13.943730 mm margin), including unchanged7.30 mm tails. The14 non-rational spline curves are certified continuously by converting to Bezier patches and bounding |v×a| / |v|³ using Bernstein control-vector convex hulls, with adaptive subdivision. Lowest certified spline radius5.276689 mm; the overall minimum is the unchanged inner reserve radius5.035 mm. Independent per-patch quadrature agrees with kernel spline lengths within2.1e−13 mm. These tests precede ALL new conductor solids. See curve-certificates-round7.json and curve_certificate_round7.py.

This fallback is not asserted contact-free: the cheap screen still has79 close same-side pairs, notably where the inlet diagonal meets the low return and at the Main fan. It is carried through the required full audit to expose actual fixed-body, strand and service blockers. No dedicated180° twist was installed: the verified endpoint frames do not require the advisor’s asserted permutation, the full-width station fails its envelope, no complete upstream7+7 station was qualified, and the post-reserve rise cannot silently be called upstream. The fallback is explicitly a nested horizontal U with existing Z-spread, followed by an ordered return hairpin; it is a failed routing trial unless the independent gates establish otherwise. It does not fulfil an exactly-one-twist construction.

