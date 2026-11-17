rho = 1.72e-8        # copper resistivity, Ohm*m
L = 0.152            # full strip length, m (conservative: whole cable in the 5V path)
Rc = 0.050           # FH12 contact resistance per mating, Ohm (datasheet max class)
# Anchor: Issue 261 extraction - loop 208.5 mOhm -> Vfar 4.785 V; slope -127 mA per ohm of loop
def vfar(loop_mohm): return 4.785 - 0.127 * (loop_mohm - 208.5) / 1000.0
for name, A in (('B3 assumed 0.035 mm2', 0.035e-6), ('pessimistic 0.026 mm2', 0.026e-6), ('extreme 0.020 mm2', 0.020e-6)):
    Rlane = rho * L / A * 1000  # mOhm
    p5v = 2 * Rc * 1000 + Rlane
    gnd = (2 * Rc * 1000 + Rlane) / 6.0   # six GND lanes in parallel
    loop = p5v + gnd
    print(f'{name}: R_lane={Rlane:.1f} mOhm, 5V path={p5v:.1f}, GND path={gnd:.1f}, loop={loop:.1f} mOhm, Vfar={vfar(loop):.3f} V (margin {vfar(loop)-4.60:+.3f})')
# Acceptance: Vfar >= 4.60  <=>  loop <= 208.5 + (4.785-4.60)/0.127*1000
loop_max = 208.5 + (4.785 - 4.60) / 0.127 * 1000
# loop = (100 + R) + (100 + R)/6 = 7/6 (100 + R)  ->  R <= loop_max*6/7 - 100
R_max = loop_max * 6 / 7 - 100
print(f'loop acceptance <= {loop_max:.0f} mOhm  ->  single-lane acceptance R_lane <= {R_max:.0f} mOhm = {R_max/1000:.2f} Ohm (set 1.30 Ohm with margin)')
