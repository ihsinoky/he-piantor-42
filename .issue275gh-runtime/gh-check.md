# Issue #275 Phase 2 — GH harness geometric check (flipped Main)

Study only, no board changes. Configuration per D-046 and the PO direction of
2026-11-18: Main Rev.10 installed flipped (components down, Wing-link
connectors on the underside), Wing side = GH side-entry underside as qualified
in Wing Rev.4, harness = 14 discrete wires/side (OD ≤ 1.0 mm, six returns
separate, ≤ 200 mm, D-024/D-033), case = adopted low-deck production tree
(plate 10.90) with the D-046 pocket. Machinery: #248 frontier library
(`fitlibF.bodies_at`) + the repaired exhaustive audit (ShapeList-aware boolean
Common; BRepExtrema for zero-Common near pairs — the #248 round-10 repair).
Scripts and raw results: `.issue275gh-runtime/build_audit.py`,
`audit-1295.json`, `audit-1295-wireside.json`, `audit-bow6.json`, `plan.md`.

## Q1 — Wing-end fit at plate 10.90: FAIL, margin −1.25 / −1.75 mm

| number | value | source |
|---|---|---|
| Wing PCB underside Z (B) | 4.70 | production README datum; cross-checked vs frontier Wing slab shifted to s=−2.65 |
| tray floor top Z | 1.60 | production tree |
| available gap | 3.10 mm | |
| GH mated plug height | 4.35 nominal / 4.85 reserved (+0.50 allowance) | #235 |
| plug bottom Z | 0.35 nominal / −0.25 reserved | |
| **margin vs floor** | **−1.25 mm nominal / −1.75 mm reserved** | |

Boolean quantification: plug envelope ∩ tray floor at 10.90 = **310.209 mm³**.
The plug body alone binds — no routing choice at plate 10.90 can pass this.
This is the binding constraint of the whole configuration at 10.90.

## Q4 — Height ladder (binding checks only, ~0.5 mm steps)

| plate | B | plug bottom Z | result |
|---|---|---|---|
| 10.90 | 4.70 | 0.35 | FAIL (short 1.25 nominal / 1.75 reserved) |
| 11.90 | 5.70 | 0.85 | FAIL (short 0.75 reserved) |
| 12.40 | 6.20 | 1.35 | FAIL (short 0.25 reserved) |
| 12.65 | 6.45 | 1.60 | arithmetic zero-gap point (reserved envelope) |
| **12.95** | **6.75** | **1.90** | **PASS (+0.30 free) — first passing step; full audit run here** |

Cross-checks: the #261 ladder (plate = B + 6.20 → GH row 12.95) and #248
Phase A (B = 7.35 at plate 13.55 = floor 2.00 + 4.85 + 0.50 free) agree.
**Minimum passing plate height = 12.95 mm, i.e. GH costs +2.05 mm of deck
over the adopted FPC at 10.90.** Binding constraint at 10.90: Wing-end plug vs
tray floor (Q1). At 12.95 no wire-level constraint binds (below); the residual
items are the exit-wire clearance (0.24 mm), the plug-envelope keep-out, and
the service reserve — none of them height-coupled.

## Q2 — Full audit at plate 12.95 (frontier s = −0.60): PASS for the harness

Fixed set: 331 bodies — frontier bodies with the pre-lever tray replaced by
the production floor slabs (top 1.60) and D-046 pocket (X −6..13, Y 28..48,
top 0.60); Main-study bodies replaced by their flipped mirrors about the
Rev.10 underside plane; Fly board official model (68 solids) + 170 mm cable +
EZmate plug in **normal pose**; #248 raised-shell bodies excluded (not part of
the low-deck case). Method validation: all 28 wire solids valid, volume =
π·0.25·length within 0.5 mm³; self-test (R1 shifted −3.0 mm in Z) intersects
the floor by 27.031 mm³ > 0; spot BRepExtrema R1–R2 = 0.232 mm (real
clearance, vs 0.0 in the pre-repair broken audit).

- **Wire–fixed contacts: 0. Wire–wire contacts: 0. Plan crossings: 0.**
- **Lengths 75.36–86.57 mm, all ≤ 200 mm.**
- Nearest clearance: exit wires vs the Wing underside U_HC1 reservation,
  0.236–0.25 mm.
- Fly (normal pose): no contact with any wire. The flipped-J4/USB residual
  from D-046 is independent of the link type and out of scope here.
- **16 mm pitch:** the frontier J_WING envelopes at pitch 16 are
  bbox-identical to pitch 17 — the Wing connector site is pitch-invariant in
  case frame, so this audit covers both pitches.

**Plug envelopes vs flipped component reservations (named residual).** Both
the Main plug envelope (21.76 × 8.15 × 4.85 reserved) and the flipped
Main-study bodies are bounding reservations, not physical parts; their
overlaps are height-invariant (both hang from the board underside), so this
is a conversion-respin keep-out item, not a height gate. With the envelope in
the assignment's placement (board side of the row): grazes C2 0.182 mm³,
Y1 0.022, C22 0.018. With the envelope on the wire side (the Wing-analogous
orientation): U4 5.839, C28 4.294, C17 3.009, C2 0.382, C27 0.134 mm³. A GH
conversion respin must keep out or relocate **U4 / C17 / C27 / C28** (watch
C2 / Y1 / C22) around the J2/J3 sites, or fit lower-profile parts there.

