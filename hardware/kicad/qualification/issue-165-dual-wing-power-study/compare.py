#!/usr/bin/env python3
"""Architecture-only DC sensitivity study; Python stdlib; writes here only.

Run from any directory. Retains #141's distributed-load solutions, temperature,
manufacturing width sensitivity, cable/contact assumptions and #157 Ron bracket.
Alternative current and copper multipliers are explicit design targets, not
measurements or qualified component maxima. No EDA files are written.
"""
from pathlib import Path
import csv
import hashlib
import itertools
import json

E = Path(__file__).resolve().parent
R = E.parents[3]
Q = E.parent


def save(name, obj):
    (E / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def write_csv(name, rows):
    with (E / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def cable(temp, contact, returns):
    wire = 1.7241e-8 * .100 / (.0804e-6) * (1 + .00393 * (temp - 20))
    return (wire + 2 * contact) * (1 + 1 / returns)


wing_path = Q / 'issue-141-wing-power-integrity/dc-drop-estimate.json'
old = json.loads(wing_path.read_text())
wing_cases = [s for s in old['results'] if s['variant'] == 'after']
assert len(wing_cases) == 16
# #157 reproduction independently recomputes every CSV row, including one-Wing,
# six/one returns, all four loads, ideal and nonzero Main resistance.
previous = list(csv.DictReader((Q / 'issue-157-main-dual-wing-stage1/dual-wing-dc.csv').open()))
errors = []
for p in previous:
    s = next(s for s in wing_cases if s['pitch_mm'] == int(p['pitch_mm'])
             and s['temperature_C'] == int(p['temperature_C'])
             and s['width_factor'] == float(p['width_factor'])
             and s['sensor_current_A'] == (.005 if p['load_case'] in
                                           ['component-5mA', 'planning-127mA'] else .011))
    i = float(p['branch_A'])
    wd = s['max_sensor_loop_drop_V'] * i / s['supply']['load_A']
    rh = cable(s['temperature_C'], float(p['contact_ohm']), int(p['return_conductors']))
    ron = .15 if s['temperature_C'] == 20 else .25
    loss = wd + i * rh + int(p['wings']) * i * (ron + float(p['main_common_loop_ohm']))
    errors.append(abs(4.75 - loss - float(p['local_at_source_4V75_V'])))
assert len(errors) == 768 and max(errors) < 1e-12

# Fixed input conditions apply to every architecture. Rail replacements are
# downstream of this same 4.75/5/5.25V converter-input boundary.
architectures = [
    # name, rail floor, active Wings, common switch count, branch switch count,
    # Wing resistance multiplier, optional replacement branch current, minimum.
    ('baseline', None, 2, 1, 0, 1., None, 4.5),
    ('regulated5V2', 5.2 * .98 - .05, 2, 1, 0, 1., None, 4.5),
    ('boost_low_cost_2V7pct', 5.2 * .973 - .05, 2, 1, 0, 1., None, 4.5),
    ('duty_replace_common', None, 1, 0, 1, 1., None, 4.5),
    ('duty_keep_common', None, 1, 1, 1, 1., None, 4.5),
    ('current_target96mA', None, 2, 1, 0, 1., .096, 4.5),
    ('regulated3V3_same127mA', 3.3 * .98 - .03, 2, 1, 0, 1., None, 3.),
    ('regulated3V3_target101mA', 3.3 * .98 - .03, 2, 1, 0, 1., .101, 3.),
    ('copper_half', None, 2, 1, 0, .5, None, 4.5),
    ('regulated5V2_copper_half', 5.2 * .98 - .05, 2, 1, 0, .5, None, 4.5),
    ('duty_replace_copper_half', None, 1, 0, 1, .5, None, 4.5),
    ('regulated3V3_target101mA_copper_half', 3.3 * .98 - .03, 2, 1, 0, .5, .101, 3.),
    ('ideal_copper_floor', None, 2, 1, 0, 0., None, 4.5),
]
rows = []
for s, contact, returns, vin, main, load_name in itertools.product(
        [s for s in wing_cases if s['sensor_current_A'] == .005],
        [.03, .05], [6, 1], [4.75, 5., 5.25],
        [(0., 0.), (.25, 0.), (.5, 0.), (.05, .05)],
        ['planning127mA', 'envelope11mA', 'allowance278mA']):
    if load_name == 'planning127mA':
        src, load = s, .127
    else:
        src = next(a for a in wing_cases if a['sensor_current_A'] == .011
                   and all(a[k] == s[k] for k in ['pitch_mm', 'temperature_C', 'width_factor']))
        load = src['supply']['load_A'] if load_name == 'envelope11mA' else .278
    rho_wing = src['max_sensor_loop_drop_V'] / src['supply']['load_A']
    rh = cable(s['temperature_C'], contact, returns)
    ron = .15 if s['temperature_C'] == 20 else .25
    rc, rb = main
    for name, rail, active, nc, nb, k, replacement_i, limit in architectures:
        # A reduced-load claim applies ONLY to its separately declared target;
        # preserve unchanged 11mA/278mA envelope for every architecture.
        current = replacement_i if replacement_i and load_name == 'planning127mA' else load
        source = vin if rail is None else rail
        switch_drop = current * ron * (active * nc + nb)
        main_drop = current * (active * rc + rb)
        wd = current * rho_wing * k
        vh = current * rh
        v = source - switch_drop - main_drop - wd - vh
        budget = source - switch_drop - wd - vh - limit
        rows.append(dict(architecture=name, load_case=load_name, pitch_mm=s['pitch_mm'],
                         temperature_C=s['temperature_C'], width_factor=s['width_factor'],
                         contact_each_ohm=contact, return_conductors=returns, input_V=vin,
                         source_floor_V=source, active_wings=active, branch_current_A=current,
                         main_common_ohm=rc, main_branch_ohm=rb, switch_bracket_ohm=ron,
                         wing_resistance_factor=k, switch_drop_V=switch_drop,
                         main_drop_V=main_drop, harness_drop_V=vh, wing_drop_V=wd,
                         sensor_voltage_V=v, operating_minimum_V=limit,
                         dc_margin_V=v-limit, main_voltage_budget_V=budget,
                         equivalent_common_resistance_budget_ohm=budget/(active*current)))
write_csv('sensitivity.csv', rows)
primary = [p for p in rows if p['load_case'] == 'planning127mA' and p['pitch_mm'] == 17
           and p['temperature_C'] == 125 and p['width_factor'] == .8
           and p['contact_each_ohm'] == .05 and p['return_conductors'] == 6 and p['input_V'] == 4.75]
write_csv('primary.csv', primary)
reference = next(p for p in primary if p['architecture'] == 'baseline' and p['main_common_ohm'] == 0)
assert abs(reference['sensor_voltage_V'] - 4.519484789226132) < 1e-12
envelope = next(p for p in rows if p['architecture'] == 'baseline' and p['load_case'] == 'envelope11mA'
                and p['pitch_mm'] == 17 and p['temperature_C'] == 20 and p['width_factor'] == 1
                and p['contact_each_ohm'] == .05 and p['return_conductors'] == 6
                and p['input_V'] == 4.75 and p['main_common_ohm'] == 0)
assert abs(envelope['sensor_voltage_V'] - 4.494196008389493) < 1e-12
assert len(rows) == 14976

# Current thresholds are load-shape sensitivities under exactly the primary
# copper/contact/temperature conditions, not sensor part specifications.
rw = reference['wing_drop_V'] / .127
thresholds = []
for active, switches in [(2, 2), (1, 1), (1, 2)]:
    for rc in [0., .25]:
        r = rw + cable(125, .05, 6) + switches * .25 + active * rc
        thresholds.append(dict(active_wings=active, switch_series_multiplier=switches,
                               main_common_ohm=rc, max_current_for_4V5_A=.25/r,
                               max_current_with_50mV_reserve_A=.20/r))

# 5.2V rail input power sensitivity: efficiency is a scenario, not a data-sheet
# guarantee. Covers original stress loads without quietly cutting their current.
power = []
for i, eta in itertools.product([.127, .2310081, .278], [.8, .85, .9, .95]):
    pout = 5.2 * 2 * i
    power.append(dict(branch_A=i, efficiency=eta, output_W=pout,
                      converter_input_A=pout/(4.75*eta), converter_loss_W=pout*(1/eta-1)))
write_csv('converter-power.csv', power)
timing = []
for power_wait_us, hall_wait_us in itertools.product([1950, 100, 50], [0, 300, 1000]):
    # 300/1000us are deliberate study assumptions: Rev.C has no numerical tON
    # bound in electrical table. 1950us is switch typical, not a guaranteed max.
    frame = 2 * (power_wait_us + hall_wait_us + 7*(1 + 50 + 3*2))
    timing.append(dict(power_wait_us=power_wait_us, hall_wait_assumption_us=hall_wait_us,
                       frame_us=frame, frames_per_s=1e6/frame))
write_csv('duty-timing.csv', timing)

# Concrete primary-condition companion to the optimistic uniform half factor.
# Derived from the unchanged #141 graph, with fixed pad/via resistors retained.
cp = E / 'copper-study.json'
if cp.exists():
    c = json.loads(cp.read_text())
    combinations = []
    fixed_conditions = [p for p in rows if p['pitch_mm'] == 17
                        and p['temperature_C'] == 125 and p['width_factor'] == .8
                        and p['contact_each_ohm'] == .05 and p['input_V'] == 4.75]
    for p in fixed_conditions:
        if p['wing_resistance_factor'] != .5:
            continue
        actual = next(x for x in c['results'] if x['pitch_mm'] == p['pitch_mm']
                      and x['conductance_multiplier'] == 2.)
        a = dict(p)
        a['architecture'] = a['architecture'].replace('copper_half', 'track_conductance_x2_fixed_pad_via')
        a['wing_resistance_factor'] = actual['wing_drop_ratio']
        a['wing_drop_V'] = p['wing_drop_V'] * actual['wing_drop_ratio'] / .5
        delta = a['wing_drop_V'] - p['wing_drop_V']
        for key in ['sensor_voltage_V', 'dc_margin_V', 'main_voltage_budget_V']:
            a[key] = p[key] - delta
        a['equivalent_common_resistance_budget_ohm'] = a['main_voltage_budget_V'] / (a['active_wings']*a['branch_current_A'])
        combinations.append(a)
    write_csv('primary-fixed-pad-via.csv', combinations)

save('model.json', dict(
    status='ARCHITECTURE_SENSITIVITY_ONLY_NOT_DESIGN_QUALIFICATION',
    equation='Vlocal=Vrail-I*(Nactive*Ncommon_switch+Nbranch_switch)*Ron-I*(Nactive*Rc+Rb)-I*Rh-I*Rw*k',
    reference_boundary='U5 VIN to Main GND; same boundary becomes regulator input in replacement architectures',
    input_wing_sha256=hashlib.sha256(wing_path.read_bytes()).hexdigest(),
    rows=len(rows), reproduced_157_rows=len(errors), max_reproduction_error_V=max(errors),
    baseline=reference, envelope_20C_nominal=envelope, thresholds=thresholds,
    rail5V2=dict(nominal_V=5.2, dc_tolerance=.02, one_sided_ripple_transient_V=.05,
                minimum_V=5.2*.98-.05, maximum_V=5.2*1.02+.05),
    rail3V3=dict(nominal_V=3.3, dc_tolerance=.02, one_sided_ripple_transient_V=.03,
                minimum_V=3.3*.98-.03, maximum_V=3.3*1.02+.03),
    limitations=[
        'Regulation tolerance, ripple, target current and copper multiplier are requirements to prove, not measured results.',
        'Off Wing voltage is zero; duty values apply only to settled on-window.',
        'Current targets apply only to separate planning rows; envelopes are unchanged.',
        '3.3V Ron bracket inherited for comparison, not a guaranteed spec across 3.0-3.63V.',
        'Main resistance scenarios are downstream lumped supply/return; upstream source losses excluded.',
        'All 21 Hall and three MUX loads are retained. Replacement load shape is linearized.',
        'Uniform half-copper factor is an optimistic sensitivity pending fixed-topology resistor study.',
        'Copper zero is an unattainable mathematical ceiling on voltage, not a manufactured design.',
        'Constant-current DC, no transient simulation or field solver; unequal returns have only one-return stress bracket.',
        '4.75V is a specified study boundary, not a USB-to-product minimum guarantee.'
    ]))
print(json.dumps({'rows': len(rows), 'reproduced': len(errors), 'baseline_V': reference['sensor_voltage_V'],
                  'baseline_budget_mV': reference['main_voltage_budget_V']*1000}, indent=2))
