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

## Follow-up round (PO decision 2026-11-17: option (a))
F0. Main Rev.8: extend outline with tabs under both ZIFs (~+4.1 mm past
    slanted edges in connector zones; REPORT 3.3(a)); route at spec
    poses, reversal assignment. Gates: DRC 0 / unrouted 0 / ERC 0,
    via-pad >=0.10; resistance extraction (input/common/branch) vs
    Rev.7 class; Rev.8-native Vfar @127mA/Wing incl #264 cable term;
    copper-diff locality disclosed.
F1. Wing Rev.5: close the 1 GND island per variant by local repair
    only (no placement moves, no rule relaxation); unconnected 0,
    wrong-net 0, via-pad not worse than 0.1013/0.1072/0.1252/0.1301.
F2. Case re-audit: tray pocket fit for extended Main outline (0.50 mm
    class clearance; silhouette D-037 NOT to be exceeded), then fitted
    repaired audit re-run (as-routed boards + #264 folded cable):
    gate 1 = 0 unexpected (name residuals), service, Fly/USB inherit.
F3. FH12 footprint verification vs Hirose official land pattern
    (CL586-0533-0 or official product-page drawing) from the web;
    pad-by-pad compare; correct + re-run affected checks if differs;
    if unobtainable, keep the flag explicit in REPORT.
F4. Regenerate manufacturing packages (Main Rev.8 + Wing Rev.5 x4)
    with final boards; status reflects closed gates; still NOT FOR
    ORDER (PO GO, Junana, order-time stock re-verify listed open).
REPORT.md: add follow-up-round section; remaining-before-order list
updated. decisions.md untouched.

## Follow-up round OUTCOME (2026-11-17)
- F0 Main Rev.8: CLOSED (unconnected 0, DRC errors 0, ERC 0, via-pad 0.1596).
  Closure: 6 std rolls (4) + 5 esc rolls (2) + 4 KRT completion passes (1)
  + J3.8 knot rip-up (7 segments) + 1 completion pass (0). 5 dangling
  warnings documented. Extraction: input 37.0 / common 75.6 (MISS) /
  branch J2 114.2, J3 240.9 mOhm (MISS); Vfar 4.754 V PASS.
- F1 Wing: 17L CLOSED (plane-repair A* 0.025 window). 16L/16R/17R BLOCKED
  with named pinching nets + NO PATH evidence at two grids.
- F2 Case: tray relief +3.94/+3.61 mm3 (inside D-037 silhouette);
  WING SEAM CONFLICT: tabs bite <=1.95 mm into true Wing outlines —
  PO disposition required (options in REPORT).
- F3 Footprint: catalog verified; land length 1.50->1.30 corrected in
  .kicad_mod + all embedded footprints, re-audited clean. MP flag remains.
  (Correction had been checkpointed as done before execution; caught on
  package review, then actually applied — see REPORT F3 note.)
- F4 Packages regenerated; FABRICATION.md x5 rewritten; case README updated.
- REPORT.md follow-up section written. decisions.md NOT edited.
