# Round 16 plan - curriculum feed optimisation + continuous slack placement

## Inputs (from round 15)
- exact_oracle.py VALIDATED (max diff 0.0; r14 hit map 94/106 reproduced)
- design_r15 rise skeleton (Y/Z from clearance scans); r14 feed = WW champion (true WW 2) but WF 94/106 body-blind
- r15 taut fitted: WW 6, WF 108/118, longest 102.3; exact feed opt stalled (loss 853k->165k chunk0, L-BFGS-B stall; fitted WW 42/WF 100/117.45)
- slack: shared-axis impossible; gridded disk assignment infeasible (capacity ~5x5<28); continuous placement UNEXPLORED
- gates: 2 PASS; 4/5/7/8 inherited PASS; 6 OPEN (Junana); 1/3 FAIL

## Task 1 - feed convergence via curriculum
- Warm start: round-14 WW-2 feed chains on design_r15 skeleton
- Stage 1: binding bodies only (C5 switch envelopes + Wing PCBs + plates)
- Stage 2: + trays + MUX bounds + POM
- Stage 3: full body set, exact oracle
- Hinge-continuation: penalty weight soft -> hard per stage; persist state (npy/json) between chunks
- Fitted probe after each stage (strict build, dense <=1.5mm sampling, repaired audit); incumbent = best FITTED state, not best loss
- Target: WF 0 with WW <= 2

## Task 2 - slack, continuous placement
- Derive bay free volume from frozen solids (exact oracle occupancy)
- Continuous reel/disk placement: centres/Z/R continuous, entry angles free, both sides in ONE optimisation (or disjoint-by-construction volumes)
- Fallback shapes: large-radius flat coils hugging bay walls, serpentine-free
- Success: fitted-clean stored loop, 28 strands, exact +30.20 slack/strand, finished <=200 incl tails

## Task 3 - audit
- Both land: full audit both pitches (gates 1/2/3 unplug-first motion, 4/5/7/8 inherited-verify, 6 OPEN)
- One lands: audit what exists; name other's binding constraint with strongest evidence

## Task 4 - report
- REPORT.md round-16 section on top; freeze round 15; checkpoint per stage

## Rules
- Scratch only .issue248-runtime/round16; cad-venv python; no push; fitted audit is the only verdict
- Fixed-body changes: pre-authorised neck tray cut class (step 1) only if strictly needed, ledgered; storage needing case-geometry change = prove + stop (step 4/PO)
