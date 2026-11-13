# E-R aluminium plate manufacturing notes — Issue #232

Package for quotation/review only. **Plate order is a PO gate.** Four distinct
parts: 16mm left/right and 17mm left/right; do not scale or mirror one part to
make another. DXFs use millimetres in assembly XY (X right, Y south, viewed
from above). STEP contains the thickness and underside aperture lead-ins.

- Material: aluminium **5052-H32**, nominal **1.50 mm**, accepted finished
  thickness **1.45–1.51 mm** at every clip-bearing flat. No 1.6 mm substitution.
- Plate bottom datum Z14.70; top datum Z16.20. Flatness **≤0.10 mm** over each
  plate, before clamping. Inspect the actual installed plate/rim step as well.
- 21 switch apertures per plate: **14.02 mm nominal**, finished opposing-flat
  dimensions **14.00–14.04 mm**, **R0.20** inside corners. **C0.20 ×45° underside
  lead-in only**, retaining the top seating edge. Aperture centres/angles are
  independently sourced from #230 for every pitch/hand. STEP bottom opening is
  14.42 mm and blends to the finished aperture at Z14.90.
- Four through tie holes **Ø2.20 mm**, at the unchanged H1–H4 sites. Drawing
  general hole/position tolerance ±0.05 mm unless a tighter aperture tolerance
  is stated. Keep washers and screw heads entirely outside the south palm band.
- Exterior follows the smooth D-037 silhouette, inset **1.20 mm**. Printed rim
  width **1.00 mm** gives **0.20 mm nominal assembly seam**. The central Main/Fly
  service bay stays open. **No Wing connector notch, finger notch or semicircle**
  is cut into any plate. Main/Fly service access is a plate boundary, not a
  clearance notch around a Wing connector.
- DXF polylines approximate offset curves to ≤0.01 mm; radiused aperture
  polylines have <0.001 mm chord deviation. STEP is the 3D machining reference.
  The dimensions and tolerances in these notes govern over tessellation.
- Deburr both faces, remove dross, clean and inspect every aperture; no raised
  burrs or sharp palm-facing edges. Smooth the perimeter without rounding the
  switch clip seats. Break exposed outer edges ≤0.10 mm. Do not add coatings
  whose thickness moves the finished apertures or stock outside acceptance.
  Any anodizing/finish is included in the **finished** dimensions. No conductive
  swarf, adhesive residue or burr may bridge to the board.
- Use a specialist process that can guarantee the finished flat dimensions;
  ordinary laser kerf tolerance alone is not acceptance. Cut a narrow-web fit
  coupon in the same stock/process and qualify both Jade Pro clips before the
  plate pair. Record thickness, flatness, all 42 apertures and eight tie holes.

The broad south shelf is backed by the raised original solid shelf at Z14.70;
it needs no new fastener or screw head in the palm contact area. The perimeter
ledge and original four Wing ties provide support and uplift retention. Nominal
coplanarity does not compensate for a warped sheet or a poorly calibrated print:
finish/fit the seating surface and reject assemblies that fail the physical gauges.
