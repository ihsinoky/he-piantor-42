# FABRICATION — DRAFT, NOT FOR ORDER

Wireless Main (Issue #292), module Insight SiP ISP1807-LR (D-056).
Status: DRAFT package for the D-058 adoption gate. NOT released for
manufacture. The module footprint is Insight SiP OFFICIAL CAD
(REPORT.md deviation 1 DISCHARGED) and the module field is routed
under the D-057 rule exception (0.05 mm class inside the
MODULE_FIELD_FINE rule area only; REPORT.md deviation 9 RESOLVED).
Board file SHA-256 `26072619…` — the edge-fix round (REPORT.md
deviation 13) superseded the D-058-adopted file, whose copper
crossed the board outline in 72 places; the fixed board passes
the copper-containment gate (`checks/copper_containment.py`,
0 crossings / 0 touchings). Two GND items remain unconnected,
both item-dispositioned in deviation 13 (CVCC2.2 pad; module
GND pads U1.14+U1.16); all signal nets are complete. Do not
order until the PO judges the residuals at the order gate.

Board: 4 layers, 1.2 mm, outline identical to Main Rev.10
(Edge.Cuts segments verified equal as undirected edges, 14/14).
Stackup and design settings transplanted from the Rev.10 project;
Default netclass corrected to 0.10 mm clearance / 0.10 mm track
(the Rev.10 project file carried 0.20 — see REPORT.md).

Fabrication notes:
- U1 (ISP1807-LR): LGA, hand-fit or consigned placement is the
  fallback; PCBA route is JLCPCB Pre-order Parts (LCSC C5264268).
  After placement, bring-up is by SWD (JSWD) + continuity check of
  the ANT_LINK (OUT_ANT pin 20 to OUT_MOD pin 22) and the power
  pins before first RF use.
- U4 pin 2 (TPS22919 GND) is connected by a 0.45/0.30 via-in-pad.
  Require the via plugged and tented (or filled) so the pad solders
  flat.
- JSWD is a pads-only TC2050 footprint (official Tag-Connect pattern, D-061; no part fitted);
  pogo access with the case open, nothing above it.
- JBATT is a JST GH (BM02B-GHS-TB class, 1.25 mm pitch, 2.9 mm
  tall) 2-pin land; LCSC code to be confirmed at quote.
- JPAD is a 6-contact 0.5 mm FFC land for the trackpad bay
  disconnect (no part on Main; the FFC ships with the trackpad
  side).
- Mounting holes H1–H3 are NPTH 2.2 mm, positions identical to
  Rev.10.
- Solder mask / finish: as per the Rev.10 JLCPCB order spec
  (1 oz, HASL-free preferred); no impedance-controlled nets.
