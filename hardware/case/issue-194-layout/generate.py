"""Phase A proposals only; stdlib, no PCB/routing/CAM writes. --check is read-only."""
import csv
import io
import itertools
import json
import math
from pathlib import Path
import sys

E = Path(__file__).resolve().parent
R = E.parents[2]

def rect(x, y, w, h, angle=0):
    a = math.radians(angle)
    return [[x+u*math.cos(a)-v*math.sin(a), y+u*math.sin(a)+v*math.cos(a)]
            for u,v in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]

def segment_distance(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)

def point_distance(p,poly):
    cross=[(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]) for a,b in zip(poly,poly[1:]+poly[:1])]
    if min(cross)>=-1e-12 or max(cross)<=1e-12: return 0.0
    return min(segment_distance(p,a,b) for a,b in zip(poly,poly[1:]+poly[:1]))

def separation(a,b):
    gaps=[]
    for poly in [a,b]:
        for p,q in zip(poly,poly[1:]+poly[:1]):
            dx,dy=q[0]-p[0],q[1]-p[1];n=math.hypot(dx,dy);axis=(-dy/n,dx/n)
            aa=[x*axis[0]+y*axis[1] for x,y in a];bb=[x*axis[0]+y*axis[1] for x,y in b]
            gaps.append(max(min(bb)-max(aa),min(aa)-max(bb)))
    return max(gaps)

def distance(a,b):
    if separation(a,b)<=0: return 0.0
    return min([point_distance(p,b) for p in a]+[point_distance(p,a) for p in b])

def edge_gap(poly,box):
    x0,y0,x1,y1=box
    return min(min(x-x0,y-y0,x1-x,y1-y) for x,y in poly)

def holes(box):
    x0,y0,x1,y1=box
    return [[x,y] for x in [x0+3,x1-3] for y in [y0+3,y1-3]]

def optimize(polys,margin):
    # 0.1mm grid, minimum area. Left/top tight; prove other three corners
    # remain clear throughout the bounded search, so only BR is active.
    pts=sum(polys,[])
    x0=math.floor((min(x for x,y in pts)-margin)*10)/10
    y1=math.ceil((max(y for x,y in pts)+margin)*10)/10
    xr=math.ceil((max(x for x,y in pts)+margin)*10)
    yb=math.floor((min(y for x,y in pts)-margin)*10)
    best=None;count=0;non_br_min=1e9
    # Feasible seed: 10mm outward on right/bottom. Area bounds all candidates.
    seed=[x0,(yb-100)/10,(xr+100)/10,y1]
    assert min(point_distance(h,p)-2.5 for h in holes(seed) for p in polys)>=margin
    area=(seed[2]-x0)*(y1-seed[1]);initial=area
    max_right=math.floor((x0+initial/(y1-yb/10))*10)
    for xi in range(xr,max_right+1):
        x1=xi/10
        min_bottom=math.ceil((y1-initial/(x1-x0))*10)
        for yi in range(yb,min_bottom-1,-1):
            y0=yi/10;candidate=(x1-x0)*(y1-y0)
            if candidate>area+1e-9: continue
            box=[x0,y0,x1,y1];hh=holes(box);count+=1
            # BL/TL/TR cannot become limiting as left/top expand either;
            # they sit in empty corner regions, outside all key Y/X bounds.
            non_br_min=min(non_br_min,min(point_distance(h,p)-2.5 for h in [hh[0],hh[1],hh[3]] for p in polys))
            if min(point_distance(hh[2],p)-2.5 for p in polys)<margin-1e-10: continue
            assert min(point_distance(h,p)-2.5 for h in hh for p in polys)>=margin-1e-10
            key=(round(candidate,9),x1-x0,y1-y0)
            if best is None or key<best[0]: best=(key,box);area=candidate
    assert best and non_br_min>=margin
    return {'bounds_mm':best[1],'area_mm2':best[0][0],'candidates_checked':count,
            'other_corners_min_mm':non_br_min,'grid_mm':0.1,'margin_mm':margin,
            'objective':'minimum area, then width; axis-aligned, corner inset 3mm'}

def csv_text(rows):
    s=io.StringIO();w=csv.DictWriter(s,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows);return s.getvalue()

