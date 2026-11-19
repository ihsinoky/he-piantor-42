# Issue #280 follow-up 3 — LiFePO4 vs NiMH: availability, price, charging environment

Study only. PO narrowed the field to **LiFePO4 and NiMH** and asked
three concrete axes: 入手性 (availability), 価格 (price), 充電環境
(charging environment). Concrete products, buyer in Japan.
**No purchase recommendation — purchase is a PO gate.**

All prices/stock below are **observed** on the retailer or
manufacturer page named, on **2026-11-18** (crawl timestamps as
noted), unless a different date is printed. Anything not observed
is marked UNVERIFIED. Basis (not re-derived): load 4.65 Wh/day;
NiMH AA ×4 runtime 1.86 d at the prior study's 1900 mAh basis —
**refreshed to ≈1.96 d** below because the current eneloop
generation is 2000 mAh min; LFP 32700 ×1 4.26 d / ×2 8.5 d;
LFP 18650 2P 2.37 d; LFP 14500 4P 1.57 d (low-risk-power.md).

## 1. Availability（入手性）

### NiMH — Panasonic eneloop AA (BK-3MCD, current generation)

- **Exact SKUs observed in stock:** BK-3MCDK/4H (4-pack) and
  BK-3MCDK/8H (8-pack) at ヨドバシ.com (在庫あり, free delivery);
  BK-3MCD/4H tracked by 価格.com across 17–18 shops, lowest
  ¥1,551, price trend ¥1,700 on 2026-11-14 (Sound House).
  Charger sets K-KJ83MCD40 / K-KJ85MCD40 listed at ヨドバシ
  (K-KJ85MCD40 在庫残少 at crawl). Rakuten carries the previous
  BK-3MCC generation (¥1,560, RoomClip/Rakuten). Amazon.co.jp
  sells the line (incl. an Amazon-limited BK-3MCC/4SA pack) —
  its live price was **not separately observed** in this pass
  (価格.com excludes Amazon from its index); the two-channel
  rule is met by ヨドバシ + 価格.com shops + Rakuten.
