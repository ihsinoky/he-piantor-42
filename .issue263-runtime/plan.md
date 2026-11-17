# Issue #263 plan — board implementation round (Wing Rev.5 / Main Rev.8)

Inputs: D-042 as amended (stock Molex 152660149 folded + jig, #264);
#261 REPORT placement spec + pad-escape; #264 fold/jig/audit model;
ZIF = FH12-14S-0.5SH(55) bottom-contact x4; cable reversal k->15-k
absorbed in Main Rev.8 footprint assignment (verify numerically from
built pad coordinates, #252 method).

Yardsticks: Wing D-021 (2L 1.2mm via .60/.30 clr .10 sig .10/pwr .30);
Main D-019 (4L 1.2mm .10/.10 via .60/.30); via-pad >=0.10 floor (.125
target) incl testpoints; Main common loop <=50 mOhm class, Vfar >=4.60V
@127mA/Wing incl cable term per #264 model (state term).

Stages (checkpoint each):
0. Recon: locate KiCad runtime + Rev.4/Rev.7 build pipelines; extract
   #261 placement spec numbers into notes-stage0.md.
1. ZIF finalisation: orderable FH12-14S-0.5SH(55), datasheet mating vs
   152660149, dated stock check (need x10). If unobtainable: STOP stage,
   report nearest variant + delta.
2. Wing Rev.5 x4 variants from issue-235 build pipeline: DRC 0 /
   unrouted 0 (native ERC n/a - inherited), via-pad, Vfar extraction.
3. Main Rev.8 from issue-240 pipeline: reversal in assignment, DRC 0 /
   unrouted 0 / ERC 0, via-pad, resistance extraction vs Rev.7, Vfar,
   copper-diff locality disclosed.
4. Case production tree plate 10.90 + fitted REPAIRED audit re-run with
   as-routed boards + #264 folded cable: gate1 = 0 unexpected (name
   residuals), service, Fly/USB inheritance, envelopes.
5. Manufacturing packages (gerber/CPL/BOM class), jig data + pre-fold
   measurement procedure (<=1.30 ohm/lane) in package notes, FFC spec.
   NO ordering.
REPORT.md ties stages; draft decision text in REPORT only.

Rules: scratch only in .issue263-runtime/; CAD python cad-venv; do NOT
push; no silent yardstick relaxation.