def build():
    out={};summary={}
    for pitch in [16,17]:
        baseline=json.loads((R/f'hardware/jitx/wing/generated/representative21-{pitch}mm/definition.json').read_text())
        src=list(csv.DictReader((E/f'inputs/stage1/hardware/case/issue-190-layout/coordinates-{pitch}mm.csv').open()))
        urows={x['key']:x for x in csv.DictReader((E/'inputs/stage1/hardware/case/issue-190-layout/coordinates-u.csv').open())}
        pp=[rect(float(k['x_mm']),float(k['y_mm']),15.8,15.8,float(urows[k['key']]['source_rotation_deg'])) for k in src]
        optimum=optimize(pp,0.25);zero=optimize(pp,0)
        for side in ['left','right']:
            sign=1 if side=='left' else -1
            d=json.loads(json.dumps(baseline));d['schema_version']='issue194-phase-a-1'
            box=optimum['bounds_mm'][:]
            if sign==-1:box=[-box[2],box[1],-box[0],box[3]]
            x0,y0,x1,y1=box
            d.update(name=f'wing-rev2-{side}-{pitch}mm-phase-a',frame='Stage 1 fixed origin; +X right, +Y up, top view; CCW degrees',
                     status='PMO review proposal; not a manufacturing definition',outline_mm=[[x0,y0],[x1,y0],[x1,y1],[x0,y1]],width_mm=x1-x0,height_mm=y1-y0,
                     layout_source={'stage1_commit':json.loads((E/'inputs/provenance.json').read_text())['stage1_commit'],'coordinates':'inputs/stage1/hardware/case/issue-190-layout/coordinates-u.csv'},
                     layout_transform='Stage1 x=(u-55/18)*pitch; y=(2-v)*pitch+9; right x=-left x; thumb CCW sign reversed',
                     outline_policy='minimum area on 0.1mm grid; 0.25mm key edge and hole keepout clearance; four holes inset 3mm',
                     size_requirement='Phase A geometric proposal; not old pitch-cell policy',key_cell_bounds_mm=None,key_cell_assumption_mm=None)
            d['mounting_holes']=[dict(x_mm=h[0],y_mm=h[1],diameter_mm=2.2,keepout_diameter_mm=5.0) for h in holes(box)]
            comps={c['reference']:c for c in d['components']};sites={s['reference']:s for s in d['sensor_sites']};keys=[]
            for k in src:
                x=sign*float(k['x_mm']);y=float(k['y_mm']);angle=sign*float(urows[k['key']]['source_rotation_deg']);ref=k['sensor'];kid=k['key'].replace('L_','R_' if sign==-1 else 'L_');a=math.radians(angle)
                s=sites[ref];s.update(x_mm=x,y_mm=y,source_key_id=kid,source_x_u=float(urows[k['key']]['x_u']),source_y_u=float(urows[k['key']]['y_u']),rotation_ccw_deg=angle)
                comps[ref].update(x_mm=x,y_mm=y,rotation_ccw_deg=angle,side='bottom')
                comps['C_'+ref[2:]].update(x_mm=x+3.5*math.sin(a),y_mm=y-3.5*math.cos(a),rotation_ccw_deg=angle,side='bottom')
                keys.append(dict(key=kid,sensor=ref,x_mm=x,y_mm=y,rotation_ccw_deg=angle,envelope_mm=rect(x,y,15.8,15.8,angle),
                                 locator_holes=[dict(x_mm=x+t*5.08*math.cos(a),y_mm=y+t*5.08*math.sin(a),diameter_mm=1.7) for t in [-1,1]]))
            d['keys']=keys;d['hall_pose_contract']={'target_active_xy':'key center; footprint origin must be calibrated to DRV5055 active point before Phase B placement','angle':'CCW top view, same as key, including on bottom','right':'real footprint rotation, never mirror pin numbering','locator_status':'±5.08mm from #158 grid-reading hypothesis; not drill release','c0_rotation_deg':0}
            # Real parts keep pin maps. Only placement positions mirror; not pads.
            reservations=[]
            def place(ref,x,y,w,h):
                c=comps[ref];c.update(x_mm=sign*x,y_mm=y,rotation_ccw_deg=0,side='top')
                reservations.append(dict(reference=ref,polygon_mm=rect(sign*x,y,w,h)))
            place('J_WING',-37,-23,26,8)
            # Connector reservation is asymmetric in Y, inherited access convention.
            reservations[-1]['polygon_mm']=rect(sign*-37,-26.0,26,8)
            d['connector_cable_access_mm']=[sign*-37-13,-30,sign*-37+13,-22]
            for g,(x,y) in zip('ABC',[(-19,-23),(-7,-23),(0,-29)]):
                place('U_MUX_'+g,x,y,7.8,5.5)
                place('C_MUX_'+g,x+5,y,1.5,3)
            tps=[c for c in d['components'] if c['kind']=='testpoint']
            for i,c in enumerate(tps):place(c['reference'],-48+3*i,-32.3,2,2)
            d['service_reservations']=reservations
            d['service_notes']='J1 is J_WING legacy reference. GH14 26x8 access includes lands; vertical mating +Z. MUX/C boxes include pad allowance; TP square 2mm includes 1.2mm pad. Reservations are design budgets, not certified courtyards.'
            polys=[k['envelope_mm'] for k in keys]
            pairs=[dict(key_a=keys[i]['key'],key_b=keys[j]['key'],sat_gap_mm=separation(polys[i],polys[j]),distance_mm=distance(polys[i],polys[j])) for i,j in itertools.combinations(range(21),2)]
            clear=[dict(key=k['key'],edge_mm=edge_gap(k['envelope_mm'],box),hole_keepout_mm=min(point_distance(h,k['envelope_mm'])-2.5 for h in holes(box))) for k in keys]
            service=[dict(reference=s['reference'],edge_mm=edge_gap(s['polygon_mm'],box),key_gap_mm=min(distance(s['polygon_mm'],p) for p in polys),hole_keepout_mm=min(point_distance(h,s['polygon_mm'])-2.5 for h in holes(box))) for s in reservations]
            sp=[dict(a=a['reference'],b=b['reference'],distance_mm=distance(a['polygon_mm'],b['polygon_mm'])) for a,b in itertools.combinations(reservations,2)]
            assert min(p['sat_gap_mm'] for p in pairs)>0
            assert min(c['edge_mm'] for c in clear)>=0.25-1e-9
            assert min(c['hole_keepout_mm'] for c in clear)>=0.25-1e-9
            assert min(min(c['edge_mm'],c['key_gap_mm'],c['hole_keepout_mm']) for c in service)>0,service
            assert min(p['distance_mm'] for p in sp)>0,sorted(sp,key=lambda x:x['distance_mm'])[:3]
            tag=f'{pitch}mm-{side}'
            out[f'definition-{tag}.proposal.json']=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
            out[f'key-clearances-{tag}.csv']=csv_text(clear);out[f'key-pairs-{tag}.csv']=csv_text(pairs)
            out[f'service-clearances-{tag}.csv']=csv_text(service);out[f'service-pairs-{tag}.csv']=csv_text(sp)
            out[f'placements-{tag}.csv']=csv_text([{k:c[k] for k in ['reference','mpn','x_mm','y_mm','rotation_ccw_deg','side']} for c in d['components']])
            summary[tag]=dict(bounds_mm=box,width_mm=x1-x0,height_mm=y1-y0,optimization=optimum,zero_margin_optimization=zero,
                              min_key_edge_mm=min(c['edge_mm'] for c in clear),min_key_hole_keepout_mm=min(c['hole_keepout_mm'] for c in clear),
                              min_key_pair=min(pairs,key=lambda x:x['distance_mm']),min_service_key=min(service,key=lambda x:x['key_gap_mm']),
                              min_service_edge_mm=min(c['edge_mm'] for c in service),min_service_hole_keepout_mm=min(c['hole_keepout_mm'] for c in service),min_service_pair=min(sp,key=lambda x:x['distance_mm']),
                              key_pairs=len(pairs),key_hole_checks=84,service_pairs=len(sp))
    out['verification.json']=json.dumps(summary,ensure_ascii=False,indent=2)+'\n'
    return out

if __name__=='__main__':
    outputs=build()
    for name,body in outputs.items():
        p=E/name
        if '--check' in sys.argv: assert p.read_text()==body,name
        else:p.write_text(body)
    print(f'{len(outputs)} proposal/evidence files '+('verified' if '--check' in sys.argv else 'written'))
