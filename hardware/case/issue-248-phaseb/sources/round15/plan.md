# Round 15 plan - body-aware routing (Candidate A completion)
- S0: read REPORT r14 section (excerpts); inventory r14 scripts/hit maps
- S1: exact-distance optimiser: BRep distance penalties vs fixed solids
  (Wing PCB, switch env, plates, trays, MUX bounds, POM) or corridor-extract
  + constrained re-opt; VALIDATE: reproduce r14 hit map 94(17mm)/106(16mm)
- S2: re-optimise feed -> fitted wire-fixed 0, WW ~0 (close last 2 crossings)
- S3: reel fans pins 3-14 R5-buildable + fitted-clean via same machinery;
  full 14-strand slack loop, +30.20/strand accounting; fitted audit of loop
- S4: full audit both pitches (repaired audit): G1 collision, G2 length<=200,
  G3 unplug-first service steps, G4 Fly, G5 USB, G6 caps(Junana OPEN),
  G7 mfg 19/19+envelopes, G8 preview STEP
- S5: REPORT r15 section; freeze round14; checkpoints each stage
- Freezes: boards/plates byte-identical; GH/D-024; OD1/AWG28; Z13.55 deck;
  Z24.65 prov plateau; seam; blisters; M2x10; retainers; R>=5 cert.
  Fixed-body change only neck tray cut class (UF step1) if needed, ledgered.
