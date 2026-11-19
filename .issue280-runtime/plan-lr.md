# Issue #280 follow-up 2 — low-risk power source comparison (plan)

Study only. PO instruction (2026-11-18): **Li-ion avoided; examine
low-risk power sources.** AA/AAA preference is one expression of the
safety requirement, not the whole of it. Cobalt/NMC Li-ion and
1.5 V-regulated Li-ion AA products are OUT. LiFePO4 is IN with an
explicit "still a lithium chemistry" flag for the PO to judge.

## Basis numbers (from aa-sizing.md — do not re-derive silently)

- Load model: **4.65 Wh/day** battery energy at η=0.85 (typing 2 h
  continuous 1.42 W + desk idle 6 h bursts 0.143 W + away 16 h
  0.016 W). 1 week = 23.3 Wh, 1 month ≈ 140 Wh.
- Converter: TPS63070, VIN run **2.0–16 V**, cold start **≥3.0 V**,
  UVLO ≈1.85 V falling.
- Case: under-board void 3.10 mm spent. Placements: (a) south-margin
  pod (AAA +2 mm palm hump / AA +5.6 mm), (b) central bay (rejected:
  spends antenna site), (c) under-case pod (+12.5 mm AAA /
  +16.5 mm AA underneath). Cell clear height ≈ Ø + 2 mm.
- Design intent: cells swapped, charged externally (no in-device
  charging) — state per candidate how that changes its risk.

## Candidates

1. NiMH AA — reference (reuse aa-sizing); add risk profile, cycle
   life, charging notes.
2. NiZn AA (1.6 V class) — Wh from datasheet-class sources, honest
   cycle life, dedicated charger need, 2-cell cold-start benefit,
   availability scan.
3. LiFePO4 — (a) 14500 (3.2 V, own configuration), (b) 18650,
   (c) 32700. Wh, discharge vs converter range, cycle life, case
   fit (Ø 14.5 / 18 / 32 mm), availability scan, precise thermal
   profile vs NMC + what abuse it still does not forgive.
4. Alkaline AA primary — reference (reuse); leakage as main hazard,
   consumable yen/day at computed runtimes.
5. Supercapacitor / hybrid cap+cell — one energy-density calculation
   vs 4.65 Wh/day decides.
6. NiCd — one-line dismissal (cadmium toxicity) if mentioned.

## Evaluation axes (per candidate)

- Risk: thermal runaway (yes/no + conditions), venting/leakage and
  what it damages, charging risk (under the external-charging
  model), storage/transport.
- Energy: Wh/cell, Wh/configuration, days vs the 4.65 Wh/day model;
  cycle life; **yen/day** (alkaline consumable vs rechargeable
  amortized incl. charger) — PO priority 1 = cost.
- Electrical: fresh/end voltage vs 2.0–16 V range + 3.0 V cold
  start; robust cell count.
- Case: placement (a)/(c)/none + added height for the diameter.
- Availability scan (workflow rule 2026-11-18): exact SKU stock at
  2+ distributors with dates; mainstream-ness in ~3 years; special
  charger availability (NiZn).

## Sources discipline

Capacities/voltages: manufacturer datasheets or named distributor
listings, discharge rate stated. Safety claims: manufacturer safety
docs, IEC/UL standard scope, or institutional summaries — never
marketing copy. Runtimes recomputed against the SAME model; any
model change stated explicitly.

## Verdict shape

Rank under: safety (PO's first criterion here) → cost > low rework >
freedom. Recommended configuration + runner-up, each with its
single biggest weakness. If nothing beats NiMH AA ×3–4 materially,
say so plainly.
