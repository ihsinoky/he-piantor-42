# Issue #280 follow-up 2 — low-risk power source comparison

Study only. PO instruction (2026-11-18): **Li-ion batteries are to
be avoided; examine low-risk power sources.** The AA/AAA preference
(aa-sizing.md) is one expression of this safety requirement, not the
whole of it. Cobalt/NMC Li-ion and 1.5 V-regulated Li-ion AA
products (Li-ion inside) are OUT of scope. LiFePO4 is evaluated
with an explicit flag: **it is still a lithium chemistry** — it is
included because its thermal behaviour differs categorically from
NMC, and the PO judges whether that difference is enough.

## Model and conventions (unchanged from aa-sizing.md)

- Load: **4.65 Wh/day** battery energy at η=0.85 (typing 2 h
  continuous 1.42 W + desk idle 6 h bursts 0.143 W + away 16 h
  0.016 W). Week target 23.3 Wh. Typing-phase battery draw
  1.67 W → pack current = 1.67 / pack V.
- Converter: TPS63070, VIN run **2.0–16 V**, cold start **≥3.0 V**,
  UVLO ≈1.85 V falling (TI SLVSC58B).
- Use model: cells are **swapped and charged externally**; there is
  no in-device charging. This removes the entire in-device charge
  fault class (wrong profile, charge-while-hot) from every
  candidate; what remains is cell abuse in the external charger,
  in-device discharge abuse, leakage/venting, and storage.
- Case placements (aa-sizing §3): (a) south-margin pod, (b) central
  bay — rejected for all (antenna site), (c) under-case pod.
  Clear height ≈ cell Ø + 2 mm.
- Prices are spot observations (Amazon JP / named listings,
  2026-11-18 unless dated otherwise); yen/day assumes two rotating
  sets where a swap rhythm needs them, amortized over the *lesser*
  of rated cycle life and a 5-year calendar cap.

## Sources for the new numbers

| Quantity | Value used | Source |
|---|---|---|
| NiMH eneloop AA capacity / cycles | 1900 mAh min (IEC 61951-2, 0.2 C); maker claim up to ~2100 cycles (std), ~500 (pro) | Panasonic eneloop lineup/FAQ, via aa-sizing |
| NiZn AA capacity | **2500 mWh typ / 2250 mWh min** (≈1500 mAh @1.6 V), Ri ≤20 mΩ, charge 0.5–1 C to **1.9 V/cell** taper, dedicated charger | PKCELL AA NiZn product datasheet page; ANSMANN PIB 1322-0005 (1600 mAh / 2.5 Wh, same rating) |
| NiZn cycle life | rated **500+** (PKCELL, ANSMANN); independent long-term reports of individual cell death within ~1–2 y of light use | maker pages above; JP user long-term report (anecdotal, labelled as such) |
| LFP 14500 capacity | **600 mAh typ / 580 min @0.2 C → 1.92 Wh**, EOD 2.0 V, charge 3.65 V, ≥2000 cycles to 80% | Drypower IFR14500EC datasheet; Vapcell IFR14500 (650 mAh typ) |
| LFP 18650 capacity | **1800 mAh typ / 1750 min @0.2 C → 5.76 Wh**, >2000 cycles @100% DOD/1 C to >80% | Antbatt IFR18650-1800 datasheet; GPE IFR18650 table |
| LFP 32700 capacity | **6500 mAh @0.2–0.5 C → 20.8 Wh**, Ri ≤9 mΩ, 145–163 g, ≥2000 cycles @0.5 C to ≥80% | IFR32700 product specification (UL1642/IEC 61960 basis); Misenpower IFR32700 |
| LFP vs NMC abuse | LFP 21700: **no thermal runaway under nail penetration at any SOC, ≤132 °C**; NMC/NCA runaway at SOC ≥30%, up to 732/1220 °C; LFP no runaway on heating at SOC 0/30 up to 350 °C | Ohneseit et al., Karlsruhe Institute of Technology, *Batteries* 2023 (peer-reviewed) |
| Supercapacitor | Maxwell BCAP3000: 3000 F / 2.7 V, **3.04 Wh stored, 510 g, 6.0 Wh/kg**, Ø60.4 × 138 mm | Maxwell K2 series datasheet (via Mouser) |
| Alkaline AA | E91: ≈1990 mAh @250 mA; 4× usable 9.27 Wh → 1.99 d | Energizer E91 datasheet, via aa-sizing |

