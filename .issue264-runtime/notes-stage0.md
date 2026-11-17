# Stage 0 notes
#261 adopted config: plate 10.90 (s=-2.65 in #248 frontier frame), B=4.70,
cruise Z 2.95 (low) / 6.90 (high, Main entry centreline), sheet modelled
10.2w x 0.25t. Wing ZIF slot (±27.0,-34.2) mouth facing Main (+Y);
Main ZIF J2 centre (23.3,40.8) yaw -43, mouth (20.92,38.24); J3 mirrored
yaw +38, mouth (-20.92,38.24). Route R centreline length 111.2, blank ~120.
Electrical #261: loop 208.5 mOhm -> Vfar 4.785 (designed lanes 1oz Cu,
5V lane 1.0mm = 59 mOhm/120mm, GND 6x0.30 parallel = 32.8, ZIF 50 mOhm).
Gate1 PASS 0; gate3 PASS w/ named residual (channel rim peel 4.49 mm3);
gates 4/5 inheritance; gate 7 PASS.
#248 round13 Candidate D: stock FFC killed for (1) straight vs bent plan
path, (2) lane R unspecified -> guarantee unclosable (on B3 assumed
0.035 mm2 lanes loop ~203 mOhm, dVfar ~-2 mV -> would pass), (3) Wing-side
FH12 actuator in 5.35 cavity, in-situ actuation not demonstrated.
B3: FH12-14S-0.5SH(55) LCSC C5378715 JLC O3919/P3909; 0.5 A/contact,
50 mOhm, FFC tail 0.30+-0.05 mm, flip-lock 20 cycles. Molex 152660149:
same-side tails, 152+-4 mm, active. LCSC generic: SHOU HAN
FFC-0.5-14P-150mm C6936336 (stock unverified, not prequalified).
Fold geometry fact: a single ribbon fold turns heading by 2*gamma
(gamma = fold-line angle to strip axis); small turns = long diagonal
fold lines + triangular doubled zones; folds flip contact face (over or
under both flip); vertical bends do not flip.
