"""Per-variant Wing-side worst-sensor drop from resistance-extraction.json
(corner: fine mesh 0.015, width factor 0.8, scaled 20C -> 125C), and the
configuration Vfar with the #141 Wing term (184.7 mV, backed out of the
published Rev.8-native pair 4.754/4.770 V and verified on both) replaced
by the measured per-variant drop. All other terms unchanged."""
import json
from pathlib import Path
E = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
SCALE = 1 + 0.00393 * 105
out = {}
for name in ('wing-rev5-16mm-left', 'wing-rev5-16mm-right', 'wing-rev5-17mm-left', 'wing-rev5-17mm-right'):
    e = json.loads((E / name / 'resistance-extraction.json').read_text())
    rows = {(r['net'], r['max_triangle_area_mm2'], r['track_width_factor']): r['result_at_20C'] for r in e['rows']}
    h5 = rows[('HALL_5V', 0.015, 0.8)]['terminal_voltage_V']
    gn = rows[('GND', 0.015, 0.8)]['terminal_voltage_V']
    sensors = sorted({k.rsplit('.', 1)[0] for k in h5 if k.startswith('U_H')})
    worst = 0.0; worst_s = None
    for s in sensors:
        d = abs(h5.get(f'{s}.1', 0.0)) + abs(gn.get(f'{s}.3', 0.0))
        if d > worst:
            worst, worst_s = d, s
    drop125 = worst * SCALE
    vfar = 4.754 + 0.1847 - drop125
    out[name] = dict(worst_sensor=worst_s, wing_drop_20C_V=round(worst, 4), wing_drop_125C_V=round(drop125, 4),
                     vfar_J3worst_V=round(vfar, 3))
    print(f'{name}: worst {worst_s} drop20 {worst*1000:.1f} mV -> 125C {drop125*1000:.1f} mV; Vfar {vfar:.3f} V')
json.dump(out, open('/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime/r2-vfar.json', 'w'), indent=2)
print('done')
