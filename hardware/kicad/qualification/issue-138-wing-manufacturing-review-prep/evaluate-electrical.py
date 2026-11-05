#!/usr/bin/env python3
"""Reproducible DC current/thermal screening, not an IPC-2152 simulation.

Formula: IPC-2221 curve fit as documented by TI TIDA-01232, p9 eq7,
and Qorvo's PCB Trace Power Handling Calculator. No cooling benefit assumed.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
width, copper = 0.08, 0.035  # finished mm, external 1oz approximated as 35um
area = width * copper / 0.0254 ** 2  # square mil
capacity = 0.048 * 10 ** 0.44 * area ** 0.725  # external, 10K screening target


def delta_t(current):
    return (current / (0.048 * area ** 0.725)) ** (1 / 0.44)


scenarios = []
for label, sensor_ma, mux_ua, note in [
    ('3.3V-datasheet-table', 4, 1.5, 'DRV5055 RevC table at 3.3V; board net is HALL_5V, comparison only'),
    ('5V-datasheet-table', 5, 2.7, 'DRV5055 RevC table at 5.0V, B=0mT; TMUX1208 RevC 5V table maximum'),
    ('conservative-10mA-envelope', 10, 2.7, 'Engineering envelope, NOT a RevC maximum specification; exceeds Fig5-13 typical curves'),
    ('envelope-plus-output-loads', 11, 2.7, '10mA per sensor plus 1mA output source per sensor; all 21 simultaneously is conservative'),
]:
    sensor = 21 * sensor_ma * 1e-3
    mux = 3 * mux_ua * 1e-6
    total = sensor + mux
    scenarios.append(dict(label=label, per_sensor_ma=sensor_ma, per_mux_ua=mux_ua,
                          sensors_A=sensor, muxes_A=mux, supply_A=total, return_A=total,
                          capacity_A=capacity, capacity_to_current_ratio=capacity / total,
                          predicted_rise_K=delta_t(total), below_10K_screen=total < capacity, note=note))

# Any individual power/GND segment is bounded by the ENTIRE Wing load.
# Do not divide by 21 or by the number of vias without a solved branch circuit.
nets = json.loads((OUT / 'net-widths.json').read_text())
net_checks = []
for n in nets:
    if n['role'] in ('power', 'GND'):
        bound = scenarios[-1]['supply_A']
        reason = 'Entire Wing envelope, no branch-current or plane benefit credited'
    elif n['net'].startswith('MUX_A') or n['net'] == 'WING_EN':
        bound = 3 * 0.10e-6
        reason = 'Three TMUX logic inputs, 0.10uA max per input; switching transient excluded'
    else:
        bound = 1e-3
        reason = 'DRV5055 recommended output drive +/-1mA; external ADC load must remain within this'
    net_checks.append(dict(cell=n['cell'], net=n['net'], role=n['role'], width_mm=n['min_width_mm'],
                           worst_width_mm=n['worst_width_mm'], screening_current_A=bound,
                           capacity_A=capacity, below_10K_screen=bound < capacity, reason=reason))

result = dict(
    method='IPC-2221 external conductor curve fit; not an IPC-2152 solver or manufacturing approval',
    formula='I[A] = 0.048 * deltaT[K]^0.44 * A[mil^2]^0.725',
    references=[
        'https://www.ti.com/lit/ug/tiducs7/tiducs7.pdf (p9, eq7)',
        'https://www.qorvo.com/design-hub/design-tools/interactive/pcb-trace-power-handling-calculator',
        'https://www.ti.com/lit/ds/symlink/drv5055.pdf (SBAS640C, p5, p9, p4)',
        'https://www.ti.com/lit/ds/symlink/tmux1208.pdf (SCDS389C, p6, p8, p5)',
    ],
    assumptions=dict(finished_width_mm=width, copper_thickness_mm=copper, external_layers=True,
                     area_mil2=area, allowed_rise_K=10, capacity_A=capacity,
                     rho_20C_ohm_m=1.7241e-8, resistance_ohm_per_m=1.7241e-8/(width*1e-3*copper*1e-3),
                     resistance_increase_due_to_width_tolerance_percent=25,
                     ambient_or_other_heat_sources_not_qualified=True),
    scenarios=scenarios, net_checks=net_checks,
    tmux=dict(count=3, supply_max_5V_ua_each=2.7, supply_max_3V3_ua_each=1.5,
              supply_test_conditions='Logic inputs = 0V or 5.5V; -40 to +125C',
              current_per_channel_abs_max_A=0.03,
              channel_check='1mA sensor output screen is 30x below 30mA absolute maximum; do not treat 30mA as operating target',
              logic_leakage_max_ua_each=0.10,
              caveat='3.3V logic at VDD=5V and switching can increase IDD beyond rail-input table test condition; not characterized here'),
    exclusions=['Copper thickness tolerance/etch profile beyond assumed 35um',
                'Connector/cable/Main regulator resistance and supply tolerance',
                'Power-on inrush, shorts/faults, capacitive ADC sampling and control switching',
                'Analog accuracy, settling, crosstalk, thermal environment and simultaneous heating',
                'DRV5055 RevC current-table vs typical-curve inconsistency; engineering envelope is not vendor clarification'],
)
assert all(n['below_10K_screen'] for n in net_checks)
(OUT / 'electrical-evaluation.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
print(json.dumps(dict(capacity_A=capacity, scenarios=scenarios), indent=2))
