# Issue #252 plan — Candidate C adoption study

## Stages
- S0 setup: plan, git config, survey assets (GH footprint/symbol, KiCad runtime), survey #248 machinery (frontier fitlib, audit_repair, round13 sources)
- S1 carrier PCB: KiCad design, 2x SM14B-GHS-TB back-to-back, 1:1 n->n; mapping table verified vs native pad coords; DRC/ERC; mounting concept (bay seat, case delta ledger); mfg note (PCBA vs hot-plate)
- S2 routing @13.55: copy machinery from raise worktree sources/ (frontier + audit_repair); add carrier solids to body set; build 2 segments/side (Wing->carrier, carrier->Main); fitted repaired audit; round-18 fitted repair passes (bounded); verdict gate1 must = 0 (2 known POM residuals only if inherited unchanged)
- S3 service qualification: shells off -> carrier unplug motion audit (both pairs, ~6mm along axes) -> Wing lift-out w/ segment -> Main segment removal; Fly170 + USB gates inherited/rechecked
- S4 if 13.55 fails: repeat S2/S3 core at 15.0, 16.2 (frontier height-shift model) -> C's own frontier
- S5 electrical: real extraction — end-to-end loop/branch R incl +2 mated pairs/line (GH contact 30mOhm class), crimps, carrier traces (actual layout), wire R from actual segment lengths; Vfar @127mA vs 4.60V; Main-copper <=50mOhm targets kept separate (#167 lesson)
- S6 stock+cost: dated live check LCSC/JLCPCB: C265343 header, GHR-14V-S housing, SSHL-002T-P0.2 contacts; delta/keyboard: +2 hdr +2 plug +28 crimps + carrier PCB/assembly; quote-level cost table
- S7 REPORT.md in hardware/case/issue-252-candidate-c/ + carrier tree hardware/kicad/qualification/issue-252-carrier/; gate table (8-gate adapted), draft D-033 amendment + D-xxx text (NOT editing decisions.md); verdict plain

## Invariants
- Main Rev.7 / Wing Rev.4 byte-unchanged; D-024 cavity n = GH pin n through both mated pairs
- OD1/AWG28, R>=5 certified; segment lengths <=200mm each + end-to-end total stated
- F-015 precedent; Ender-3 Pro envelopes; Al plates D-038
- Fitted repaired audit is the only verdict; no silent relaxation
- Scratch only in .issue252-runtime/; CAD py = ~/workspace/tools/cad-venv/bin/python; no push
