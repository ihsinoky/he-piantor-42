"""Write quote-handoff.md for the five Rev.9/Rev.6 packages.
Carries the Issue #267 handoff content with the FH12 status CORRECTED
to the quote run's finding: FH12-14S-0.5SH(55) IS orderable at JLCPCB
as LCSC C5378715 (Extended, stock 3,907 on 2026-11-17)."""
from pathlib import Path

ROOT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification")

MAIN = """# Main Rev.9 — JLCPCB quote handoff (DRAFT package, not released for manufacture)

Upload together: a zip of this directory's `gerber/` contents,
`BOM-jlcpcb.csv` and `CPL-jlcpcb-gerber-frame.csv` (Issue #267 conversion,
carried over unchanged — Issue #270 changed the board outline only;
parts, footprints and positions are identical to Main Rev.8).
Do NOT upload the KiCad-native `BOM.csv` / `CPL.csv` — their LCSC column is
empty (except FH12) and the CPL uses KiCad headers.

- BOM: 54 part rows / 55 designators, every orderable designator mapped
  to a real LCSC code (sources: Main Rev.6 package BOM; C26-C28 = adopted
  substitute TDK C3225X7R1C226MT000N / C342699 and R17 = Yageo
  RT0603BRD0754K9L / C728593 per docs/issue-175; L1 = C3033018 per the
  order-time rule, stock 19,053 on 2026-11-16). Unmapped parts: NONE.
  `BOM-jlcpcb-consolidated.csv` (24 part rows with Quantity) is the
  format the JLCPCB matching screen accepts.
- FH12: J2/J3 (Hirose FH12-14S-0.5SH(55)) = LCSC **C5378715** — verified
  orderable at JLCPCB in the Issue #267 quote run (Extended part, stock
  3,907 on 2026-11-17, auto-matched in the PCBA quote and included in
  the quoted totals). No consignment needed. Do not substitute another
  connector. Re-confirm stock at order time.
- Excluded from the JLCPCB BOM (as in the Rev.6 package): mounting holes
  H1-H3 (NPTH) and test points TP1-TP4 — not orderable parts.
- CPL frame: gerber frame = native KiCad frame for this package (offset
  +0.000000 / +0.000000 mm; all 55 footprint origins re-verified against
  the fresh Rev.9 CPL export, max deviation < 0.000001 mm). Use only the
  converted file, not `CPL.csv`.
- Board change vs Rev.8: Edge.Cuts only (60-degree trapezoid connector
  tabs). Copper, footprints and schematic are unchanged; see the Issue
  #270 REPORT.md. The Rev.8 quote (Issue #267, $115.49 for 5 pcs PCBA)
  carries over except for any outline-driven PCB price delta.
- Inherited gates (from the Rev.6 handoff, unchanged): supplier DFM,
  stencil/paste acceptance, stock confirmation at order time, CPL
  rotation/pin-1 acceptance, physical fit checks. This handoff authorizes
  a quote only — no order, no manufacturing release.
"""

WING = """# Wing Rev.6 {variant} — JLCPCB quote handoff (DRAFT package, not released for manufacture)

Upload together: a zip of this directory's `gerber/` contents,
`BOM-jlcpcb.csv` and `CPL-jlcpcb-gerber-frame.csv` (Issue #267 conversion,
carried over unchanged — Issue #270 changed the notch-zone outline only;
parts, footprints and positions are identical to Wing Rev.5).
Do NOT upload the KiCad-native `BOM.csv` / `CPL.csv` — their LCSC column is
empty (except FH12) and the CPL uses KiCad headers.

- BOM: 4 part rows / 49 designators, every orderable designator mapped to a
  real LCSC code (sources: Matrix Rev.3 package BOM — DRV5055A3QDBZR /
  C266128, GRM188R71C104KA01D / C45000, TMUX1208PWR / C494728).
  Unmapped parts: NONE.
- FH12: J_WING (Hirose FH12-14S-0.5SH(55)) = LCSC **C5378715** — verified
  orderable at JLCPCB in the Issue #267 quote run (Extended part, stock
  3,907 on 2026-11-17, auto-matched in the PCBA quotes). No consignment
  needed. Do not substitute another connector. Re-confirm stock at order
  time.
- Excluded from the JLCPCB BOM (as in the adopted packages): NPTH mounting
  holes (MH_*, H1-H4) and test-point pads (TP_*) — not orderable parts.
- Assembly is single-sided, all parts on the BOTTOM layer (Layer column of
  the CPL says `bottom` throughout).
- CPL frame: gerber frame = native KiCad frame for this package (offset
  +0.000000 / +0.000000 mm; all 49 footprint origins re-verified against
  the fresh Rev.6 CPL export, max deviation < 0.000001 mm). Use only the
  converted file, not `CPL.csv`.
- Board change vs Rev.5: Edge.Cuts only (notch floor re-cut as the exact
  0.55 mm offset of the Main Rev.9 trapezoid tab; pour fringe refilled,
  delta confined to the notch band). Routing and footprints unchanged;
  see the Issue #270 REPORT.md.
- Inherited gates: supplier DFM, stencil/paste acceptance, stock
  confirmation at order time, CPL rotation/pin-1 acceptance (bottom-side
  parts), physical fit checks. Wing assembly method (PCBA vs hand) is NOT
  decided — it waits on the Matrix evaluation; this handoff supports the
  PCBA quote and the bare-board price only. No order, no release.
"""

(ROOT / "issue-270-main-rev9" / "main-rev9" / "manufacturing" / "quote-handoff.md").write_text(MAIN)
for v in ("17mm-left", "17mm-right", "16mm-left", "16mm-right"):
    (ROOT / "issue-270-wing-rev6" / f"wing-rev6-{v}" / "manufacturing" / "quote-handoff.md").write_text(
        WING.format(variant=v))
print("hanoffs written")
