# Issue #282 — TMAG5253 vs DRV5055A3 formal comparison — PLAN

Study only. No board/case changes, no orders.

## Comparison axes (deliverable: tmag-comparison.md + .json)

1. **Datasheet table** — supply range, active current (with its VCC), shutdown,
   power-on time, per-variant sensitivity/range (ratiometric scaling stated),
   sensitivity error, tempco/drift, output noise (+ conversion to travel
   resolution), bandwidth, output swing limits, package/assembly.
2. **Field compatibility** — flux swing the current design presents across
   travel (or DRV5055 output swing actually used, field derived from it);
   per-variant PASS/FAIL with margin; TMAG output swing @3.3V; effective
   (noise-limited) travel resolution vs DRV5055 baseline.
3. **Architecture impact** — (a) 3.3V Hall rail vs D-026/D-027 guarantee
   structure; (b) TMUX1208 @3.3V (range, Ron, settling); (c) RP2040 ADC
   interface both sensors; (d) EN control options (ganged / per-group /
   per-sensor) — routing+GPIO cost, energy difference.
4. **Revised power model** — aa-sizing profile UNCHANGED; burst window
   re-derived (sensor power-on + MUX settling + ADC conversion, each term
   sourced); Wh/day, NiMH AA×4 runtime, typing duty/period for 7 days
   (or shortfall). Side-by-side vs DRV5055 model.
5. **Availability scan** — exact orderables for passing variants: LCSC/JLCPCB
   + DigiKey/Mouser stock & price, observed & dated; assembly class;
   DRV5055A3 C266128 reference line.
6. **Verdict** — wireless-variant design input adopt/reject/conditional;
   bearing on wired design (expected none); Wing respin scope if changed.

## Basis numbers — sources

| Number | Source |
|---|---|
| Usage profile, pack energy 8.65 Wh, DRV model 4.65 Wh/day | sibling `.issue280-runtime/aa-sizing.md` |
| DRV5055 tON basis, burst analysis, recorded loads | sibling `.issue280-runtime/hw-implications.md` |
| Wing scheme, 5V guarantees | repo `docs/decisions.md` D-024/D-026/D-027 |
| Field / sensitivity / reservation numbers | repo docs + findings (#255/#263 work) — search |
| TMAG5253 electricals | TI SBASAI5 (verify PMO spot-check) |
| DRV5055A3 electricals | TI SBAS640 |
| TMUX1208 @3.3V | TI SCDS387 (datasheet) |
| TMAG5253 use in he_kbd_module | gh api ihsinoky/he_kbd_module (background) |

## Invariants
- Every electrical number traces to a named datasheet (doc+rev) or repo record (file+section). No blog/forum figures.
- First matching variant is distrusted: check swing at BOTH travel ends + noise vs current resolution.
- Revised model reuses aa-sizing profile verbatim; arithmetic shown; models differ ONLY in sensor/architecture inputs.
