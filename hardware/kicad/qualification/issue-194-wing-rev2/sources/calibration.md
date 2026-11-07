# Phase B preflight: Hall and locator coordinates

Manufacturer sources are preserved with SHA-256 in `retrieval.json`.

TI DRV5055 SBAS640C (Rev.C, June 2026), section 6.3.8, page14,
Figure6-5: DBZ/SOT-23 sensing element is centered in the package in XY,
with +/-50um position tolerance; lead seating plane to element is
650+/-80um. DBZ0003A package drawing supplies the body center datum.
The existing JITX component uses `SOT23_3()` with symmetric 1.3mm body width,
2.9mm body length and lead span. The extracted native Wing lands have
X extrema -1.67/+1.67 and paired lead Y centers +/-0.95; origin is the
package body center, not the centroid of the three pad centers. An arithmetic
centroid of those three pad centers would be incorrect because two leads lie
on one side. Nominal active offset from this body-centered land origin:
**delta=(0,0)mm**, not (-0.338522,0). Apply `F=K-R(theta)delta` explicitly.
The +/-0.05mm is device tolerance, not a deterministic offset to subtract.

Native KiCad bottom flip plus the final top-view angle maps the zero-angle
land coordinates `(x,y)` to `(x,-y)` in the top-view mechanical frame.
The physical sensor is on B.Cu. With delta=0, the bottom transform also gives
zero active offset. Pin numbers and VCC/OUT/GND identity are retained by the
native flip; the right board is a separately placed identical part. Independent
verification derives every individual pad location from this transform.

Gateron SPEC-KS-20T-041 v1 (2024-08-19), page7, Layout of PCB:
locator holes lie on the same horizontal grid line, eight 1.27mm grid spaces
apart, symmetrically about the magnet/actuator axis. Thus nominal centers
are (-5.08,0)/(+5.08,0). The bottom view shows the same symmetric pair;
reflection of the drawing cannot alter the pair. The hole callout explicitly
requires diameter1.70+/-0.05mm. PCB thickness is1.20mm. A direct raster read
checks the two centers are eight spaces apart, independent of raster scale.

**Design adoption:** manufacture the nominal +/-5.08mm pair as NPTH1.70,
requiring completed hole diameter1.65..1.75mm. This is an engineering adoption
of the manufacturer's dimensioned grid, not measured manufacturing history.
The prior #150/#158 work is drawing analysis only; neither constitutes a
fabricated Jade Pro fit trial. No independent fabricated-fit data was found in
this work copy. Hole-position tolerance relative to the magnetic axis and
maximum actual locator diameter remain unmeasured; do not claim fit or mass
production acceptance. Verify with the specified full-height Jade Pro sample
and manufacturer before order release. Do not silently substitute Dual-SMD,
Jade Max, a generic MX, or a different Jade variant.
