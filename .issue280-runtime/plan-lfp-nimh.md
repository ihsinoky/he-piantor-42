# Issue #280 follow-up 3 — plan: LiFePO4 vs NiMH practical deep-dive

PO narrowed the field to TWO finalists — **LiFePO4 and NiMH** — and
asked three concrete axes: 入手性 (availability), 価格 (price),
充電環境 (charging environment). Concrete product level, buyer in
Japan. Study only; no purchase recommendation (PO gate).

## Basis numbers (from prior studies, not re-derived)

- Load model: 4.65 Wh/day; week target 23.3 Wh (aa-sizing.md).
- NiMH AA ×4: 8.66 Wh usable → 1.86 d; eneloop std 1900 mAh min,
  maker claim ~2100 cycles, calendar life binds first.
- LFP 32700 ×1: 20.8 Wh/cell → 4.26 d; ×2 → 8.5 d (week reached).
  ≥2000 cycles @0.5C, Ri ≤9 mΩ, Ø32×~70 mm, 145–163 g.
- LFP 18650 2P: 2.37 d; LFP 14500 4P: 1.57 d (dominated; one line
  each in this study).
- Prior ¥/day: NiMH ≈¥3, LFP ≈¥4–5 (spot observations 2026-11-18,
  low-risk-power.md §1). This study re-derives with dated,
  retailer-named observations and a 3-year ownership model.
- Converter: TPS63070 VIN 2.0–16 V, cold start ≥3.0 V (not the
  subject here, but rotation configs are defined against it).

## Configurations under study

- NiMH AA ×4 in use + ×4 charging = **8 cells** rotation (eneloop
  standard class; eneloop pro noted as a variant line).
- LFP 32700 ×2 in use (week config) + rotation → **2–4 cells**
  (×2 in use + ×2 spare/charging = 4; also state the 2-cell
  minimum viable rotation).
- One availability/price line each: LFP 18650, LFP 14500.

## Axis 1 — Availability (observed, dated, exact SKU, 2+ channels)

- NiMH: Panasonic eneloop SKUs at Amazon JP, ヨドバシ, モノタロウ,
  秋月電子 as applicable; product-line age (eneloop since 2005),
  3+ year supply outlook.
- LFP 32700: identifiable-brand cells only (name the brands /
  manufacturer stores actually reachable: e.g. Vapcell-class,
  solar-DIY brands); ANY domestic (JP) distributor?; counterfeit /
  inflated-capacity exposure on marketplace generics; how a buyer
  verifies capacity (test charger / discharge test).
- LFP 18650 / 14500: one line each.
- Rule: exact SKU, ≥2 channels, observation date on every figure;
  unreadable page → UNVERIFIED, never silently estimated.

## Axis 2 — Price (JPY, observed)

- Cell unit price × rotation set size (NiMH 8; LFP 32700 2 and 4).
- Charger price (from Axis 3 picks).
- 3-year cost of ownership at the swap rhythms: NiMH swap every
  1.86 d → ~590 swaps/3 y (calendar-bound, likely 1 set of 8 lasts
  the period — verify against cycle/calendar claims); LFP 32700
  ×2 swap every 8.5 d → ~130 swaps/3 y, cycles never bind.
- Electricity cost: compute once, show it is negligible (¥ class).
- Reconcile with prior ¥/day (≈¥3 NiMH / ≈¥4–5 LFP); explain moves.

## Axis 3 — Charging environment

- NiMH: mainstream smart chargers (Panasonic BQ-CC class and
  equivalents), charge time for a 4-cell set at maker-stated
  currents, whether one charger comfortably serves a 1.86 d rhythm.
- LFP — the critical checks:
  (a) True LFP mode = 3.6–3.65 V termination. What a 4.2 V Li-ion
      profile does to an LFP cell; how real the household
      wrong-charger risk is (charger count in house, mode
      persistence / auto-detect behaviour of candidate chargers).
  (b) Physical FIT of 32700 (Ø32 × ~70 mm) + LFP mode in named
      chargers — verify against MANUFACTURER spec pages (XTAR,
      Nitecore lines; slot max diameter/length, per-slot current).
  (c) Charge time for a ~6000–6500 mAh 32700 at the real per-slot
      current of the fitting chargers.
  (d) Storage practice: LFP storage charge (~40–60% SOC) vs NiMH
      LSD shelf behaviour.
- One charger for BOTH finalists? (universal smart chargers with
  NiMH + LFP modes and 32700-capable slots — verify or refute.)

## Deliverable

`.issue280-runtime/lfp-nimh-practical.md` + `.json`: three sections
matching the axes, side-by-side summary table, closing practical
verdict (which finalist is easier to LIVE with; what each route
demands that the other does not). Checkpoint commits per part.
