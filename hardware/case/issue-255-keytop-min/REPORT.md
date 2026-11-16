# Issue #255 — Keytop height minimisation

PO objective (2026-11-16): minimise the KEYTOP height with all qualification
gates kept. This supersedes the fixed Z13.55 plate target of Issue #248.

Keytop = plate top + 9.60 (Jade Pro unpressed stem tip above plate, datasheet)
+ q (Junana MX cap term). **q is UNMEASURED** — assumed 1.50, sensitivity
0.50–2.50 (Issue #248 Phase A). Every absolute keytop figure in this report is
provisional on q; the minimisation itself is over the stack below the cap,
which does not depend on q.

References: GH baseline plate 13.55 → keytop 24.65 (q=1.50). Δ+6 (D-041):
plate 22.20 → keytop 33.30.

---

# Stage 1 — Stack decomposition and bound-by-bound attack

## 1.1 Decomposition (every term verified against CAD/data sources)

Let B = Wing PCB underside Z; F = tray floor top Z. Plate top = B + 6.20.

| # | Term | Value (mm) | Source / verification | Owner of the bound |
|---|---|---:|---|---|
| 1 | Case floor slab (Z0 → floor top) | 2.00 (F=2.00) | #232/#248 case build; sockets 0.80 deep leave 1.20 below | case print |
| 2 | Connector mated envelope (GH SM14B-GHS-TB + GHR-14V-S) | 4.35 | JST reference dimension; dimensioned mated model in #248 REPORT-B1 | connector |
| 3 | Assembly allowance on connector | 0.50 | inherited engineering budget — explicitly NOT a JST-certified maximum (#248 Phase A) | project budget |
| 4 | Free gap, connector reservation bottom → floor top | 0.50 | #248 Phase A (retained there) | project budget |
| 5 | Hall-sensor underside reservation | 3.40 deep | #232 `build.py`: reservation **cube** 3.4×3.4×3.4. Physical DRV5055A3 (repo JITX model from TI outline 4214838/F): SOT-23 body height **1.12**, seated protrusion ≈1.27, +solder ≈1.35 → ~2.0 of the reservation is protective air | reservation policy |
| 6 | MUX + solder envelope | 1.40 (+0.50 gap) | #232 `build.py` envelope (5.1×6.6×1.4) | component |
| 7 | Capacitor envelope | 1.00 (+0.50 gap) | #232 `build.py` envelope (2.4×1.6×1.0) | component |
| 8 | M2 tie / boss root (M2×12) | engagement 5.50 below B, ≥1.20 material below tip → B ≥ 6.70 | #248 Phase A stack: 0.30 washer + 1.50 plate + 3.50 spacer + 1.20 PCB = 6.50; 12 − 6.50 = 5.50 | fastening |
| 9 | Wing PCB | 1.20 | D-021; Jade Pro ratings are quoted at PCB 1.2 mm | board |
| 10 | POM spacer | 3.50 | see §1.2 — invariant | switch seat |
| 11 | Aluminium plate (5052-H32) | 1.50 (finished 1.45–1.51) | D-038; Jade Pro datasheet thickness window | switch seat |
| 12 | Stem tip above plate top | +9.60 | Jade Pro datasheet (repo `jade-pro.pdf` p.7, per #248 Phase A primary read): housing top = PCB top +11.10, stem extension TT 3.50, PCB-top→plate-top 5.00 → 11.10 − 5.00 + 3.50 = 9.60 | switch |
| 13 | Cap term q | 1.50 assumed (0.50–2.50) | UNMEASURED — Junana MX publishes no installed height (#248 Phase A) | cap (PO-side measurement) |

Plate-top bounds at F=2.00 (re-verified, matching #248 Phase A):
**GH 13.55 (binding)** · M2 tie (×12) 12.90 · Hall 12.10 · MUX+solder 10.10 ·
caps 9.70.

## 1.2 Why the POM spacer (and the whole +6.20 above B) is invariant

The Jade Pro datasheet fixes PCB-top → plate-top = 5.00 ± 0.05: the switch's
plate-retention clips and housing shoulder seat against a plate in that plane,
and the plate thickness itself is datasheet-windowed (1.50, +0.01/−0.05 per
Issue #230). Spacer 3.50 + plate 1.50 = exactly 5.00. Re-splitting the 5.00
(thicker plate, shorter spacer) gains 0.00. Shortening the sum unseats the
switch. **B + 6.20 is a hard floor for any stack using Jade Pro + Wing PCB
1.20**; thinning the PCB to 1.00 was examined and rejected (datasheet ratings
are quoted at 1.2 mm; board stiffness feeds the D-038 E-R analysis; 0.20 gain
does not justify a respin risk).

## 1.3 Lever evaluation (PO axes: cost / backtracking risk / freedom)

| Lever | Δ on its bound | Cost | Backtracking risk | Freedom | Verdict |
|---|---|---|---|---|---|
| **M2×12 → M2×10 ties** (engagement 5.50 → 3.50) | tie bound 12.90 → **10.90** | none (shorter screw) | LOW — already qualified in the #248 tuning round; Phase B audits record "M2×10 engagement PASS, full thread-bearing support PASS". Physical pull-out test still open (inherited) | none lost | **ADOPT** (already the Phase B production choice; Phase A's 12.90 used the superseded ×12) |
| **Floor 2.00 → 1.60** (ribbed tray floor) | −0.40 on every floor-referenced bound | none (less material) | MEDIUM — print strength/stiffness of the tray floor and the E-R post socket floor (1.20 → 0.80 below socket) need a rib layout + physical gauge; a cracked floor is a case reprint, not a board loss | none lost | **ADOPT with conditions** (rib + gauge in Stage 2 case delta) |
| **Free gap 0.50 → 0.30** (connector + Hall bounds) | −0.20 on those bounds | none | MEDIUM — this is dress/assembly tolerance, exactly the margin class PO priority 2 protects; 0.30 still exceeds the 0.10 DRC-class clearances used elsewhere, but a hand-dressed harness varies | none lost | **ADOPT at 0.30, floor of this lever** — do not go below |
| **Assembly allowance 0.50 (connector)** | — | — | Cutting it bets against an uncertified JST max; the 4.35 is a reference (nominal) dimension | — | **REJECT** — keep 0.50 |
| **Hall reservation 3.40 → 2.40** (physical 1.35 + 1.05 flex/assembly reserve) | Hall bound 12.10 → 11.10 (F=2.00) | none | LOW–MEDIUM — the 3.40 cube is ~2.0 air over a 1.12-body sensor; the retained 1.05 reserve covers E-R-qualified PCB flex + placement. Does not touch sensing geometry (sensor position/height on PCB unchanged) | none lost | **ADOPT** (only binds once connector < ~2.9 envelope) |
| **Connector: JST SH side-entry 14-way** (SM14B-SRSS-TB, envelope 2.95) | connector bound 13.55 → 12.15 (F=2.00, ×10 ties, gap 0.50) | SH headers/housings/contacts ≈ GH class; harness re-crimp | MEDIUM–HIGH — header supply: JLC overseas **0**, presale **1,342** (REPORT-B3, 2026-11-14) → pre-purchase mitigates but single-channel risk stands; **mating-cycle rating unpublished** (friction lock) → service-life unknown; Wing footprint respin required | keeps single-14-way architecture; SH is a living JST line (no lifecycle flag found in B3) | **ADOPT as the connector lever**, Wing-side (see §1.4); supply pre-purchase is a PO-gate note |
| **Connector: Hirose DF52** (envelope 1.75) | arithmetic stack 10.90 (tie-bound) | ≈ GH class | **The #250 failures are NOT fixed**: housing DF52-14P-0.8C stock ≈ 0 at LCSC/JLC/DigiKey (2026-11-14 re-check) — a Wing-side-only or carrier pairing still needs those housings on the Wing side; Wing 17R footprint failure (3 via-in-pad) unfixed — a respin *might* fix it but #250's round was that attempt, unverified. Only the Main-routing failure is fixed (by not putting DF52 on Main) | — | **REJECTED — stays rejected** (supply failure stands) |
| **Connector: Pico-EZmate 7+7** (envelope ~1.65) | arithmetic stack 10.90 (tie-bound) | + second housing set | DigiKey **obsolete flags** on both 7-way parts + a 2023 Molex discontinuance notice (REPORT-B2); JLC stock 0. Nothing in a carrier pairing revives a discontinued part | narrows future supply options | **REJECTED — stays rejected** |
| **Connector on Main too (SH both boards)** | same Wing stack | + Main respin | HIGH — #250's lesson: Main's power copper is the fragile part under connector swaps (DF52-on-Main failed DRC + the ≤50 mΩ targets). SH-on-Main is untested | — | **REJECT for this round** — SH Wing-side + carrier (GH to Main) keeps Main Rev.7 byte-unchanged |

## 1.4 Candidate minimum stack (arithmetic)

Lever set: **SH Wing-side + M2×10 ties + floor 1.60 + free gap 0.30 + Hall
reservation 2.40**, assembly allowance 0.50 kept, GH retained on Main (via the
Issue #252 carrier if Stage 2 confirms it; otherwise this stack's harness
question reopens — Stage 2 decides).

| Bound check at the candidate | Required B | Plate-top equivalent |
|---|---:|---:|
| **SH connector: 1.60 + 2.95 + 0.50 + 0.30** | **5.35** | **11.55 — BINDING** |
| Hall (reservation 2.40): 1.60 + 2.40 + 0.30 | 4.30 | 10.50 |
| M2×10 tie: tip = 5.35 − 3.50 = 1.85 ≥ 1.20 | (4.70) | 10.90 ✓ (0.65 spare) |
| MUX+solder: 1.60 + 1.40 + 0.30 | 3.30 | 9.50 |
| Caps: 1.60 + 1.00 + 0.30 | 2.90 | 9.10 |

Resulting stack (Z from case bottom): floor 0–1.60 · PCB underside B=5.35 ·
PCB top 6.55 · plate bottom 10.05 · **plate top 11.55** · stem tip 21.15 ·
**keytop 22.65 provisional** (q=1.50; q-range 21.65–23.65).

**Gain vs GH baseline: plate −2.00, keytop −2.00 (24.65 → 22.65).**
New binding bound: the SH connector envelope (2.95). The next bound below it
is the M2×10 tie at 10.90 — only 0.65 away, so no further connector thinning
buys anything without a fastening redesign beyond M2×10.

Respins/requalification implied: **Wing Rev.5** (SH footprint + fanout
re-route at D-021 yardsticks + via-pad audit + electrical requal — the
Issue #235 programme re-run for one footprint); Main Rev.7 unchanged in the
carrier configuration. Case: tray floor remake at 1.60 with ribs (print
qualification + seam/flatness gauges inherited from #248).

*Stage 2 (harness + service qualification at this stack, and the
harness-qualified minimum if it differs) follows below.*
