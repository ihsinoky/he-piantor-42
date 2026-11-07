"""Read-only independent checks of proposal coordinates, pose, interface and geometry."""
import csv
from fractions import Fraction
import itertools
import json
import math
from pathlib import Path

E=Path(__file__).resolve().parent
R=E.parents[2]
checks={}
for pitch,side in itertools.product([16,17],['left','right']):
    tag=f'{pitch}mm-{side}';d=json.loads((E/f'definition-{tag}.proposal.json').read_text())
    b=json.loads((R/f'hardware/jitx/wing/generated/representative21-{pitch}mm/definition.json').read_text())
    src={x['key']:x for x in csv.DictReader((E/'inputs/stage1/hardware/case/issue-190-layout/coordinates-u.csv').open())}
    sign=1 if side=='left' else -1;parts={c['reference']:c for c in d['components']}
    assert d['nets']==b['nets'] and d['intentional_nc']==b['intentional_nc'] and d['harness']==b['harness']
    assert {c['reference']:c['pins'] for c in d['components']}=={c['reference']:c['pins'] for c in b['components']}
    assert len(d['keys'])==21 and len(d['sensor_sites'])==21
    hole_min=1e9;edge_min=1e9
    for k in d['keys']:
        s=src[k['key'].replace('R_','L_',1) if side=='right' else k['key']]
        x=sign*float((Fraction(s['x_u_exact'])-Fraction(55,18))*pitch)
        y=float((2-Fraction(s['y_u_exact']))*pitch+9)
        assert abs(k['x_mm']-x)<1e-9 and abs(k['y_mm']-y)<1e-9
        theta=sign*float(s['source_rotation_deg']);assert k['rotation_ccw_deg']==theta
        c=parts[k['sensor']];assert c['side']=='bottom' and c['rotation_ccw_deg']==theta
        assert c['x_mm']==k['x_mm'] and c['y_mm']==k['y_mm']
        a=math.radians(theta);co=math.cos(a);si=math.sin(a)
        # Inverse rotation to axis-aligned 15.8 box, independent of stored polygons.
        for h in d['mounting_holes']:
            dx=h['x_mm']-x;dy=h['y_mm']-y
            dist=math.hypot(max(0,abs(dx*co+dy*si)-7.9),max(0,abs(-dx*si+dy*co)-7.9))-2.5
            hole_min=min(hole_min,dist)
        xs=[p[0] for p in d['outline_mm']];ys=[p[1] for p in d['outline_mm']]
        half=7.9*(abs(co)+abs(si))
        edge_min=min(edge_min,x-half-min(xs),max(xs)-x-half,y-half-min(ys),max(ys)-y-half)
    minimum=1e9
    for a,b in itertools.combinations(d['keys'],2):
        # Rectangle support functions on both sets of local axes.
        ta,tb=map(math.radians,[a['rotation_ccw_deg'],b['rotation_ccw_deg']]);gaps=[]
        for t in [ta,ta+math.pi/2,tb,tb+math.pi/2]:
            projection=abs((a['x_mm']-b['x_mm'])*math.cos(t)+(a['y_mm']-b['y_mm'])*math.sin(t))
            radius=sum(7.9*(abs(math.cos(t-u))+abs(math.sin(t-u))) for u in [ta,tb])
            gaps.append(projection-radius)
        assert max(gaps)>0;minimum=min(minimum,max(gaps))
    saved=json.loads((E/'verification.json').read_text())[tag]
    assert abs(saved['min_key_edge_mm']-edge_min)<1e-8
    assert abs(saved['min_key_hole_keepout_mm']-hole_min)<1e-8
    assert abs(saved['min_key_pair']['sat_gap_mm']-minimum)<1e-8
    assert edge_min>=.25-1e-9 and hole_min>=.25-1e-9
    # All real GH pads (including MP) fit the reserved access region at 0deg.
    j=parts['J_WING'];x0,y0,x1,y1=d['connector_cable_access_mm']
    pads=json.loads((R/'hardware/kicad/qualification/issue-129-wing-2layer-routing/evidence/library-pads.json').read_text())
    for p in pads['connector']:
        assert x0<=j['x_mm']+p['x_mm']-p['width_mm']/2
        assert x1>=j['x_mm']+p['x_mm']+p['width_mm']/2
        assert y0<=j['y_mm']+p['y_mm']-p['height_mm']/2
        assert y1>=j['y_mm']+p['y_mm']+p['height_mm']/2
    checks[tag]=dict(keys=21,pairs=210,key_hole_checks=84,pins_nets_harness_unchanged=True,min_edge_mm=edge_min,min_hole_keepout_mm=hole_min,min_sat_gap_mm=minimum)
print(json.dumps(checks,indent=2))
