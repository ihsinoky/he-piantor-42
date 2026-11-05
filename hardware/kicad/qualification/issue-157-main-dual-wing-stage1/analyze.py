#!/usr/bin/env python3
"""Read-only Stage 1 survey. No PCB writer, router, refill or CAM export.

Run from any directory with Python 3 (stdlib only). Outputs only in this new
evidence directory. Source parser is reused read-only from Issue 153.
"""
from pathlib import Path
import csv
import copy
import hashlib
import importlib.util
import itertools
import json
import math
import sys

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
R = E.parents[3]
PCB = R / 'hardware/kicad/qualification/issue-155-main-mounting-stage2/inspection/final/main.kicad_pcb'
PROJECT = PCB.with_suffix('.kicad_pro')
OLD = R / 'hardware/kicad/qualification/issue-141-wing-power-integrity/dc-drop-estimate.json'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    (E / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

spec = importlib.util.spec_from_file_location('survey153', R / 'hardware/kicad/qualification/issue-153-main-mounting-stage1/measure.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
root = m.parse(PCB)
before = digest(PCB)
assert before == 'fdc1a7748f94714e395eb50f3e08c43afa24192ee76eb3d1804a8cba28690222'
fps, pads = [], []
for f in m.children(root, 'footprint'):
    props = {p[1]: p[2] for p in m.children(f, 'property')}
    ref = props['Reference']
    at = m.child(f, 'at')
    xy = list(map(float, at[1:3]))
    angle = float(at[3]) if len(at) > 3 else 0
    fp_pads = []
    for p in m.children(f, 'pad'):
        dx, dy = m.rot(*m.pair(p, 'at'), angle)
        pat = m.child(p, 'at')
        pa = float(pat[3]) if len(pat) > 3 else 0
        w, h = m.pair(p, 'size')
        px, py = xy[0] + dx, xy[1] + dy
        corners = [m.rot(x, y, pa) for x in [-w/2, w/2] for y in [-h/2, h/2]]
        box = [min(x for x,y in corners)+px, min(y for x,y in corners)+py,
               max(x for x,y in corners)+px, max(y for x,y in corners)+py]
        n = m.children(p, 'net')
        pad = dict(ref=ref, number=p[1], xy=[px,py], size=[w,h], angle=pa,
                   shape=p[3], attribute=p[2], net=n[0][2] if n else '', box=box,
                   uuid=m.child(p, 'uuid')[1])
        pads.append(pad)
        fp_pads.append(pad)
    hull = [min(p['box'][0] for p in fp_pads), min(p['box'][1] for p in fp_pads),
            max(p['box'][2] for p in fp_pads), max(p['box'][3] for p in fp_pads)]
    fps.append(dict(ref=ref, value=props['Value'], xy=xy, angle=angle, pad_hull=hull))
assert len(fps) == 53 and len(pads) == 203
holes = [f for f in fps if f['ref'].startswith('H')]
assert {f['ref']:f['xy'] for f in holes} == {'H1':[79,92], 'H2':[121,81], 'H3':[79,119], 'H4':[102,111.5]}
template = [p for p in pads if p['ref']=='J2']
assert len(template)==16
pinmap = {p['number']:p['net'] for p in template if int(p['number']) <= 14}
assert pinmap == dict(zip(map(str, range(1,15)), ['HALL_5V','GND','MUX_A0','GND','MUX_A1','MUX_A2','WING_EN','GND','MUX_OUT_A','GND','MUX_OUT_B','GND','MUX_OUT_C','GND']))
assert next(p for p in pads if p['ref']=='U1' and p['number']=='8')['net']==''

def translate_box(b, x, y):
    return [b[0]+x,b[1]+y,b[2]+x,b[3]+y]

def gap(a,b):
    return math.hypot(max(a[0]-b[2], b[0]-a[2], 0), max(a[1]-b[3], b[1]-a[3], 0))

def hits(a,b):
    return a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]

# Same 0-degree orientation as J2; native source body is +Y in KiCad.
body_local = [-10.375,.2,10.375,4.45]
land_local = [-10.475,-.85,10.475,4.75]
service_local = [-13,-1.5,13,6]  # #153 provisional allocation, NOT manufacturer volume
obstacles = []
for f in fps:
    if f['ref'].startswith('H'): continue
    b=f['pad_hull']
    obstacles.append(dict(ref=f['ref'], box=[b[0]-.5,b[1]-.5,b[2]+.5,b[3]+.5], kind='pad hull + 0.5mm assumption'))
obstacles += [dict(ref='J1-service',box=[79.5,76,90.5,86.5],kind='Issue153 assumption'),
              dict(ref='J2-service',box=[97,114.5,123,122],kind='Issue153 assumption')]
# Actual board-level courtyard segments are supplementary obstacles.
for g in m.children(root, 'gr_line'):
    if m.child(g,'layer')[1] != 'F.CrtYd': continue
    a,b=m.pair(g,'start'),m.pair(g,'end')
    width=float(m.child(g,'stroke')[1][1]) if m.children(g,'stroke') else .05
    obstacles.append(dict(ref='F.CrtYd:'+m.child(g,'uuid')[1],
        box=[min(a[0],b[0])-width/2,min(a[1],b[1])-width/2,max(a[0],b[0])+width/2,max(a[1],b[1])+width/2],kind='actual courtyard segment bounding box'))

def candidate(label,x,y,outline):
    body=translate_box(body_local,x,y)
    land=translate_box(land_local,x,y)
    service=translate_box(service_local,x,y)
    envelope=[land[0]-.5,land[1]-.5,land[2]+.5,land[3]+.5]
    rows=[]
    for key,b in [('body',body),('land_hull',land),('assembly',envelope),('service',service)]:
        hd=[dict(hole=h['ref'],gap_mm=m.rect_distance(*h['xy'],b)-2.500004) for h in holes]
        os=sorted([dict(ref=o['ref'],gap_mm=gap(b,o['box']),overlap=hits(b,o['box'])) for o in obstacles],key=lambda z:(z['gap_mm'],z['ref']))
        rows.append(dict(kind=key,box_mm=b,edge_margin_mm=min(b[0]-outline[0],b[1]-outline[1],outline[2]-b[2],outline[3]-b[3]),hole_gaps=hd,
                         obstacle_overlaps=[o for o in os if o['overlap']],nearest_obstacles=os[:4]))
    return dict(label=label,origin_mm=[x,y],angle_deg=0,outline_mm=outline,envelopes=rows)

candidates=[candidate('A-top-retained',105,81,[76,78,124,122]),
            candidate('B-bottom-left-rejected',89,116,[76,78,124,122]),
            candidate('C-north-extension-fallback',105,73,[76,70,124,122])]
selected=candidates[0]
assert all(not r['obstacle_overlaps'] and min(h['gap_mm'] for h in r['hole_gaps'])>0 and r['edge_margin_mm']>0 for r in selected['envelopes'])
save('geometry.json',dict(board_sha256=before,method='Read actual #155 PCB S-expression; conservative pad hulls, actual courtyard segment bounds; hypothetical rectangles only',
    limitations=['No 3D plug/wire/tool/tolerance proof','Not routing or copper-clearance qualification','Service rectangle is provisional; smallest margin is explicitly retained'],
    board_bounds_mm=[76,78,124,122],footprints=fps,holes=holes,connector_template_pads=template,existing_pad_count=len(pads),candidates=candidates))
save('signal-inventory.json',dict(board_sha256=before,existing_pinmap=pinmap,
    control_pads=[p for p in pads if (p['ref']=='U1' and p['number'] in ['4','5','6','7','8','9','38','39','40']) or p['ref'] in ['R6','R7','U5']],
    proposed_second_enable=dict(net='MUX_EN1',gpio='GPIO6',package_pad='U1.8',currently_unconnected=True,pulldown_ohm=100000,proposal_only=True),
    existing_enable_alias=dict(physical_net='WING_EN',logical='MUX_EN0',gpio='GPIO5',package_pad='U1.7')))

# Extend the saved #141 linear resistive Wing solutions; branch drops are NOT
# multiplied by number of Wings. Both branches draw power even with EN=0.
old=json.loads(OLD.read_text())
after=[s for s in old['results'] if s['variant']=='after']
assert len(after)==16
cases=[]
for s in after:
    base=copy.deepcopy(s);base['load_scale']=1.;base['load_case']='component-5mA' if s['sensor_current_A']==.005 else 'envelope-11mA'
    cases.append(base)
    budget=.127 if s['sensor_current_A']==.005 else .278
    allowance=copy.deepcopy(s);allowance['load_scale']=budget/s['supply']['load_A']
    allowance['load_case']='planning-127mA' if budget==.127 else 'envelope-allowance-278mA'
    cases.append(allowance)
rho=1.7241e-8
wire20=rho*.100/(.0804e-6)
power=[]
for s,contact,returns,rmain in itertools.product(cases,[.030,.050],[6,1],[0,.25,.5]):
    scale=s['load_scale']
    current=s['supply']['load_A']*scale
    assert abs(current-(21*s['sensor_current_A']+3*2.7e-6)*scale)<1e-12
    temp=s['temperature_C']
    wire=wire20*(1+.00393*(temp-20))
    rh=(wire+2*contact)*(1+1/returns)
    # 125C is an electrical resistance sensitivity, not approved system ambient.
    # Engineering bracket from the 3.6V test-point maxima, not an interpolated
    # guaranteed RON specification at 4.75V. 20C uses the 25C table value.
    ron=.150 if temp==20 else .250
    for wings in [1,2]:
        total=wings*current
        wingdrop=s['max_sensor_loop_drop_V']*scale
        fixed=wingdrop+current*rh+total*ron
        drop=fixed+total*rmain
        power.append(dict(load_case=s['load_case'],pitch_mm=s['pitch_mm'],sensor_mA=s['sensor_current_A']*1000*scale,
            temperature_C=temp,width_factor=s['width_factor'],wings=wings,branch_A=current,total_A=total,
            contact_ohm=contact,return_conductors=returns,harness_loop_ohm=rh,main_common_loop_ohm=rmain,
            switch_ohm=ron,switch_drop_V=total*ron,harness_drop_V=current*rh,
            wing_drop_V=wingdrop,main_drop_V=total*rmain,total_drop_V=drop,
            local_at_source_4V75_V=4.75-drop,local_at_source_5V_V=5-drop,
            required_source_for_4V5_V=4.5+drop,
            main_loop_budget_at_source_4V75_ohm=(.25-fixed)/total,
            switch_loss_W=total*total*ron))
with (E/'dual-wing-dc.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(power[0]),lineterminator='\n');w.writeheader();w.writerows(power)
assert len(power)==768
summary=[p for p in power if p['wings']==2 and p['contact_ohm']==.05 and p['return_conductors']==6 and p['main_common_loop_ohm']==0]
save('power-model.json',dict(method='Vlocal_i=Vsource-(I_L+I_R)*(Rswitch+Rmain_common)-I_i*Rharness_i-DeltaVwing_i; source at TPS22919 VIN to Main GND',
    wing_input_sha256=digest(OLD),wing_cases_reused=len(after),derived_load_cases=len(cases),rows=len(power),wire_20C_ohm=wire20,
    assumptions=dict(wire_mm=100,wire_mm2=.0804,copper_rho20=rho,copper_alpha=.00393,ron_20C_ohm=.15,ron_125C_ohm=.25,
        main_common_loop_sensitivity_ohm=[0,.25,.5],contact_each_ohm=[.03,.05],returns=[6,1]),
    limitations=['Main common loop is an unknown parameter, not a measurement of #155 copper','New connector branch resistance must be added after Stage2 routing; current Rmain parameter lumps common and symmetric branch loss',
        '4.75V/5V at switch INPUT are sensitivities, not USB guarantees','Branch return sharing, crimp resistance and actual current unknown','Main 3V3 loads, USB cable loss, inrush, ADC error and thermal qualification excluded'],summary=summary))

# Diagram is a review illustration in SVG, never a board input.
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="70 68 62 62" width="744" height="744">',
     '<rect x="70" y="68" width="62" height="62" fill="white"/>',
     '<style>text{font:1.1px sans-serif} .label{font:1.5px sans-serif}</style>',
     '<path d="M76 78V70H124V78" fill="none" stroke="#777" stroke-dasharray="1 1" stroke-width=".18"/>',
     '<rect x="76" y="78" width="48" height="44" fill="#f6faf6" stroke="#222" stroke-width=".2"/>']
for f in fps:
    if f['ref'].startswith('H'):continue
    b=f['pad_hull'];svg.append(f'<rect x="{b[0]}" y="{b[1]}" width="{b[2]-b[0]}" height="{b[3]-b[1]}" fill="#d5dae0" stroke="#888" stroke-width=".08"/><text x="{f["xy"][0]}" y="{f["xy"][1]-.8}">{f["ref"]}</text>')
for h in holes:
    x,y=h['xy'];svg.append(f'<circle cx="{x}" cy="{y}" r="2.500004" fill="#ffe3dd" stroke="#b44" stroke-width=".12"/><circle cx="{x}" cy="{y}" r="1.1" fill="white" stroke="#b44" stroke-width=".1"/><text x="{x-1}" y="{y-3}">{h["ref"]}</text>')
for c in [candidates[0],candidates[2]]:
    color='#156ab2' if c==candidates[0] else '#777'
    for a in c['envelopes']:
        if a['kind'] not in ['body','service']:continue
        b=a['box_mm'];dash='1 .5' if a['kind']=='service' else '0'
        svg.append(f'<rect x="{b[0]}" y="{b[1]}" width="{b[2]-b[0]}" height="{b[3]-b[1]}" fill="none" stroke="{color}" stroke-width=".18" stroke-dasharray="{dash}"/>')
    x,y=c['origin_mm'];svg.append(f'<text class="label" x="{x-7}" y="{y+3}">{c["label"]}</text>')
svg += ['<text class="label" x="76" y="126">Top view; KiCad mm; A: retained 48 x 44; C: 48 x 52 fallback</text>',
        '<text x="76" y="128">Dashed service areas are assumptions. No routing / 3D qualification.</text>','</svg>']
(E/'placement.svg').write_text('\n'.join(svg)+'\n')
assert digest(PCB)==before
save('inputs.json',dict(base_commit='a11c1f7d535241e65b54dc8bb7a27bbf949cf250',
    files={str(p.relative_to(R)):digest(p) for p in [PCB,PROJECT,OLD,R/'docs/decisions.md',R/'hardware/rev-m1/main-wing-interface.md',R/'hardware/rev-m1/g0b-freeze-proposal.md',R/'hardware/tscircuit/src/qualification/JstGh14.tsx',Path(spec.origin)]},board_unchanged=True))
print(json.dumps(dict(geometry=[dict(label=c['label'],envelopes=c['envelopes']) for c in candidates],power_rows=len(power),summary=summary),indent=2))
