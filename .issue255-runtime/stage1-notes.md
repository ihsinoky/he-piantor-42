# Stage 1 notes — verification + arithmetic (2026-11-16)

## Verified from sources (not summaries)
- Phase A decomposition: raise REPORT.md §1 (issue-248-lowdeck-raise). plate = B + 1.20 PCB + 3.50 POM + 1.50 plate = B+6.20.
- Jade Pro (repo jade-pro.pdf p.7, per Phase A primary read; drawing numerals are vector art, pdftotext does not yield them — cross-checked via #230's use of same datasheet): housing top = PCB top +11.10; stem TT 3.50; PCB-top→plate-top 5.00±0.05 → stem tip = plate +9.60. Spacer invariant WHY: 3.50 spacer + 1.50 plate = the datasheet's 5.00 switch-seat; plate thickness itself datasheet-bound 1.50 (+0.01/−0.05, #230). The +5.00 above PCB top is fixed; only its split could change, gain 0.
- GH mated 4.35: JST reference dim (Phase A/B1 dimensioned model). Assembly allowance 0.50 = inherited budget, NOT JST-certified max. Free gap 0.50 retained in Phase A.
- Hall reservation 3.40 = #232 build.py line 100: reservation CUBE 3.4×3.4×3.4 (kind=='hall'), vs MUX envelope height 1.4, caps 1.0. Physical DRV5055 (repo JITX model from TI outline 4214838/F): SOT-23 body height 1.12; seated protrusion ≈1.27 max + solder ≈1.35. → ~2.0 of the 3.40 is protective air (flex/assembly). Argued reduction: reservation 2.40 (physical 1.35 + 1.05 reserve) — saves 1.00 on Hall bound.
- M2 tie: Phase A bound used M2×12 (engagement 5.50 below B, root ≥1.20 → B≥6.70 → 12.90). Phase B production switched to M2×10 (engagement 3.50) — qualified in the tuning round; phaseb REPORT audits repeatedly record "M2×10 engagement PASS / full thread-bearing support PASS". → tie bound with M2×10: B ≥ 3.50+1.20 = 4.70 → plate 10.90. ALREADY-PROVEN lever.
- Connectors (REPORT-B3 verified lines): DF52 envelope 1.75×4.10, 20 cycles, housing must be secured (stock ~0 in #250 re-check); SH 2.95×6.25, header presale 1342 / overseas 0, cycle rating NOT published; EZmate 7+7 (REPORT-B2): mated 1.65 class, DigiKey obsolete flags, JLC stock 0.
- PCB 1.20: Jade Pro ratings quoted at PCB 1.2mm; thinning = respin + stiffness requal for 0.20 → examined, rejected.

## Bound arithmetic (B = floor_top F + depth + allow/gap; plate = B+6.20; keytop = plate+9.60+q, q=1.50)
Baseline (F=2.00): GH 7.35→13.55 | tie×12 6.70→12.90 | Hall 5.90→12.10 | MUX 3.90→10.10 | caps 3.50→9.70. Keytop 24.65.

## Lever stacks (plate top / keytop@q1.5)
- L1 M2×10 only → GH binds: 13.55 / 24.65 (gain 0)
- L2 GH + floor 1.60 + gap 0.30 + M2×10 → B=1.60+4.35+0.50+0.30=6.75 → 12.95 / 24.05 (gain 0.60). Tie tip 3.25≥1.20 ✓; Hall 5.50 ✓ under.
- L3 SH both boards, F=2.0, M2×10 → conn B=5.95 → 12.15 / 23.25. Main Rev.8 untested (DF52 lesson: Main power copper fragile under swaps).
- L4 SH + floor 1.60 + gap 0.30 + Hall res 2.40 + M2×10 → conn B=1.60+2.95+0.50+0.30=5.35 → plate 11.55 / keytop 22.65 (q range 21.65–23.65). Hall B=1.60+2.40+0.30=4.30→10.50 ✓; tie tip=5.35−3.50=1.85≥1.20 ✓ (0.65 spare); MUX 3.30 ✓. BINDING: SH connector envelope. ← CANDIDATE MINIMUM (credible levers)
- L5 DF52 + same micros → conn B=4.15, tie binds B≥4.70 → 10.90 / 22.00. NOT CREDIBLE: housing stock failure unfixed by any pairing (Wing side still needs DF52 housings); Wing 17R footprint failure from #250 unfixed (respin might fix, unverified). Excluded.
- L6 EZmate 7+7 → arithmetic 10.90 like L5. NOT CREDIBLE: obsolete flags + stock 0 stand. Excluded.

## Candidate minimum stack (L4), terms (Z from floor bottom 0)
floor 0–1.60 (ribbed, −0.40) | B=5.35 (PCB underside) | PCB 5.35–6.55 | plate bottom 10.05, top 11.55 (spacer 3.50: 6.55–10.05) | stem tip 21.15 | keytop 22.65 (q=1.50 assumed).
Respins: Wing Rev.5 (SH footprint + fanout requal) IF SH Wing-side; Main Rev.8 only if SH both sides — preferred config: SH Wing-side + #252 carrier (GH to Main) pending Stage 2 read of #252. Carrier height does not enter the Wing stack (bay-mounted).
Risks: floor 1.60 print strength (needs rib + physical gauge; socket floor under E-R posts thins 1.20→0.80); gap 0.30 dress tolerance; SH header supply = presale 1342 only (pre-purchase mitigates, single-source risk remains); SH cycle rating unpublished (service-life unknown → backtracking risk); Hall reserve cut assumes E-R posts limit flex as qualified.