- **Current-generation refresh:** BK-3MCD (launched 2023-04-25)
  is **min. 2000 mAh** (up from BK-3MCC's 1900), and Panasonic's
  cycle claim on the current JIS C8708:2019 basis is **≈600
  cycles** (アズワン spec listing) — not the ~2100 of the older
  JIS basis used in earlier studies. Runtime at 2000 mAh:
  ×4 usable ≈9.12 Wh → **≈1.96 d** (was 1.86 d).
- **Supply stability:** eneloop has been sold continuously since
  2005 (Sanyo → Panasonic); in 2023 Panasonic consolidated its
  NiMH rechargeables under the eneloop name. Every JP
  electronics chain stocks it. 3+ year supply is as close to
  certain as a consumer product gets. No transport restrictions
  (not dangerous goods) — any channel, any quantity, forever.

### LFP 32700 — the honest picture

- **No domestic JP distributor for bare cells was found.**
  秋月電子 stocks no bare LFP cylindrical cells (search of its
  catalogue surfaced modules/parts only; consistent with the
  follow-up 2 check). モノタロウ sells *finished* LFP products
  (e.g. AZ Battery motorcycle packs with BMS), not bare 32700
  cells. ヨドバシ/家電量販 do not list bare LFP cells at all.
- **What a JP buyer actually does:** (i) Amazon.co.jp
  *marketplace import sellers* — listings exist (a generic
  3.2 V 6000 mAh 32700 listing mirrored by desertcart.jp at
  **¥8,609**, in stock 2026-11-18; the page did not state the
  pack count, so the per-cell price is **UNVERIFIED** — the
  listing is evidence that JP-reachable marketplace pricing is
  opaque and inflated, not a usable unit price); (ii)
  **AliExpress brand stores** — the identifiable-brand route:
  **LiitoKala** (Lii-70A 32700) and **Vapcell** (Shenzhen
  Vapcell Technology, its own store) are the two brands with
  recognisable storefronts and test/review coverage;
  **Misenpower** publishes full datasheets (6000 mAh and
  6500 mAh IFR32700 variants, Ø32.2±0.3 × 70.5±0.3 mm,
  ≥2000–2200 cycles) but sells B2B/direct, not JP retail.
- **Counterfeit / capacity-fraud exposure — the real cost of
  this channel.** The same 32×70 mm can is sold claiming
  6000, 6500 and **7000 mAh** (LiitoKala Lii-70A). Every
  manufacturer datasheet found tops out at **6500 mAh**
  (Misenpower IFR32700; A&S Power 6500 typ / 6450 min).
  Claims above 6500 mAh exceed the format's datasheet class
  and should be read as marketing. Anonymous marketplace
  generics add the standard risks: rewrapped B-grade or
  recycled cells, no lot traceability. Mitigations that
  actually work: buy only from the brand's own store; treat
  ≥7000 mAh claims as fiction and price against 6000;
  **discharge-test every cell on arrival** (the charger in §3
  does this) and reject/return cells >5% under claim.
- **Supply stability:** 32700 is a multi-factory industrial /
  solar-DIY commodity format — no single line to discontinue,
  and solar-storage demand keeps volume high (Alibaba
  wholesale $1.35–2.30/cell at MOQ 100, Vapcell store). But no
  brand commits to a JP retail channel, and loose lithium
  cells move under UN38.3 / carrier rules — the AliExpress
  route works today and is exactly the kind of channel that
  can tighten. 3-year buyability: plausible, not assured;
  per-order quality risk persists even when availability does.

### One line each — the dominated LFP forms

- **LFP 18650 (2P, 2.37 d):** buyable via AliExpress brand
  stores (Vapcell/PKCell IFR18650 1800 mAh; wholesale
  $0.6–1.2/cell, retail landed a few hundred ¥/cell; a JP
  hobbyist observed ≈¥700/cell in 2026-08, secondary source);
  no JP domestic retail; its one plus is fitting ordinary
  chargers — still dominated on runtime.
- **LFP 14500 (4P, 1.57 d):** solar-light replacement channel
  (AliExpress ~$0.4–1/cell wholesale; Amazon JP marketplace
  packs); the AA-form 3.2 V mix-up hazard from follow-up 2
  stands; dominated.

## 2. Price（価格）— observed, and a 3-year cost of ownership

### Observed unit prices (2026-11-18 unless dated)

| Item | Observed price | Where |
|---|---|---|
| eneloop AA BK-3MCDK/4H (4 cells) | **¥1,720** (8-pack BK-3MCDK/8H ¥3,350) | ヨドバシ.com, in stock |
| eneloop AA BK-3MCD/4H (4 cells) | ¥1,551 lowest / ¥1,700 trend 2026-11-14 | 価格.com (17–18 shops) |
| Panasonic reference price, BK-3MCD/4H | ¥2,430 | Panasonic site via secondary report (2026-10) |
| K-KJ85MCD40 (BQ-CC85 + 4 cells) | **¥3,710** | ヨドバシ.com |
| K-KJ83MCD40 (BQ-CC83 + 4 cells) | **¥2,550** | ヨドバシ.com |
| LFP 32700 branded (LiitoKala Lii-70A, 4 pcs) | £23.58 ≈ **¥4,700** (≈¥1,175/cell) | eBay listing via PicClick (crawl 2026-11) |
| LFP 32700 branded (LiitoKala 6500 mAh, 6 pcs) | €92.88 ≈ ¥15,000 (EU retail — outlier) | Klarna price comparison |
| LFP 32700 generic, Amazon-sourced | ¥8,609, **pack count UNVERIFIED** | desertcart.jp |
| XTAR VX4 charger | **¥5,519** (2026-11-12 Amazon調べ) / ¥6,780 | Amazon.co.jp via VOLTECHNO tracker / 楽天市場 |

Planning figure for branded 32700 landed in JP: **≈¥1,000–
1,500/cell** (AliExpress brand store, eBay anchor). Anyone
quoting far below that is quoting wholesale MOQ-100 pricing
or an anonymous generic — see the fraud note in §1.

### Rotation baskets and 3-year ownership

Swap rhythms: NiMH ×4 set every ≈1.96 d → each 4-cell set is
cycled ≈280 times in 3 years (two sets alternating). LFP
32700 ×2 pair every 8.5 d → ≈130 cycles per pair in 3 years.
Electricity: 4.65 Wh/day × 365 × 3 y ≈ 5.1 kWh at the cells,
≈6.8 kWh at the wall at ~75% end-to-end efficiency → **≈¥210
over 3 years** at ¥31/kWh. Negligible for both; stated once,
not carried per-row.

| Route | Initial basket | Replacements in 3 y | 3-y total | ¥/day (3 y) | ¥/day (5 y) |
|---|---|---|---|---|---|
| NiMH, BQ-CC85 set + 4 extra cells (8 total) | ¥3,710 + ¥1,720 = **¥5,430** | none — ≈280 cycles vs ≈600 rating (JIS C8708:2019); calendar life is the limit and exceeds 3 y | **≈¥5,640** | **≈¥5.2** | ≈¥3.2 |
| NiMH, budget: BQ-CC83 set + 4 extra | ¥2,550 + ¥1,720 = ¥4,270 | none (same basis) | ≈¥4,480 | ≈¥4.1 | ≈¥2.6 |
| LFP 32700 ×4 (2 in use + 2 spare) + VX4 | ≈¥4,800 cells + ¥5,519 = **≈¥10,300** | none — ≈130 cycles vs ≥2000 | **≈¥10,500** | **≈¥9.6** | ≈¥5.9 |
| LFP 32700 ×2 minimum (×1 in use 4.26 d + 1 spare) + VX4 | ≈¥2,400 + ¥5,519 = ≈¥7,900 | none | ≈¥8,100 | ≈¥7.4 | ≈¥4.6 |

**Reconciliation with the earlier ≈¥3 (NiMH) / ≈¥4–5 (LFP)
per day:** those figures amortised over the 5-year calendar
cap. On the 3-year window this study was asked for, NiMH is
≈¥5/day and LFP ≈¥10/day (4-cell) — and the LFP figure also
moves because follow-up 2 assumed a ≈¥2,600 LFP charger.
**No charger at JP retail that both fits a 32700 and has a
true LFP mode exists at that price** — the real floor is the
XTAR VX4 at ¥5,519 (§3). The charger, not the cells, is the
LFP route's price problem. In absolute terms both routes are
cheap; the 3-year gap is ≈¥5,000, roughly the price of the
VX4 itself.

## 3. Charging environment（充電環境）

### NiMH — commodity, zero-drama

- **Panasonic BQ-CC85** (manufacturer spec page, panasonic.jp):
  AA/AAA NiMH only, 1–4 cells, per-cell sensing charge with
  −ΔV/temperature termination. Charge time, eneloop standard
  AA: **×2 ≈1.5 h, ×4 ≈3 h**. The BQ-CC83 (in the ¥2,550 set)
  is the slow sibling: ×4 ≈7 h class.
- **Does one charger serve the rhythm?** Trivially. The in-use
  set runs ≈1.96 days; the spare set charges in 3 h (or 7 h).
  There is no schedule pressure at all — charge whenever, the
  charged set then waits on the shelf (see storage below).
- **Profile risk: none.** A BQ-CC charger physically accepts
  only AA/AAA and only speaks NiMH. Any smart NiMH charger
  from any maker works. There is no mode to forget and no
  wrong charger in the house that fits these cells and harms
  them. This is the baseline the LFP route is measured
  against.

### LFP — one true profile, one fitting problem, both solvable

**(a) The 3.65 V rule and the wrong-charger risk.** LFP charges
CC/CV to **3.60–3.65 V**. A plain 4.2 V Li-ion profile
overcharges it by ~0.55 V: XTAR's own product text warns an
LFP cell in Standard mode "may be recognized as a 3.6 V
lithium battery, which can cause overcharging and damage to
the battery" — sustained 4.2 V charging oxidises electrolyte,
gases the cell, fades capacity fast, and spends exactly the
safety margin that justified choosing LFP (follow-up 2, §4).
How real is the risk in a household? The exposure is (i) a
universal charger left in Standard mode, and (ii) any *other*
4.2 V-only cylindrical charger in the house (flashlight
18650 chargers are the classic case). It is a human-factors
risk, not an equipment-availability risk, and it is
mitigable: the VX4 **V2** has charging-mode memory (retains
Standard/LiFePO4 mode across power loss — xtar.cc), so a
dedicated LFP charger stays in LFP mode. The discipline
required is real but small: one charger, labelled, always in
LFP mode; never borrow the 4.2 V charger.

**(b) Which chargers physically fit a 32700 AND have LFP
mode — verified against manufacturer specs.**
- **XTAR VX4 / VX4 V2 — FITS, with a diameter caveat.** XTAR
  product copy lists 32700 for **slots 1 and 4 only**, under
  the general rule "not thicker than 32 mm and not longer
  than 83 mm"; LFP cutoff 3.65±0.05 V; currents 3 A×1 /
  2 A×2 / 1 A×4 (xtar.cc spec table; XTAR distributor copy).
  Caveat: the reference 32700 cell is **Ø32.2±0.3 mm**
  (Misenpower datasheet) — 0.2 mm *over* the stated 32 mm
  limit at nominal. Length (70.5 mm) is fine. Expect a snug
  fit in the outer slots; wrapper strain is possible and a
  fatter-than-datasheet cell may not seat. This must be
  test-fitted with the actual cells before the route is
  committed — it is the single physical unknown in this
  study.
- **XTAR VX2 Pro — FITS on paper, 2 slots.** Manufacturer
  spec: diameter 10–32 mm, length 34–80 mm, 32700 explicitly
  listed; LFP cutoff 3.65±0.05 V; LFP requires manual
  chemistry selection; currents to 3 A×1 / 2 A×2. Same
  32 mm diameter caveat. Two slots is exactly what the
  ×2-pair rotation needs.
- **Nitecore UMS4 — does NOT fit.** Nitecore's official
  compatibility list for its flagship 4-slot charger ends at
  **26700** (LiFePO4 supported, manual voltage selection);
  32700 is not listed. The Nitecore line is out for this
  cell size.
- LiitoKala Lii-S8/S12 advertise a 3.65 V LiFePO4 output,
  but their published size lists also cap at 26650 — out on
  fit, and the S12's JP marketplace price (¥11,284, Qoo10)
  is above the VX4 anyway.

**(c) Charge time for a 6000–6500 mAh 32700.** On the VX4,
two cells (slots 1+4) at 2 A each: CC phase ≈3.3 h + CV
tail → **≈3.5–4 h for the pair**; a single cell at 3 A:
≈2.5–3 h. Against an 8.5-day pair runtime this is a
non-constraint — but note the rotation arithmetic: with
only 2 cells total in the ×2 configuration the keyboard is
*down* during charging, so **4 cells is the real minimum
for the week configuration**; 2 cells suffice only for the
×1 configuration (4.26 d, 1 in use + 1 spare).

**(d) Storage practice.** LFP spares should sit at partial
charge (~40–60% SOC, ≈3.2–3.3 V); stored full, calendar fade
accelerates; self-discharge is low (<3%/month class, cell
datasheets). The VX2 Pro has a dedicated **Store** operation
that brings cells to storage voltage; on the VX4 you stop a
charge early or use its discharge-test function. NiMH is
the opposite lifestyle: eneloop's low self-discharge keeps
**≈85–90% after 1 year on the shelf** (Panasonic claims), so
the spare set sits *fully charged and ready* for a year with
no management at all. Practical consequence: the NiMH
"charged spare" is grab-and-go; the LFP spare pair, kept
properly at storage charge, wants a top-up charge (hours)
before it goes into the keyboard — or you accept full-charge
storage and pay for it in calendar life.

### One charger for both finalists?

**Yes — the XTAR VX4 (or VX2 Pro) is that charger.** It
charges NiMH AA (VX4: fixed 0.5 A ×4, cutoff 1.45±0.1 V →
≈4–4.5 h for 4 cells, slower than the BQ-CC85's 3 h but
serviceable) and LFP 32700 (slots 1/4, LFP mode), and its
capacity-test function doubles as the arrival-inspection
tool §1 demands for marketplace cells. Caveats: LFP mode is
a charger-wide mode (NiMH charges normally in either mode;
3.7 V Li-ion and LFP cannot charge simultaneously — XTAR);
and if the household runs both finalists, the mode switch
becomes a per-session action rather than a set-and-forget —
which reintroduces exactly the human-factors risk of (a).
One chemistry per charger is the safer household rule; the
VX4 covering both is a fallback, not the plan.

## 4. Side-by-side summary

| Axis | NiMH (eneloop AA ×4) | LiFePO4 (32700 ×2) |
|---|---|---|
| Runtime per set | ≈1.96 d (2000 mAh gen) | 8.5 d — the week |
| Availability | Every JP channel, in stock, exact SKUs (BK-3MCDK/4H ¥1,720 ヨドバシ) | **No JP domestic distributor**; AliExpress brand stores / marketplace imports only |
| Cell identity risk | None — one maker, one SKU | Real — 6000/6500/7000 mAh claims for one can size; test-on-arrival required |
| Rotation basket | 8 cells ¥3,440 + charger set | 4 cells ≈¥4,800 + VX4 ¥5,519 |
| 3-year cost | **≈¥5,640 (≈¥5.2/day)** | **≈¥10,500 (≈¥9.6/day)** |
| Charger | Panasonic BQ-CC85, ¥3,710 with 4 cells; ×4 in ≈3 h | XTAR VX4, ¥5,519; pair in ≈3.5–4 h |
| Charger fit risk | None (AA is the charger's native size) | **Diameter borderline**: cell Ø32.2 vs charger 32 mm limit — test-fit required |
| Wrong-profile risk | None — NiMH-only charger, no modes | Real — 4.2 V profile damages LFP; mitigated by VX4 V2 mode memory + one-charger discipline |
| Spare-set storage | Charged, ready, ~85–90% after 1 y | Storage charge ~50%; top-up before use, or pay calendar life |
| Attention rhythm | Swap every ~2 days (30 s), charge whenever | Swap weekly, but cells/charger need managing |
| Supply in 3 years | Certain | Plausible (solar-DIY demand), channel can tighten (UN38.3) |

## 5. Practical verdict — living with each finalist

**NiMH is easier to live with, and it is not close on the
daily-experience axes.** Every part of the NiMH route is a
commodity bought from a domestic shelf, the charger cannot
be set wrong, the spare set waits a year at full charge, and
a dead cell in 2029 is replaced from any electronics store
in the country for ¥430. Its one real cost is rhythm: a
30-second swap every two days, forever. What NiMH demands
that LFP does not: *frequency of attention* — and nothing
else.

**LFP 32700 is the only route to the week, and everything
it asks for is paid once, up front, in exchange.** What the
LFP route demands that NiMH does not: (1) importing cells
through a channel with genuine capacity-fraud exposure,
plus a discharge test of every cell on arrival; (2) a
¥5,519 specialist charger whose 32 mm slot limit the cell's
own 32.2 mm diameter technically exceeds — a test-fit that
has to pass before the route is real; (3) permanent
mode discipline around 3.65 V vs 4.2 V in a house that may
contain other lithium chargers; (4) storage-charge
management of the spare pair. In exchange it removes the
swap rhythm almost entirely (weekly), and its cells will
out-cycle the keyboard. The 3-year money difference
(≈¥5,000) is the price of the charger, not the chemistry.

The deciding question for the PO is therefore not price or
availability in the abstract: it is whether **weekly swaps
are worth an imported, test-on-arrival cell supply and a
borderline charger fit** — or whether a two-day swap rhythm
on fully domestic, zero-discipline hardware is the better
life. Both finalists remain technically sound; neither
needs the other finalist's charger if the household rule is
one chemistry per charger.

*Study only. No purchase is recommended or authorised here;
purchase is a PO gate.*