## 1. Master table

Runtime = usable Wh / 4.65 Wh/day, same model as aa-sizing.

| Candidate (config) | Wh/cell | Usable Wh | Runtime | Cycles | ¥/day | Electrical fit | Case fit |
|---|---|---|---|---|---|---|---|
| **NiMH AA ×3** | 2.28 | 6.50 | **1.40 d** | ~2100 claim | ≈¥3 | clean (§aa-1) | (c) +16.5 mm |
| **NiMH AA ×4** | 2.28 | 8.66 | **1.86 d** | ~2100 claim | ≈¥3 | clean | (c) +16.5 mm |
| NiMH AA ×4 pro | 2.94 | 11.17 | 2.40 d | ~500 claim | ≈¥6 | clean | (c) +16.5 mm |
| **NiZn AA ×2** | 2.25 | 4.50 | 0.97 d | 500 rated, less in practice | ≈¥9 | **cold-start ✓ (only 2-cell config that clears 3.0 V)** | (c) +16.5 mm |
| **NiZn AA ×3** | 2.25 | 6.75 | **1.45 d** | 500 rated, less in practice | ≈¥7 | clean with margin | (c) +16.5 mm |
| NiZn AA ×4 | 2.25 | 9.00 | 1.94 d | 500 rated, less in practice | ≈¥6 | clean | (c) +16.5 mm |
| **LFP 14500 ×1 (1S)** | 1.92 | 1.82 | 0.39 d | ≥2000 | — | runs, EOD at floor | (c) +16.5 mm |
| LFP 14500 ×4 (1S4P) | 1.92 | 7.30 | 1.57 d | ≥2000 | ≈¥4 | clean (cutoff 2.5 V) | (c) +16.5 mm |
| **LFP 18650 ×1** | 5.76 | 5.50 | 1.18 d | ≥2000 | ≈¥5 | clean | (c) +20.5 mm |
| LFP 18650 ×2 (1S2P) | 5.76 | 11.0 | 2.37 d | ≥2000 | ≈¥4 | clean | (c) +20.5 mm |
| **LFP 32700 ×1** | 20.8 | 19.8 | **4.26 d** | ≥2000 | ≈¥4 | clean | (c) **+34 mm**, 145–163 g |
| LFP 32700 ×2 | 20.8 | 39.6 | **8.5 d — week reached** | ≥2000 | ≈¥4 | clean | (c) +34 mm, ~0.3 kg of cells |
| Alkaline AA ×4 | — | 9.27 | 1.99 d | primary | **≈¥250** | clean | (c) +16.5 mm |
| Supercap (BCAP3000 bank) | 3.04 Wh/510 g | — | **dismissed, §6** | ~10⁶ | — | — | none (Ø60 mm) |

Yen/day basis: NiMH — 8 eneloop AA ≈¥3,000 + charger ≈¥2,000,
5-y cap → ≈¥2.7/d. NiZn — 8 Melasta-class cells ≈¥2,600 +
dedicated charger ≈¥2,500, at a *realistic* 300 cycles/set →
≈¥8.5/d (¥5/d at the rated 500). LFP — cells ≈¥500–2,400 ea +
LFP-profile charger ≈¥2,600, cycle life never binds before the
5-y cap → ≈¥4–5/d. Alkaline — ≈¥500 per 4-pack / 1.99 d.

## 2. NiMH AA — the reference (unchanged energy results)

- **Risk profile.** Aqueous KOH electrolyte, sealed recombinant
  construction. **No thermal-runaway mechanism** at this device's
  abuse envelope: no flammable solvent, no oxygen-releasing
  cathode. Abuse outcomes are venting (H₂ under gross external
  overcharge — the external smart charger with −ΔV/temperature
  termination is the mitigation, and it is mature, commodity
  technology) and, rarely, KOH seepage from a damaged or
  reverse-charged cell; KOH is corrosive to contacts/PCB but not a
  fire or toxicity event. Storage/transport: unrestricted (not
  dangerous goods). This is the lowest-risk rechargeable chemistry
  in the set, full stop.