**Service reserve.** Measured by re-auditing a bowed variant (fan bowed 6 mm
toward case centre): per-wire length gain only 1.66–4.76 mm, and that bow
already grazes the joint-screw post (R1, 0.708 mm³) and flipped C26
(L13, 0.018). Clean stored reserve inside the audited corridor is therefore
≈ 0–2 mm — **far below the ≥ 30 mm bound set for the #242/#246 cover design**
(reported per assignment, not failed on it alone). The configuration's real
provision is build length: routed 75–87 mm vs the 200 mm qualification bound
leaves ~113 mm that a conversion-stage route can store as a wide loop in the
open tray; and the practical detach sequence is board removal (Wing/Main
screws) followed by hand-held plug extraction (7.15 mm axial), not in-situ
extraction against a fixed board.

## Q3 — Plan-view fan: FEASIBLE (at the passing height)

An order-preserving fan exists: 0 crossings, 0 wire–wire contacts, approach
tails straight continuations of the fan's end tangent at exactly the 1.25 mm
row pitch (pin 1 at the west end of every row). Construction that passes:
rotating frame over the **full ~48 mm run** from the Wing-exit drop to the
Main row (transverse direction rotates 43° to rowdir; pitch profile
1.30 → ~1.80 mid-fan → 1.25) **plus a two-level profile** — alternate wires
ride +1.15 mm in Z mid-fan, fading in/out so both plug rows stay planar.

What is genuinely different vs #248: (1) **no rise at the Main end** — both
rows live in the tray plane; the #242/#248 binding (14 conductors/side rising
through the Wing PCB plane to Main's top face) is gone; (2) endpoints
coplanar, so the turn is plan-only and can use the whole run length; (3) the
5.15 mm tray gap at 12.95 admits the two-level fan. What is unchanged: the
heading still swings ~110° (south → SSW → SSE) while the spacing rotates
43°, so the perpendicular factor dips to ~0.6 and the turn-radius factor
scales inner spacing by ~(R−d)/R — across 10 route iterations, every planar
single-level construction squeezed the inside pairs to ~0.6 mm < OD 1.0
(best planar residual 0.44 mm³). The #248 round-8 approach-tail bound does
not apply: the tails here are parallel continuations, not convergences on a
rising bundle.

## Q5 — Comparison note: flipped-GH at 12.95 vs adopted FPC at 10.90

Facts only; the decision is the PO's.

| axis | flipped GH (this study) | adopted FPC (D-042/D-046) |
|---|---|---|
| plate height | **12.95** (minimum passing) | **10.90** |
| keytop (provisional, q=1.50) | 24.05 | 22.00 |
| link build | 28 hand-crimped discrete wires (14×2), AWG28, 56 crimp terminations (SSHL-002T-P0.2), 4 housings GHR-14V-S + 4 headers SM14B-GHS-TB; routed 75–87 mm of the ≤200 mm bound | stock Molex 152660149 FFC ×2, 5 folds on a printed jig (detents keyed to measured length), pre-fold lane acceptance ≤1.30 Ω/lane; no crimping |
| pin order | D-024 native k→k at both ends | FFC delivers k→15−k, absorbed in Main's footprint assignment |
| service | plugs extract horizontally (7.15 mm axial); audited route stores ≈0–2 mm in-corridor; service = board removal + hand-held extraction; up to ~113 mm build-length headroom for a storage loop (not audited) | ZIF actuators on the flipped Main face the tray — board lift required before (un)locking (Stage B record); FFC is a formed sheet in its channel |
| Wing board change | connector back to GH side-entry underside (SM14B-GHS-TB) — a Rev.4-style respin of the link site on the Rev.6 outline (the Rev.4 GH site itself was qualified, D-039) | none (Rev.6 as adopted) |
| Main board change | underside GH headers at the Rev.10 symmetric sites (new bottom-side footprint + fanout respin); keep-out/relocation of U4/C17/C27/C28 around the sites per Q2 | none (Rev.10 as adopted) |
| case change | plate 10.90 → 12.95 (+2.05) with dependent heights (bosses/standoffs); formed-FPC channel reverts to open tray; D-046 pocket unchanged | as adopted |
| unchanged either way | flipped-J4/USB residual (D-046) — USB in flipped pose needs its own study regardless of link type; EN0/EN1 swap under flip, firmware-absorbed | same |

## Limits

CAD-scope only (no physical bend-rating/tolerance certification). The plug
envelope and the flipped component bodies are bounding reservations; the
real GH plug is 4.35 mm tall (envelope reserves 4.85) and smaller in plan
than 21.76 × 8.15. The fan is an existence construction, not a manufacturing
route: a conversion stage would re-derive the dressed harness against the
respun boards. Junana keytop term q=1.50 remains unmeasured (both columns).
