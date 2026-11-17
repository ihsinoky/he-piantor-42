# Matrix Rev.4 — JLCPCB order CPL / Issue #268

The CPL to hand to the JLCPCB placement viewer together with the Gerber set is
[`CPL-jlcpcb-gerber-frame.csv`](CPL-jlcpcb-gerber-frame.csv).
It is derived from the Matrix Rev.3 gerber-frame CPL (Issue #219 method):
all 42 non-connector rows are carried over unchanged — Rev.4 footprint
positions were verified identical to Rev.3 for every footprint except
`J_WING` (full census diff, see `../REPORT.md`). Only the `J_WING` row is new.

- Units mm, X right / Y up. Gerber frame = KiCad frame via `(X, -Y)`;
  vs the legacy KiCad-frame CPL the offset is `(+36.000000, -140.000000)`.
- Edge_Cuts line-centre extent in this frame: `[36, -140, 164, -60]` mm
  (unchanged from Rev.3; outline verified identical, segment for segment).
- Row count 43; row order and Designator set identical to Rev.3.

## J_WING row (new in Rev.4)

`J_WING,100.000000mm,-134.400000mm,bottom,180.000000`

- The Rev.3 GH14 header (top side) is replaced by a Hirose
  FH12-14S-0.5SH(55) bottom-contact ZIF on the **bottom** side.
- Centroid = housing body centre, as with the Rev.3 GH14 convention:
  the footprint courtyard spans KiCad y 131.675..137.125 at x centre 100.000,
  so the body centre is KiCad (100.000, 134.400) — i.e. the footprint origin
  (100, 133) + (0, +1.40) — which maps to (100.000000, -134.400000) in the
  gerber frame. Signal pads sit at KiCad y = 132.000, pad 1 east
  (103.250) descending to pad 14 west (96.750).
- Rotation 180.000000 is the KiCad placed orientation of the flipped
  footprint. Assembler-library rotation / pin-1 acceptance for this
  bottom-side part is an order-time check (see `quote-handoff.md`).

No upload or order has been made with this file.
