#!/usr/bin/env python3
"""Plan C mechanical / ideal-Main DC preflight. Never writes a design file.

Model assumptions are scenarios, not acceptance limits or measured forces.
In particular the beam is NOT a bound for a plate on four point supports.
"""
from pathlib import Path
import csv
import hashlib
import importlib.util
import itertools
import json
import math
import sys

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
R = E.parents[3]
Q = R / 'hardware/kicad/qualification'
PCB = Q / 'issue-155-main-mounting-stage2/inspection/final/main.kicad_pcb'
PARSER = Q / 'issue-153-main-mounting-stage1/measure.py'
WING = Q / 'issue-141-wing-power-integrity/dc-drop-estimate.json'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    (E / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

spec = importlib.util.spec_from_file_location('measure153', PARSER)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
b = m.parse(PCB)
assert sha(PCB) == 'fdc1a7748f94714e395eb50f3e08c43afa24192ee76eb3d1804a8cba28690222'
fps = {next(p[2] for p in m.children(f, 'property') if p[1] == 'Reference'): f
       for f in m.children(b, 'footprint')}
assert len(fps) == 53 and 'J3' not in fps
holes = {k: list(m.pair(fps[k], 'at')) for k in ['H1', 'H2', 'H3', 'H4']}
assert holes == {'H1': [79., 92.], 'H2': [121., 81.],
                 'H3': [79., 119.], 'H4': [102., 111.5]}
assert list(m.pair(fps['J1'], 'at')) == [85., 81.]
assert list(m.pair(fps['J2'], 'at')) == [110., 116.]

def point_rect(p, box):
    return math.hypot(max(box[0]-p[0], p[0]-box[2], 0),
                      max(box[1]-p[1], p[1]-box[3], 0))

def signed_north_distance(p):
    # Positive on the north / J3 side of the H1--H2 support edge.
    a, c = holes['H1'], holes['H2']
    vx, vy = c[0]-a[0], c[1]-a[1]
    return -(vx*(p[1]-a[1])-vy*(p[0]-a[0])) / math.hypot(vx, vy)

center = [105., 75.325]  # Assumed load datum: header-body midpoint.
origin = [105., 73.]
body = [94.625, 73.2, 115.375, 77.45]
service = [92., 71.5, 118., 79.]
housing = [95.625, 73.25, 114.375, 77.4]  # Centering remains an assumption.
L = signed_north_distance(center)
Lmax = max(signed_north_distance([x,y]) for x in [body[0],body[2]]
           for y in [body[1],body[3]])
back_lever = max(-signed_north_distance(p) for p in holes.values())
beam = []
for force, modulus, width, length in itertools.product(
        [5., 10., 20., 40.], [15000., 20000., 25000.], [5., 20.75, 48.], [L, Lmax]):
    t = 1.2
    inertia = width*t**3/12
    stress = 6*force*length/(width*t**2)
    beam.append(dict(force_N=force, modulus_MPa=modulus, effective_width_mm=width,
                     length_mm=length, thickness_mm=t,
                     deflection_mm=force*length**3/(3*modulus*inertia),
                     slope_rad=force*length**2/(2*modulus*inertia),
                     root_stress_MPa=stress, root_strain_microstrain=stress/modulus*1e6,
                     root_moment_Nmm=force*length))
with (E/'beam-sensitivity.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(beam[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(beam)

grip = []
for d in [6., 8., 10.]:
    p = [housing[2]+d/2, center[1]]
    grip.append(dict(grip_diameter_mm=d,
                     right_grip_to_screw_head_d3_mm=math.dist(p, holes['H2'])-d/2-1.5,
                     right_grip_to_washer_d4_mm=math.dist(p, holes['H2'])-d/2-2.,
                     meaning='Planar projection only. No hand size or compliant-grip qualification'))

mechanical = dict(
    outcome='STOP_MECHANICAL_GATE_UNESTABLISHED',
    adopted_geometry=dict(outline_mm=[76,70,124,122], size_mm=[48,52],
                          J3_origin_mm=origin, J3_rotation_deg=0, holes_mm=holes),
    selected_trial_hardware=dict(
        screw=dict(part='NBK SNZS-M2-6', thread='M2x0.4', length_mm=6,
                   head='precision pan, cross recess No.0', head_diameter_mm=3,
                   head_height_mm=.6, screw_only_max_torque_Nm=.22),
        screw_driver=dict(part='HOZAN D-540-100', tip='No.0', shaft_diameter_mm=4,
                          shaft_length_mm=100, handle_diameter_mm=19.8),
        latch_probe=dict(part='HOZAN P-512-S with P-512S-1', material='PEEK',
                         tip_size_mm=[.4,3.5], tip_length_mm=30,
                         tool_length_mm=140.5, GH_approved=False),
        insulators=dict(status='Proposed custom dimensions; no manufactured part or strength proof',
                        top_washer_OD_ID_thickness_mm=[4.,2.2,.3],
                        underside_threaded_POM_boss_OD_height_mm=[4.,6.],
                        female_thread='M2, proposed usable depth5.0mm',
                        nominal_thread_engagement_mm=6-1.2-.3,
                        nominal_blind_bottom_clearance_mm=5-(6-1.2-.3),
                        nominal_head_top_z_mm=.3+.6,
                        nominal_boss_bottom_z_mm=-1.2-6,
                        combined_radial_error_scenarios_mm=[.1,.2,.3],
                        radial_copper_reservation_margin_mm=[.5-.1,.5-.2,.5-.3],
                        assembly_torque_Nm=None)),
    projections=dict(header_body_mm=body, assumed_housing_mm=housing,
                     retained_stage1_service_rectangle_mm=service,
                     H2_to_service_driver_d4_gap_mm=point_rect(holes['H2'],service)-2,
                     H2_to_header_washer_d4_gap_mm=point_rect(holes['H2'],body)-2,
                     side_grip_scenarios=grip),
    proposed_operation=[
        'Remove USB/power and lid; release cable strain relief before handling.',
        'Fit insulating bosses/washers and screws with GH harnesses removed; driver approaches along +Z. Screw-only torque maximum is not an assembly torque.',
        'For insertion align housing and hold wires across the full pitch; apply axial force with PCB supported locally. Do not use the latch probe as a lever.',
        'For extraction use P-512-S only to depress the lock while holding all14 wires together, keeping them at their natural pitch; fully unlock then pull axially.',
        'Target zero tilt; manufacturer section3.3 permits at most20deg. Latch travel and complete release must be verified with actual housing/tool.',
        'Local underside support alone reacts insertion, not extraction. An edge-retaining fixture must also react upward load; its geometry/contact sites are not yet verified.'
    ],
    cable_scenarios=[dict(straight_rise_mm=s, bend_radius_mm=rad, wire_OD_mm=od,
                          required_z_mm=7.3+s+rad+od/2,
                          assembly_height_reference_mm=7.3)
                     for s,rad,od in itertools.product([0.,2.],[3.,5.,8.],[.76,1.])],
    cable_trial_selection=dict(straight_rise_mm=2., radius_mm=5., OD_mm=1.,
                              resulting_z_mm=14.8, hypothetical_extraction_stroke_mm=6.,
                              resulting_moving_wire_z_mm=20.8,
                              source='Engineering scenarios; NOT a wire bend specification or verified extraction stroke'),
    overhang=dict(load_datum_assumed_mm=center,
                  origin_outside_support_polygon_mm=signed_north_distance(origin),
                  body_center_outside_support_polygon_mm=L,
                  furthest_body_corner_outside_support_polygon_mm=Lmax,
                  deepest_rear_support_lever_mm=back_lever,
                  insertion_minimum_total_rear_uplift_per_unit_load=L/back_lever,
                  static_meaning='Point-support equilibrium: a down load outside H1-H2 needs tensile screw reactions. Ignoring finite boss radii and clamp moments.',
                  beam_model='Illustrative clamped strip: I=b*t^3/12; delta=F*L^3/(3*E*I); sigma=6*F*L/(b*t^2). No plate/torsion/joint model.',
                  beam_rows=len(beam),
                  force_values_are_measured_or_rated=False,
                  actual_laminate_or_stiffness_known=False,
                  beam_is_upper_or_lower_bound=False,
                  actual_force_N=None, verified_board_deflection_mm=None,
                  accepted_solder_strain_limit=None),
    unresolved=[
        'No actual GHR-14V-S latch datum/travel and probe swept solid; the0.4x3.5 tip alone cannot verify lock release or tool-body clearance.',
        'Actual 14-way insertion and unlocked extraction force, local restraint, screw preload/POM thread strength and laminate stiffness are not established.',
        'No qualified wire bend radius, strain-relief position, actual extraction stroke or case/cover model.',
        'Consequently this is mechanical concretization and sensitivity evaluation, NOT a successful3D service/strain qualification.'
    ],
    execution=dict(pcb_writes=0, schematic_writes=0, router_attempts=0,
                   refill_runs=0, independent_new_board_qualifications=0, manufacturing_exports=0))
save('mechanical.json', mechanical)

# Independently rebuild the ideal-Main upper-voltage screen from #141 data,
# not by copying #157's printed worst-case voltage. The branch/copper drop is
# set to ZERO deliberately; these are not new routed resistance estimates.
old = json.loads(WING.read_text())
cases = [s for s in old['results'] if s['variant'] == 'after']
assert len(cases) == 16
rho, alpha = 1.7241e-8, .00393
rows = []
for s, contact, voltage in itertools.product(cases, [.03,.05], [4.75,5.]):
    for label, scale in [('component' if s['sensor_current_A']==.005 else 'envelope',1.),
                         ('planning127mA' if s['sensor_current_A']==.005 else 'allowance278mA',
                          (.127 if s['sensor_current_A']==.005 else .278)/s['supply']['load_A'])]:
        load = s['supply']['load_A']*scale
        wire = rho*.100/(.0804e-6)*(1+alpha*(s['temperature_C']-20))
        harness_loop = (wire+2*contact)*(1+1/6)
        ron = .15 if s['temperature_C']==20 else .25
        wing_drop = s['max_sensor_loop_drop_V']*scale
        fixed = wing_drop+load*harness_loop+2*load*ron
        rows.append(dict(pitch_mm=s['pitch_mm'],temperature_C=s['temperature_C'],
                         width_factor=s['width_factor'],load_case=label,
                         sensor_current_A=s['sensor_current_A']*scale,
                         branch_current_A=load,total_current_A=2*load,
                         source_at_U5_V=voltage,contact_each_ohm=contact,
                         harness_loop_ohm=harness_loop,switch_ohm=ron,
                         wing_drop_V=wing_drop,harness_drop_V=load*harness_loop,
                         switch_drop_V=2*load*ron,main_common_ohm=0.,main_branch_ohm=0.,
                         ideal_Main_sensor_voltage_V=voltage-fixed,
                         common_resistance_budget_for_4V5_ohm=(voltage-4.5-fixed)/(2*load),
                         passes_with_zero_Main_resistance=voltage-fixed>=4.5))
assert len(rows) == 128
with (E/'ideal-main-dc.csv').open('w',newline='') as f:
    w = csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
save('power-preflight.json',dict(
    status='SUPPLEMENTARY_IDEAL_MAIN_SCREEN_ONLY_NOT_ROUTED_QUALIFICATION',
    equation='Vsensor=V_U5_input-2*Ibranch*Ron-Ibranch*Rharness-WingDrop; Main copper set to0ohm',
    rows=len(rows),failed_scenarios=sum(not p['passes_with_zero_Main_resistance'] for p in rows),
    minimum=min(rows,key=lambda p:p['ideal_Main_sensor_voltage_V']),
    planning_minimum=min((p for p in rows if p['load_case']=='planning127mA'),key=lambda p:p['ideal_Main_sensor_voltage_V']),
    envelope_4V75_20C_nominal17=[p for p in rows if p['load_case']=='envelope' and p['pitch_mm']==17 and p['temperature_C']==20 and p['width_factor']==1 and p['source_at_U5_V']==4.75 and p['contact_each_ohm']==.05][0],
    limitations=[
        'Not a regenerated Stage2 board. Actual routed common/branch/return resistance is NOT measured or extracted.',
        '4.75V/5V are sensitivities at U5 input, not guarantees from USB. Actual upstream and Main MCU load are omitted.',
        '125C and11mA are requested sensitivities, not a qualified full-system ambient or a measured component load.',
        'Ron brackets inherited from #157; not a guaranteed interpolated value at4.75V.',
        'Six equal GND harness wires are assumed; contact sharing, crimp loss, transients and ADC behavior remain unverified.',
        'A negative ideal-Main budget identifies a scenario Main widening alone cannot fix under this model. It does not make every scenario infeasible.'
    ]))
save('input-hashes.json',{str(p.relative_to(R)):sha(p) for p in [PCB,PCB.with_suffix('.kicad_pro'),PARSER,WING,
    Q/'issue-157-main-dual-wing-stage1/analyze.py',R/'hardware/tscircuit/src/qualification/JstGh14.tsx']})
print(json.dumps(dict(mechanical_outcome=mechanical['outcome'],overhang_mm=L,
                     beam_rows=len(beam),dc_rows=len(rows),pcb_unchanged=True),indent=2))