- **Cycle life / charging.** Maker claim up to ~2100 cycles
  (standard eneloop, JIS conditions), ~500 for eneloop pro;
  calendar life (5–10 y) binds before cycle life at this swap
  rhythm. Any AA NiMH smart charger works — no special charger,
  no profile risk.
- **Electrical/case.** As aa-sizing: ×3 is the smallest robust
  configuration (fresh 4.35 V / EOD 3.0 V, whole curve in range);
  ×4 buys 1.86 d. Under-case pod (c) +16.5 mm; south pod (a) costs
  a +5.6 mm palm hump.

## 3. NiZn AA — higher voltage, weaker longevity, thinner supply

- **Energy/electrical.** 1.6 V nominal (fresh off charger ≈1.85 V,
  plateau ≈1.6 V, practical knee ≈1.2 V, maker EOD reference
  1.0 V), 2250 mWh min. The voltage is the one real win: **2 cells
  clear the 3.0 V cold start with margin (fresh ≈3.7 V, plateau
  3.2 V)** — the only 2-cell configuration in the study that does —
  and 3× gives 1.45 d with the whole curve ≥3.0 V at EOD. Low Ri
  (≤20 mΩ) shrugs off the 0.52 A typing draw.
- **Risk profile.** Aqueous KOH like NiMH; **no thermal runaway,
  no flammable solvent**. The chemistry's failure mode is not
  energetic: zinc dendrite growth eventually shorts the cell
  internally — the cell quietly dies (and can get warm on charge),
  it does not vent flame. Venting under abuse is H₂/steam class,
  same family as NiMH.
- **The honest weakness — cycle life.** Rated 500+ cycles by
  PKCELL/ANSMANN, but NiZn's dendrite/shape-change wear is the
  documented historical reason the chemistry stayed niche:
  independent long-term users report individual cells failing
  within 1–2 years of light service, and capacity spread between
  cells in a set grows with age (a series set is only as good as
  its weakest cell — and a weak cell in a 3S string gets
  reverse-stressed at end of discharge). Budget on ~300 effective
  cycles, not 500. PKCELL also warns against low-drain use
  (self-discharge + shallow cycling shorten life) — this device's
  deep daily cycling is actually the favourable regime, which is
  the one mitigating fact.
- **Charger.** **Dedicated NiZn charger is mandatory** (1.9 V/cell
  taper profile; a NiMH charger undercharges and a Li-ion charger
  would be destructive). Chargers exist (Melasta/PKCell bundled,
  ISDT C4-class smart chargers with a NiZn mode) but this is a
  second charger ecosystem in the house.
- **Availability scan (2026-11-18).** Amazon JP: Melasta NiZn AA
  8-pack (2600 mWh class, ASIN B082DXWN1M) in stock; Z-Power Cell
  USB-C-port NiZn AA 4-pack ¥1,639 (MAKERZ, sale price reported
  2026-10); PKCELL via import sellers. **Not stocked by JP
  electronics chains** (no NiZn at Akizuki/Yodobashi class
  retailers in this check) — supply is Amazon-marketplace-only.
  Mainstream-ness: ANSMANN (EU) legitimises the chemistry, but it
  has been "about to take off" for 15 years; 3-year buyability is
  plausible, not assured. That is a freedom-axis (PO priority 3)
  cost NiMH does not have.

## 4. LiFePO4 — ⚠ still a lithium chemistry (PO to judge)

**What the flag means precisely.** LFP's cathode (olivine
LiFePO₄) does not release oxygen on heating, which removes the
self-sustaining core of NMC thermal runaway. The peer-reviewed
abuse record (Ohneseit et al., KIT, *Batteries* 2023, commercial
21700s, identical protocols): **no thermal runaway under nail
penetration at any state of charge, peak ≤132 °C**, and no
runaway under heating at SOC 0/30 up to 350 °C — where NMC/NCA ran
away at every SOC ≥30% and peaked at 732/1220 °C. Runaway onset
for LFP is ~270 °C class vs ~210 °C for NMC (FPA figures).
**What it does not forgive:** the electrolyte is still a flammable
organic solvent — a crushed *and* overcharged cell can vent
flammable gas (incl. HF) and burn, just without the cathode-fed
explosion; over-discharge below ~2.0 V permanently damages the
cell (and makes recharge hazardous); charging below 0 °C plates
metallic lithium; and charging on a 4.2 V Li-ion profile (wrong
external charger) overcharges it — the external charger must have
a true 3.65 V LFP profile. Transport/storage: still UN38.3
lithium rules for shipping; store at partial charge. In short:
categorically milder than NMC, categorically **not** in the
aqueous chemistries' risk class.

