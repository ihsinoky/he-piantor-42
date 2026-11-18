# Main Rev.10 — JLCPCB quote handoff (DRAFT package, not released for manufacture)

Upload together: a zip of this directory's `gerber/` contents,
`BOM-jlcpcb.csv` and `CPL-jlcpcb-gerber-frame.csv` (Issue #267
conversion, carried over; the J2 CPL row is regenerated for
Rev.10 — see below).
Do NOT upload the KiCad-native `BOM.csv` / `CPL.csv` — their LCSC
column is empty (except FH12) and the CPL uses KiCad headers.

- BOM: 54 part rows / 55 designators, every orderable designator
  mapped to a real LCSC code (sources: Main Rev.6 package BOM;
  C26-C28 = adopted substitute TDK C3225X7R1C226MT000N / C342699
  and R17 = Yageo RT0603BRD0754K9L / C728593 per docs/issue-175;
  L1 = C3033018 per the order-time rule, stock 19,053 on
  2026-11-16). Unmapped parts: NONE. Parts are IDENTICAL to
  Rev.9/Rev.8 — Rev.10 changes no component.
  `BOM-jlcpcb-consolidated.csv` (24 part rows with Quantity) is
  the format the JLCPCB matching screen accepts.
- FH12: J2/J3 (Hirose FH12-14S-0.5SH(55)) = LCSC **C5378715** —
  verified orderable at JLCPCB in the Issue #267 quote run
  (Extended part, stock 3,907 on 2026-11-17, auto-matched in the
  PCBA quote and included in the quoted totals). No consignment
  needed. Do not substitute another connector. Re-confirm stock
  at order time.
- Excluded from the JLCPCB BOM (as in the Rev.6 package): mounting
  holes H1-H3 (NPTH) and test points TP1-TP4 — not orderable parts.
- CPL frame: gerber frame = native KiCad frame for this package
  (offset +0.000000 / +0.000000 mm). J2 sits at its new mirrored
  pose in Rev.10 (PosX 75.745202, PosY -111.823895, Rot 43.0), so
  the conversion file's J2 row was regenerated from the fresh
  Rev.10 CPL export; all 55 footprint origins re-verified against
  that export, max deviation < 0.000001 mm. Use only the converted
  file, not `CPL.csv`.
- Board change vs Rev.9: J2 site mirrored onto J3 (footprint move
  + fanout re-route, confined to J2's own nets) and the left tab
  replaced by the mirror of the right tab. Schematic unchanged.
  See the Issue #275 REPORT.md. The Rev.8 quote (Issue #267,
  $115.49 for 5 pcs PCBA) is the price class reference; re-quote
  at order time.
- Inherited gates (from the Rev.6 handoff, unchanged): supplier
  DFM, stencil/paste acceptance, stock confirmation at order
  time, CPL rotation/pin-1 acceptance, physical fit checks. This
  handoff authorizes a quote only — no order, no manufacturing
  release.
