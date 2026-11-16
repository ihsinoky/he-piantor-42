# Issue #255 plan — keytop height minimisation

Objective: minimise KEYTOP = plate_top + 9.60 (Jade Pro stem tip) + q (Junana, assumed 1.50, range 0.5–2.5, UNMEASURED → all absolute keytop figures provisional on q).
Refs: plate 13.55 → keytop 24.65 (GH baseline); Δ+6 plate 22.2 → keytop 33.3.

## Stage 1 — stack decomposition, verify every term from CAD/data, attack each bound
- [ ] Read #248 phaseb REPORT Phase A decomposition + Frontier (excerpts); locate sources (audit machinery, jade-pro.pdf datasheet).
- [ ] Verify terms: floor top Z2.00; GH mated 4.35; allow 0.50; gap 0.50; Hall reservation; MUX+solder; caps; PCB 1.20; POM spacer 3.50 (verify WHY invariant from Jade Pro plate dims); plate 1.50; stem tip +9.60.
- [ ] Re-verify Phase A plate-top bounds: GH 13.55 / M2 tie-root 12.90 / Hall 12.10 / MUX+solder 10.10 / caps 9.70.
- [ ] Lever per bound, costed + risk-rated (cost / backtracking+thin-margin / freedom):
  - connector: DF52 1.75 (rejected #250: Main routing, Wing 17R, housing stock), SH 2.95 (header stock 0), EZmate 7+7 (obsolete) — re-evaluate ONLY Wing-side-only or with #252 carrier; name which #250 failure each lever fixes or not.
  - M2 tie/boss root 12.90: fastening redesigns (no sub-PCB screw penetration, relocated ties, boss engagement) preserving E-R plate function (D-038).
  - Hall reservation 12.10: what it reserves; reducible terms w/o touching sensing geometry.
  - floor 2.00 + allowances 0.50+0.50: reducibility vs print strength; argue, don't assume.
- [ ] Output: candidate minimum stack (plate top + terms), lever set, new binding bound, respin/requal notes.
- [ ] CHECKPOINT commit (Stage 1 alone).

## Stage 2 — harness + service at minimum stack
- [ ] Read sibling REPORTs at this time: #252 (midconn carrier C), #253 r2 (north extension 3D bends) — excerpts.
- [ ] Best interconnect → qualify at Stage-1 minimum in #248 case design (plateau = new keytop, slope/seam unchanged): repaired-audit fitted, target 0 unexpected (2 known POM residuals only if inherited unchanged), length ≤200, unplug-first service, Fly 170 + USB PASS, print envelopes.
- [ ] If harness fails: step plate up ~0.5mm increments, same method, until pass. Report harness-qualified minimum separately; name binding constraint at each.
- [ ] CHECKPOINT commit.

## Deliverable
- hardware/case/issue-255-keytop-min/REPORT.md: decomposition table, lever table (PO axes), minimum stack (arithmetic + harness-qualified), gate table, provisional items (q first), draft decision text (REPORT only; never edit docs/decisions.md).
- Rules: scratch only in .issue255-runtime; CAD python ~/workspace/tools/cad-venv/bin/python; no push; fitted audit is the only verdict; rejected parts stay rejected unless the fixed failure is named + re-verified.