- **14500 (AA form, 3.2 V — its own configuration, NOT a 1.5 V
  drop-in).** 1.92 Wh/cell is barely above NiZn per cell, and the
  voltage forces 1S-parallel thinking: ×1 = 0.39 d (a non-starter),
  ×4 parallel = 1.57 d — NiMH ×3 class runtime for lithium
  handling plus the worst human-factors trap in the study: a
  3.2 V cell in an AA slot invites fatal mix-ups (a 14500 placed
  in a 1.5 V device destroys it; the keyboard's parallel holder
  would need keying/labelling as designed rework). No material
  win; not recommended.
- **18650.** 5.76 Wh/cell: ×1 = 1.18 d, ×2 parallel = 2.37 d
  (eneloop-pro class) at +20.5 mm pod height. A real configuration
  but no step change, and JP retail supply of *LFP* 18650 (as
  opposed to NMC 18650, which is everywhere and OUT of scope) is
  the thinnest of the three LFP forms.
- **32700.** The only step change in the study: **20.8 Wh in one
  cell → 4.26 d; ×2 → 8.5 d, the first configuration anywhere in
  Issue #280 that reaches the week.** ≥2000 cycles, ≤9 mΩ, and at
  this device's 0.08 C draw it delivers full datasheet capacity.
  The costs are physical and categorical: Ø32 × 70 mm, 145–163 g
  per cell, under-case pod grows to **+34 mm** — the keyboard sits
  on a brick — and it is unambiguously a lithium cell, i.e. it
  asks the PO to read "avoid Li-ion" as "avoid cobalt/NMC
  Li-ion". Availability: solar-DIY demand keeps 32700 plentiful
  (Amazon JP marketplace sellers stock it; regional platforms move
  tens of thousands/month), and LFP as a chemistry is becoming
  *more* mainstream in JP (Elecom's 2026 LFP power-bank line) —
  the 3-year outlook is good.

## 5. Alkaline AA primary — benchmark and emergency fallback

Energy is fine (×4 = 1.99 d, clean electricals) and fire risk is
nil, but two numbers disqualify it as the primary source:
**≈¥250/day** (≈¥7,500/month of consumables — two orders above
every rechargeable) and its main hazard, **KOH electrolyte
leakage**: alkaline cells left installed — especially deeply
discharged, warm, or aged — leak corrosive electrolyte that eats
contacts and PCB traces; manufacturer guidance is to remove cells
from devices in storage. In a device that deep-cycles a set every
2 days the leak exposure per set is short, but a forgotten spent
set left in the pod is exactly the leak scenario, and the damage
lands on the keyboard. Verdict: keep as the emergency/benchmark
column, not a design choice.

## 6. Supercapacitor / hybrid — dismissed by arithmetic

Maxwell BCAP3000 (the largest mainstream EDLC cell): 3.04 Wh
stored in 510 g (6.0 Wh/kg), Ø60.4 × 138 mm. One day of this
device (4.65 Wh) needs ≈2 cells ≈ **1.02 kg of capacitors, each
wider than the keyboard is thick** — before self-discharge
(leakage ~mA class per cell; a charged bank sheds a meaningful
fraction of a day's energy per day of sitting) is even counted.
A hybrid cap+cell buys nothing: the load is not pulse-limited
(NiMH/LFP internal resistance is already ≪ the 0.5 A typing draw),
so the cap adds mass, volume and a balancing problem to solve a
problem the cells do not have. **Dismissed.**

NiCd, for completeness: dismissed in one line — cadmium toxicity
(RoHS-restricted); no property it offers is unavailable elsewhere.
