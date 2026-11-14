# DF52 library construction and process

Dimension authority is Hirose. Archived [June 2024 catalogue](hirose-df52-2024.pdf) from [LCSC's archive](https://atta.szlcsc.com/upload/public/pdf/source/20240705/F8048CFA8CA38915C03406E9857DD465.pdf), page 6 recommended PCB layout and the 14-position dimension row. The [older Hirose catalogue](hirose-df52-legacy.pdf) comes from the [selected header's LCSC PDF](https://datasheet.lcsc.com/datasheet/pdf/5ea0a85a5bcb8788a8e9ecc2c382fe0d.pdf). The [current Hirose product/drawing entry](https://www.hirose.com/en/product/p/CL0668-0024-2-21) and [current catalogue](https://www.hirose.com/en/product/document?clcode=&documentid=en_DF52_CAT&documenttype=Catalog&lang=en&productname=&series=DF52) were consulted. Direct Hirose HTTP downloads returned 403; the archived manufacturer catalogue via LCSC supplies the dimensioned recommended layout. The current individual 2D drawing could be opened through the browser service but not downloaded as a local authoritative file. This limitation remains a release blocker.

Generated footprint: fourteen **rectangular 0.50×1.00 mm lands**, 0.80 mm pitch, centred at X−5.2…+5.2/Y−1.11. Two **rectangular 0.90×1.60 mm MP lands**, X±6.45/Y+0.81. Overall land extent in Y is 3.22 mm. Body bounds X±6.70/Y−1.26…+1.51, 2.77 mm bare depth. Rectangles implement the dimensioned layout directly; they do not shrink the recommended solder area with rounded corners. No electrical net is assigned to either MP land. Contact numbering follows the catalogue pin-1 mark from the mounting side; native flip/rotation carries the same numbering to Wing B.Cu. Main's old pin15 mechanical lands become MP, not a fifteenth cavity.

The standalone symbol has fourteen numbered passive contacts plus mechanical MP marked no-connect. Main's frozen review symbols retain their original wire connection coordinates, with identity/footprint and mechanical number updated. This changes no logical connection.

A conservative **surface copper-free body reservation**, X±5.95/Y−0.55…+1.61, forbids tracks, vias and pours underneath the body while leaving the solder lands available. Opposite/internal copper layers remain available. This is an additional study reservation, **not a claim to have transcribed the individual drawing's exact no-pattern polygon**. Exact manufacturer no-pattern coverage and pin-mark interpretation require drawing review before library release. Do not remove it to make the failed Main route pass. Native board copies of the same reservation were added during the Main repair to expose it to the router's board-keepout parser.

The board stays **1.2 mm**; the SMT pattern has no board-thickness-dependent retention posts. Hirose's catalogue process is **0.10 mm stencil, 100% land opening**, lead-free peak ≤250°C (peak interval ≤10 s), ≥220°C for <60 s, preheat 150–180°C for 90–120 s, ≤2 reflow cycles. Manual solder: 350±10°C, ≤3 s. Connector-centre board warpage ≤0.02 mm relative to ends; cleaning not recommended. The project board, paste, actual oven profile and nail wetting need assembler DFM/profile acceptance; no process concession is hidden in CAD.

Hirose specifies AWG28–32 thin wire with OD0.50–0.60 mm, initial contact resistance ≤10 mΩ and +85°C maximum operation. This project uses AWG28, 1.2 A at the 14-position catalogue condition. The 125°C solver corner is inherited numerical extrapolation, not DF52 temperature approval.

Continuation drawing review (2026-11-14): the local
[header drawing](hirose-header-drawing.pdf) is Hirose EDC3-356517-01,
revision 3 dated 2017-03-10, archived reference copy bearing 2018-02-01
copyright. [Review record](drawing-review.json) records its retrieval URL and
SHA-256. Both pages were rendered and inspected. Page 1 corroborates 13.4 /
10.4 / 12.8 mm dimensions, 0.8 mm pitch, 0.5×1.0 contact lands,
0.9×1.6 nail lands, 3.22 mm overall land depth and 0.10 mm stencil. The
0.8 mm nail offset is to the inner edge, giving nail centres ±6.45 mm.
The mounting-side pin-1 mark corroborates the library numbering. Page 2 gives
the reference reflow profile and two-cycle limit.

This is an older manufacturer drawing, **not the downloaded current drawing**.
The current [Hirose drawing endpoint](https://www.hirose.com/en/product/p/CL0668-0024-2-21/documents?path=%2Fapi%2Fv1%2Fproducts%2FCL0668-0024-2-21%2Fdocuments%2Fdrawing_2d%2Fcontent%3Flang%3DEN)
was located and its two-page identity was retrieved through the web service;
direct local download attempts returned 403. Its dimensioned graphics were not
available for a dependable local review. No explicit dimensioned no-pattern
polygon appears on the archived drawing. Consequently, the conservative
surface reservation is retained and the **exact current no-pattern coverage
is an unresolved library-release gate**. The older PDF resolves the absence
of any local individual drawing evidence; it does not resolve that gate.
