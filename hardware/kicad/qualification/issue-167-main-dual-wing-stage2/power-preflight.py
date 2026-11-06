#!/usr/bin/env python3
"""Bounded supply feasibility calculation; no PCB/router/manufacturing writer.

Python 3 stdlib only. All outputs belong to this evidence directory.
Sensitivity parameters are not measured or guaranteed component limits.
"""
from pathlib import Path
import csv
import itertools
import json
import math

E = Path(__file__).resolve().parent
R = E.parents[3]


def save(name, value):
    (E / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def table(name, rows):
    with (E / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def input_voltage(source, resistance, power, other):
    # Converter is constant INPUT POWER Pout/eta. Main is a separate current
    # sink through this simplified shared loop. Choose the high-voltage root.
    a = source - resistance * other
    disc = a*a - 4*resistance*power
    if disc < 0:
        return None
    return (a + math.sqrt(disc)) / 2


old = json.loads((R / 'hardware/kicad/qualification/issue-157-main-dual-wing-stage1/main-resistance.json').read_text())
old_r = next(x['resistance_ohm'] for x in old['results'] if
             x['net'] == 'VBUS' and x['temperature_C'] == 125 and x['width_factor'] == .8)
rows = []
for branch, rail, eta in itertools.product([.127, .2310081, .278], [5.2, 5.304], [1., .95, .9, .85, .8]):
    power = 2*branch*rail
    converter = power/(4.75*eta)
    rows.append(dict(branch_A=branch, rail_V=rail, efficiency=eta,
        output_W=power, converter_input_at_4V75_A=converter,
        remaining_other_Main_at_USB_100mA_A=.1-converter,
        remaining_other_Main_at_USB_500mA_A=.5-converter,
        converter_loss_W=power*(1/eta-1),
        scope='design' if branch == .127 else 'stress-only'))
table('current-budget.csv', rows)

# Reproduce ALL 12 previous converter rows independently; this is an arithmetic
# check, not an assumption that those efficiencies are guaranteed in forced PWM.
previous = list(csv.DictReader((E / 'inputs/issue-165-converter-power.csv').open()))
for p in previous:
    r = next(x for x in rows if x['branch_A'] == float(p['branch_A']) and
             x['rail_V'] == 5.2 and x['efficiency'] == float(p['efficiency']))
    assert abs(r['converter_input_at_4V75_A']-float(p['converter_input_A'])) < 1e-12

sweep = []
for branch, rail, eta, source, upstream, pcb, other in itertools.product(
    [.127, .2310081, .278], [5.2, 5.304], [.8, .85, .9, .95, 1.],
    [4.75, 5., 5.25], [0., .1, .25, .5], [0., .05, old_r], [0., .05, .1, .15]):
    power = 2*branch*rail/eta
    resistance = upstream+pcb
    vin = input_voltage(source, resistance, power, other)
    current = power/vin+other if vin else None
    required_source = 4.75+resistance*(power/4.75+other)
    # Independently check KVL, constant power and source requirement.
    if vin:
        assert abs(vin-(source-resistance*current)) < 1e-12
        assert abs((current-other)*vin-power) < 1e-12
    assert abs(input_voltage(required_source, resistance, power, other)-4.75) < 1e-12
    sweep.append(dict(branch_A=branch, rail_V=rail, efficiency=eta,
        source_V=source, upstream_loop_ohm=upstream, pcb_loop_ohm=pcb,
        other_Main_A=other, converter_input_V=vin, USB_current_A=current,
        required_source_for_converter_4V75_V=required_source,
        input_4V75_met=vin is not None and vin >= 4.75-1e-12,
        note='all R/Main/eta values are sensitivities; old PCB R is positive path only'))
table('upstream-sensitivity.csv', sweep)

wing = json.loads((R / 'hardware/kicad/qualification/issue-141-wing-power-integrity/dc-drop-estimate.json').read_text())
downstream = []
for w in wing['results']:
    if w['variant'] != 'after':
        continue
    base = w['supply']['load_A']
    branch = .127 if w['sensor_current_A'] == .005 else .278
    # Also retain raw 11 mA/sensor envelope; 278 mA includes planning allowance.
    for load in ([branch] if branch == .127 else [base, branch]):
        wire = 1.7241e-8*.100/(.0804e-6)*(1+.00393*(w['temperature_C']-20))
        harness = (wire+2*.05)*(1+1/6)
        ron = .15 if w['temperature_C'] == 20 else .25
        wingdrop = w['max_sensor_loop_drop_V']*load/base
        for common, branch_r in [(0., 0.), (.05, .05)]:
            local = 5.2*.98-.05-2*load*(ron+common)-load*(harness+branch_r)-wingdrop
            downstream.append(dict(pitch_mm=w['pitch_mm'],temperature_C=w['temperature_C'],
                width_factor=w['width_factor'],branch_A=load,Main_common_ohm=common,
                Main_branch_ohm=branch_r,rail_floor_V=5.2*.98-.05,
                farthest_sensor_V=local,margin_to_4V60_V=local-4.60,
                scope='conditional target calculation ONLY; Main R NOT extracted',
                load_scope='design' if branch == .127 else 'stress-only'))
table('conditional-downstream.csv', downstream)

example = next(x for x in sweep if x['branch_A'] == .127 and x['rail_V'] == 5.2 and
    x['efficiency'] == .8 and x['source_V'] == 4.75 and x['upstream_loop_ohm'] == .1
    and x['pcb_loop_ohm'] == .05 and x['other_Main_A'] == .1)
save('power-preflight.json', dict(
    status='STOP: converter input 4.75 V cannot be guaranteed from unspecified USB upstream',
    equations=dict(Pin='2*Iwing*Vrail/eta',
        KVL='Vin=Vsource-(Rupstream+Rpcb)*(Pin/Vin+Iother)',
        required_source='4.75+(Rupstream+Rpcb)*(Pin/4.75+Iother)'),
    counterexample=example,
    mathematical_obstruction='At source=4.75 V, Pin>0 and Rloop>0 imply Vin<4.75 V, even with eta=1 and Iother=0. Reducing positive resistance cannot make it zero.',
    source_status='No specified higher minimum source or bounded cable was provided at assessment; USB-C connector alone is not a higher supply contract.',
    sweep_rows=len(sweep), current_rows=len(rows), downstream_rows=len(downstream),
    previous_converter_rows_reproduced=len(previous), old_partial_VBUS_R_ohm=old_r,
    limitations=['No revised PCB or actual routed Main resistance',
        'Efficiency and other Main currents are sensitivities, not guaranteed operating bounds',
        'Actual USB descriptors, granted current and Main maximum current are not qualified',
        'Downstream rail-floor calculations require the input condition to be met',
        'No whole-product thermal/noise/startup or ADC qualification']))
print(json.dumps(example, indent=2))
