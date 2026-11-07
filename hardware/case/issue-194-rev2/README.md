# Wing Rev.2 case inputs (Issue #194 Phase B)

`generate.py` regenerates four independent sets of key, hole and outline CSVs
from `wing.rev2`. Source frame: top view, X right, Y up, CCW degrees.
KiCad X=100+x, Y=100-y. All sizes are mm. Outlines and holes retain the
approved Phase A fixed origin; neither half is recentered. The PO south-cut
revision trims the south edge to the full switch-envelope limit and adds a
45-degree inner chamfer (3.956/3.928mm from the former corner). The outer
south mounting hole follows the edge; the inner south mounting hole moves
15.8mm north. Use the five-vertex outline CSVs and revised mounting rows.

Hall XY is the nominal active point and calibrated land origin (delta=0).
All Hall and local 100nF capacitors are on the bottom. Locator NPTH: nominal
1.70mm, required finished tolerance +/-0.05mm, centers +/-5.08mm in key frame.
This is a design adoption from the manufacturer's 1.27mm grid, not a measured
fit qualification. PCB thickness 1.2mm; switch support square 15.8mm. Junana MX
physical envelope, locator fit, stack height and magnetic polarity/response
still require physical validation; old #150 raised-fixture heights do not apply.
