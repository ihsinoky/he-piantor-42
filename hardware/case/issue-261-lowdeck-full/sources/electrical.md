# Issue #261 electrical — FPC lane design + Vfar (analytic, Stage 1)

FPC: 1-layer, 1 oz Cu (35 um), rho = 1.72e-8 ohm·m.
Path length per side (patterned centreline): ~118 mm (under-Wing westward
run + strip climb + approach; longer than the GH route's span because the
FPC takes the west corridor). Use L = 120 mm conservative.

Lane plan (14 lanes, 0.5 mm pitch base grid; power lanes widened by
merging grid slots):
- HALL_5V: 1 lane widened to 1.0 mm -> A = 0.0350 mm2
  R = rho*L/A = 1.72e-8*0.120/3.50e-8 = 59.0 mOhm
- GND: 6 lanes x 0.30 mm -> A each 0.0105 mm2, R each 196.6 mOhm,
  parallel = 32.8 mOhm
- Signals (A0,A1,A2,EN,OUT_A,OUT_B,OUT_C): 0.30 mm lanes, R 196.6 mOhm
  (uA-mA class currents; no drop concern)

ZIF contacts (FH12 class, B3 record): 50 mOhm/contact.
- 5V path contacts: 2 (Wing ZIF + Main ZIF) = 100 mOhm
- GND path contacts: 2 per lane, 6 lanes parallel = 16.7 mOhm

Loop (5V out + GND return):
  (100 + 59.0) + (16.7 + 32.8) = 208.5 mOhm
GH baseline harness loop (#252 extraction): 143.0 mOhm
Delta = +65.5 mOhm -> extra drop at 127 mA = 8.3 mV
Vfar = 4.792958 (Rev.7 qualified, baseline harness) - 0.0083
     = 4.785 V >= 4.60 V  PASS, margin +185 mV

Current checks: HALL_5V lane 127 mA < FH12 0.5 A/contact PASS;
lane current density 127 mA / 0.035 mm2 — fine for FPC power lane class.
Main-side copper invariant: Rev.8 keeps Rev.7 power extraction except the
J2/J3 site (local re-route); the <=50 mOhm Main targets are a Stage-1
board-verification item, not changed by this calc.
