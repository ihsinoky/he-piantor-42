#!/usr/bin/env python3
"""Read-only mechanical screening; assumptions are not certified clearances.

No KiCad writer, route, refill or manufacturing export is invoked.
Run from the repository root. Runtime files belong to .issue160-runtime/.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import sys

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
R = E.parents[3]
PCB = R / 'hardware/kicad/qualification/issue-155-main-mounting-stage2/inspection/final/main.kicad_pcb'
PARSER = R / 'hardware/kicad/qualification/issue-153-main-mounting-stage1/measure.py'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location('measure153', PARSER)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
board = m.parse(PCB)
fps = {}
for f in m.children(board, 'footprint'):
    props = {p[1]: p[2] for p in m.children(f, 'property')}
    fps[props['Reference']] = f
assert len(fps) == 53
assert sha(PCB) == 'fdc1a7748f94714e395eb50f3e08c43afa24192ee76eb3d1804a8cba28690222'
assert list(m.pair(fps['J2'], 'at')) == [110., 116.]
holes = {k: list(m.pair(fps[k], 'at')) for k in ['H1', 'H2', 'H3', 'H4']}
assert holes == {'H1':[79.,92.], 'H2':[121.,81.], 'H3':[79.,119.], 'H4':[102.,111.5]}

def pad_box(f):
    at = m.child(f, 'at'); x,y = map(float, at[1:3])
    ang = float(at[3]) if len(at)>3 else 0
    points = []
    for p in m.children(f, 'pad'):
        px,py = m.pair(p,'at'); w,h = m.pair(p,'size')
        pa=m.child(p,'at'); a=float(pa[3]) if len(pa)>3 else 0
        # KiCad pad angle is absolute; footprint rotates the pad center.
        dx,dy=m.rot(px,py,ang)
        for xx in [-w/2,w/2]:
            for yy in [-h/2,h/2]:
                tx,ty=m.rot(xx,yy,a);points.append((x+dx+tx,y+dy+ty))
    return [min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)]

r2 = pad_box(fps['R2'])
def rect_dist(p,b):
    return math.hypot(max(b[0]-p[0],p[0]-b[2],0),max(b[1]-p[1],p[1]-b[3],0))
def rect_gap(a,b):
    return math.hypot(max(b[0]-a[2],a[0]-b[2],0),max(b[1]-a[3],a[1]-b[3],0))
def candidate(name,y):
    # Header body from existing native definition, not a fabricated footprint.
    header=[94.625,y+.2,115.375,y+4.45]
    # Housing is centered on header in this screening model. Seating / latch
    # datum tolerances are absent from catalogue; this is not exact 3D CAD.
    center=[105,y+2.325]
    housing=[95.625,center[1]-2.075,114.375,center[1]+2.075]
    service=[92,y-1.5,118,y+6]
    r2allow=[r2[0]-.5,r2[1]-.5,r2[2]+.5,r2[3]+.5]
    grips=[]
    # Side-grasp alternatives, cylinders touching housing ends. Projected
    # conflicts only: actual fingers may approach above low parts.
    for diameter in [6,8,10]:
        radius=diameter/2
        left=[housing[0]-radius,center[1]]
        right=[housing[2]+radius,center[1]]
        grips.append({'diameter_mm':diameter,'left_center':left,'right_center':right,
          'left_to_R2_actual_pad_hull_mm':rect_dist(left,r2)-radius,
          'right_to_H2_head_d4p5_mm':math.dist(right,holes['H2'])-radius-2.25,
          'meaning':'Negative is a planar screening conflict, not proof of 3D collision or impossibility'})
    gap=rect_gap(service,r2allow)
    return {'name':name,'origin_mm':[105,y],'rotation_deg':0,
       'outline_mm':[76,78 if name=='A' else 70,124,122],
       'header_body_mm':header,'housing_projection_assumed_mm':housing,
       'service_rectangle_from_stage1_mm':service,
       'service_to_R2_pad_plus_0p5_mm':gap,
       'service_to_H2_d5_reservation_mm':rect_dist(holes['H2'],service)-2.500004,
       'service_to_H2_driver_d6_mm':rect_dist(holes['H2'],service)-3,
       'R2_service_gap_after_relative_tolerance_mm':[
           {'relative_allowance_mm':t,'signed_remaining_mm':gap-t} for t in [.05,.10,.20]],
       'side_grasp_projection_sweep':grips}

result={'status':'STOP_PROPOSE_C','decision_kind':'Engineering judgment of multiple unresolved service constraints; not proof that every A assembly method is impossible',
 'inputs':{str(p.relative_to(R)):sha(p) for p in [PCB,PCB.with_suffix('.kicad_pro'),PARSER,R/'hardware/tscircuit/src/qualification/JstGh14.tsx']},
 'actual_R2_pad_hull_mm':r2,'holes_mm':holes,
 'manufacturer_catalogue':{'url':'https://jst.es/wp-content/uploads/2025/06/gh-connector.pdf',
   'housing_GHR14_width_mm':18.75,'housing_depth_mm':4.15,'housing_height_mm':5.7,
   'top_entry_assembly_height_reference_mm':7.3,'wire_insulation_OD_range_mm':[.76,1.0],
   'pages_1_based':[1,2,3]},
 'assumptions':{'housing_center':'header body midpoint; full seating/latch datum and tolerances not supplied',
   'finger_diameters_mm':[6,8,10],'driver_diameter_mm':6,'screw_head_diameter_max_mm':4.5,
   'relative_tolerance_sweep_mm':[.05,.10,.20],
   'bend_centerline_radii_mm':[3,5,8],
   'notes':'Sweeps are engineering scenarios, not manufacturer minimums or newly approved requirements. Original service envelope is never reduced.'},
 'candidates':[candidate('A',81),candidate('C',73)],
 'cable_bend_height_screen':[{'radius_mm':rad,'wire_OD_mm':od,'minimum_z_above_PCB_screen_mm':7.3+rad+od/2}
     for rad in [3,5,8] for od in [.76,1.]],
 'unresolved':['3D latch actuation and straight withdrawal with actual harness/tool',
   'Selected wire bend radius, strain relief and case/cover height',
   'Actual component/assembly/fastener/tool tolerances',
   'Support against insertion/withdrawal forces; no actual force or deflection test'],
 'execution':{'pcb_writes':0,'router_runs':0,'refill_runs':0,'qualification_runs':0,'manufacturing_exports':0}}
(E/'mechanical-gate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'candidates':result['candidates']},ensure_ascii=False,indent=2))
