# GH overhead envelope source

JST official GH family drawing, downloaded 2026-11-07:
https://www.jst.com/wp-content/uploads/2025/06/eGH.pdf
(saved as `jst-gh.pdf`). Page 2 top-entry assembly profile gives the reference
mated height (7.3mm). It is not a maximum tolerance specification. The Stage 2
assembly model reserves 8mm above PCB, and puts the horizontal cable center
5mm higher, allowing a nominal R5 vertical-to-horizontal transition.

The same catalog specifies insulation OD0.76–1.0mm. Fourteen such wires cannot
form a phi2mm bundle even by cross-sectional area. Phi2 is retained only as the
Stage 1 geometric screen. Stage 2 also screens a controlled <=phi5mm assembled
bundle. Its retention/sleeve must fit within that outer envelope. Manufacturer
minimum wire bend radius and actual assembled dimensions remain fit inputs.

The continuation independently verified the official English catalog at
https://www.jst-mfg.com/product/pdf/eng/eGH.pdf on 2026-11-07: p.1 lists
105C including current-induced temperature rise and insulation OD0.76-1.0mm;
p.2 labels the top-entry assembly height (7.3) as a reference value. The
saved PDF uses external CID fonts that may not render in the minimal runtime;
use the official English catalog for a readable manufacturer drawing.
