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
