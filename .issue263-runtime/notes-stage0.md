# Stage 0 recon (2026-11-17)
- KiCad runtime: /home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/kicad (v9.0.9), KRT + venv + grid-search same store (issue-235 toolchain.json).
- Wing Rev.4 pipeline: hardware/kicad/qualification/issue-235-wing-round2/ (build.py, route.py, audit.py, variants wing-rev4-{16,17}mm-{left,right}).
- Main Rev.7 pipeline: hardware/kicad/qualification/issue-240-main-rev7/ (build.py, extract-power.py, power-extraction-final.json; Rev.7 input loop 49.086 mOhm class).
- #261 placement spec (REPORT, fitted audit):
  Wing ZIF envelope centre (+-27.0,-37.5), entry slot (+-27.0,-34.2), entry CL Z2.95, underside at GH site, mouth facing Main.
  Main J2 centre (23.3,40.8) yaw -43deg mouth (20.92,38.24); J3 centre (-23.09,40.97) yaw 38deg mouth (-20.92,38.24); entry CL Z6.90.
  Stack: Wing PCB underside B=4.70, PCB 4.70-5.90; plate top 10.90; keytop 22.00 prov.
  Escape: 0.5 pitch pad gap 0.20 -> no same-layer escape at 0.10/0.10; fan outboard + 0.60/0.30 vias to back layer (GH fanout class #235/#240).
  Electrical #261 (custom FPC lanes): loop 208.5 mOhm, Vfar 4.785V. #264 cable model supersedes cable term: loop 203.8 mOhm assumed / 234.0 pessimistic, Vfar 4.786/4.782 (state term in Rev.8 extraction).
- #264: cable 152660149 Type A 152mm; 5 folds; arrival order reversed k->15-k both sides; FH12-14S-0.5SH(55) bottom-contact all 4 sites, no board delta on Wing; jig PETG 42x98x11, R2.0 pins, S1 slider detents 148..156mm; measurement acceptance <=1.30 ohm/lane pre-fold.
