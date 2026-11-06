#!/usr/bin/env python3
"""Reproduce Stage 1 coordinate proposals and planar screening, without CAD tools.
Run from anywhere with --check to compare committed output bytes (no writes).
"""
import argparse
import csv
import hashlib
import io
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = {}

def put(name, value):
    OUTPUT[name] = value

def csvout(name, header, rows):
    s = io.StringIO(newline='')
    w = csv.writer(s, lineterminator='\n')
    w.writerow(header)
    w.writerows(rows)
    put(name, s.getvalue())

def num(x):
    return round(float(x), 9)

def loadcsv(path):
    return list(csv.DictReader(path.open()))

def corners(x, y, w, angle):
    a = math.radians(angle)
    c, s = math.cos(a), math.sin(a)
    return [(x+c*u-s*v, y+s*u+c*v) for u,v in itertools.product((-w/2,w/2),repeat=2)]

def separation(a, b, w, angles):
    """SAT signed max axis separation; negative iff interiors overlap."""
    axes = [(math.cos(math.radians(t)), math.sin(math.radians(t)))
            for t in (angles[0], angles[0]+90, angles[1], angles[1]+90)]
    pa, pb = corners(*a,w,angles[0]), corners(*b,w,angles[1])
    def sep(axis):
        xa = [x*axis[0]+y*axis[1] for x,y in pa]
        xb = [x*axis[0]+y*axis[1] for x,y in pb]
        return max(min(xb)-max(xa),min(xa)-max(xb))
    return max(map(sep,axes))

def circle_gap(x,y,hx,hy,w,angle,r):
    a=math.radians(angle); dx,dy=hx-x,hy-y
    lx=math.cos(a)*dx+math.sin(a)*dy
    ly=-math.sin(a)*dx+math.cos(a)*dy
    return math.hypot(max(abs(lx)-w/2,0),max(abs(ly)-w/2,0))-r

def main():
    src=loadcsv(HERE/'inputs/cantor-extracted.csv')
    other=loadcsv(HERE/'inputs/piantor-extracted.csv')
    assert len(src)==len(other)==21
    assert [(s['source_key'],s['source_x_mm'],s['source_y_mm']) for s in src] == [(s['source_key'],s['source_x_mm'],s['source_y_mm']) for s in other]
    # Independent PMO transcription from instructions-190.md, not inferred from Wing.
    expected={f'K{r}{c}':(74+18*c,[70,70,58,53,58,60][c]+17*r) for r in range(3) for c in range(6)}
    expected.update(K30=(141,113),K31=(163,114),K32=(184,121))
    points={}
    source_angles={}
    rows=[]
    for s in src:
        k=s['source_key']; x,y=F(s['source_x_mm']),F(s['source_y_mm'])
        assert (x,y)==expected[k]
        key=f'L_R{k[1]}_C{k[2]}' if k[1]!='3' else f'L_T{k[2]}'
        u,v=(x-74)/18,(y-53)/17
        points[key]=(u,v); source_angles[key]=float(s['source_rotation_deg'])
        rows.append([k,key,num(x),num(y),str(u),str(v),num(u),num(v),s['source_rotation_deg']])
    assert points['L_T0']==(F(67,18),F(60,17))
    assert points['L_T1']==(F(89,18),F(61,17))
    assert points['L_T2']==(F(55,9),F(4))
    csvout('coordinates-u.csv',['source_key','key','source_x_mm','source_y_mm','x_u_exact','y_u_exact','x_u','y_u','source_rotation_deg'],rows)
    summary={}
    changes=[]
    for p in (16,17):
        path=ROOT/f'hardware/jitx/wing/generated/representative21-{p}mm'
        d=json.loads((path/'definition.json').read_text())
        old={s['source_key_id']:s for s in d['sensor_sites']}
        oldp={s['reference']:s for s in loadcsv(path/'placements.csv')}
        oldkeys=loadcsv(HERE/f'inputs/keys-{p}mm.csv')
        assert {r['key'] for r in oldkeys}==set(points)==set(old)
        for r in oldkeys:
            s=old[r['key']]; c=oldp[s['reference']]
            assert abs(float(r['kicad_x_mm'])-100-s['x_mm'])<1e-8
            assert abs(float(r['kicad_y_mm'])-100+s['y_mm'])<1e-8
            assert float(c['x_mm'])==s['x_mm'] and float(c['y_mm'])==s['y_mm']
        # Candidate uses bounds midpoint, preserving +9 mm north shift for service strip.
        new={k:(float((u-F(55,18))*p),float((2-v)*p+9)) for k,(u,v) in points.items()}
        fixed={k:(float((u-F(11,4))*p),float((F(15,8)-v)*p+9)) for k,(u,v) in points.items()}
        csvout(f'coordinates-{p}mm.csv',['key','sensor','x_mm','y_mm','kicad_x_mm','kicad_y_mm','rotation_deg'],[[k,old[k]['reference'],num(x),num(y),num(100+x),num(100-y),0] for k,(x,y) in new.items()])
        csvout(f'keys-{p}mm.csv',list(oldkeys[0]),[[r['key'],r['sensor'],num(100+new[r['key']][0]),num(100-new[r['key']][1]),0] for r in oldkeys])
        diff=[]
        for k in points:
            s=old[k]; x,y=new[k]; fx,fy=fixed[k]
            diff.append([k,num(s['x_mm']),num(s['y_mm']),num(x),num(y),num(x-s['x_mm']),num(y-s['y_mm']),num(-(y-s['y_mm'])),num(fx-s['x_mm']),num(fy-s['y_mm'])])
        csvout(f'deltas-{p}mm.csv',['key','old_x_mm','old_y_mm','new_x_mm','new_y_mm','delta_x_mm','delta_y_up_mm','delta_kicad_y_down_mm','fixed_anchor_delta_x_mm','fixed_anchor_delta_y_up_mm'],diff)
        # File/JSON-pointer-level replacement plan; never write the target files.
        patch=[
            dict(op='replace',path='/layout_source/source',value=dict(
                coordinate_basis='Cantor Classic / Piantor left PCB footprint centers; verified 2026-11-07',
                records=json.loads((HERE/'inputs/upstream.json').read_text()),
                license_note='Original upstream attribution retained in records; no upstream PCB/footprint artwork copied. Review upstream licensing before Stage 2 integration.')),
            dict(op='replace',path='/layout_source/repository_record',value=dict(path='hardware/case/issue-190-layout/coordinates-u.csv',status='Stage 1 proposal')),
            dict(op='replace',path='/layout_source/frame',value='origin source KiCad (74,53) mm; x=(X-74)/18, y=(Y-53)/17; +x right, +y down'),
            dict(op='replace',path='/layout_source/note',value='Exact center ratios from PCB sources replace QMK display geometry. Thumb rotations remain zero in this center-only proposal; source-angle sensitivity is documented separately.'),
        ]
        for i,k in enumerate(d['layout_source']['keys']):
            u,v=points[k['id']]
            for axis,val in [('x',u),('y',v)]:
                patch.append(dict(op='replace',path=f'/layout_source/keys/{i}/{axis}',value=float(val)))
        patch.extend([dict(op='replace',path='/layout_transform',value='x=(source_x-55/18)*pitch; y=(2-source_y)*pitch+9; no key rotation'),dict(op='replace',path='/key_cell_bounds_mm',value=[num(-F(55,18)*p-p/2),num(9-2*p-p/2),num(F(55,18)*p+p/2),num(9+2*p+p/2)]),dict(op='replace',path='/outline_policy',value='Stage 1 proposal: centers re-anchored; existing outline fails full envelope; PO outline decision required before regeneration')])
        moves=[]
        for i,s in enumerate(d['sensor_sites']):
            k=s['source_key_id'];u,v=points[k];x,y=new[k]
            for name,val in [('x_mm',x),('y_mm',y),('source_x_u',float(u)),('source_y_u',float(v))]:
                patch.append(dict(op='replace',path=f'/sensor_sites/{i}/{name}',value=val))
            dx,dy=x-s['x_mm'],y-s['y_mm']
            for ref in (s['reference'],'C_'+s['reference'][2:]):
                ci=next(i for i,c in enumerate(d['components']) if c['reference']==ref)
                c=d['components'][ci]
                for name,val in [('x_mm',c['x_mm']+dx),('y_mm',c['y_mm']+dy)]:
                    patch.append(dict(op='replace',path=f'/components/{ci}/{name}',value=val))
                moves.append([ref,num(c['x_mm']),num(c['y_mm']),num(c['x_mm']+dx),num(c['y_mm']+dy),'key-site dependency; Stage 2 collision review'])
            for ci,c in enumerate(d['components']):
                if c['reference'].startswith('TP_H_') and f"H_{s['reference'][3:]}_RAW" in c['pins'].values():
                    for name,val in [('x_mm',x-3.5),('y_mm',y)]:
                        patch.append(dict(op='replace',path=f'/components/{ci}/{name}',value=val))
                    moves.append([c['reference'],num(c['x_mm']),num(c['y_mm']),num(x-3.5),num(y),'raw-node dependency; Stage 2 collision review'])
        put(f'definition-{p}mm.proposal.json',json.dumps(dict(target=str(path.relative_to(ROOT)/'definition.json'),status='INCOMPLETE DESIGN PROPOSAL: key geometry and dependent offsets only; not a production definition',geometry_patch=patch,required_metadata_changes=['Keep superseded QMK attribution in historical record; do not claim it as new center source.','Update /size_requirement, /outline_mm, /width_mm, /height_mm, /mounting_holes, /connector_cable_access_mm only after PO outline decision and Stage 2 service placement.','Invalidate and regenerate placement.svg, bom.csv/nets.csv as needed and downstream PCB/manufacturing evidence in Stage 2; no present qualification carries over.']),indent=2)+'\n')
        csvout(f'placements-{p}mm.proposal.csv',['reference','old_x_mm','old_y_mm','proposed_x_mm','proposed_y_mm','status'],moves)
        W,H=d['width_mm'],d['height_mm']
        holes=[(h['x_mm'],h['y_mm']) for h in d['mounting_holes']]
        metrics={}
        allclear=[]; allpairs=[]
        for anchor,coords in [('fixed',fixed),('reanchored',new)]:
            metrics[anchor]={}
            for rotation in ('zero','source'):
                metrics[anchor][rotation]={}
                for label,w in [('jade',15.8),('dsa',18.415),('narrow_design',15.0),('pitch_cell',p)]:
                    angles={k:0 if rotation=='zero' else source_angles[k] for k in points}
                    ps=[]
                    for a,b in itertools.combinations(points,2):
                        gap=separation(coords[a],coords[b],w,(angles[a],angles[b]))
                        ps.append((gap,a,b))
                        if anchor=='reanchored': allpairs.append([rotation,label,a,b,num(gap),gap < -1e-8])
                    bb=[corners(x,y,w,angles[k]) for k,(x,y) in coords.items()]
                    xs=[x for box in bb for x,y in box];ys=[y for box in bb for x,y in box]
                    center_edge=min(min(x+W/2,W/2-x,y+H/2,H/2-y) for x,y in coords.values())
                    edge=min(min(xs)+W/2,W/2-max(xs),min(ys)+H/2,H/2-max(ys))
                    circ=[]
                    for k,(x,y) in coords.items():
                        cdist=min(math.hypot(x-hx,y-hy) for hx,hy in holes)
                        gapdrill=min(circle_gap(x,y,hx,hy,w,angles[k],1.1) for hx,hy in holes)
                        gapkeep=min(circle_gap(x,y,hx,hy,w,angles[k],2.5) for hx,hy in holes)
                        circ.append((gapkeep,k))
                        if label!='pitch_cell':
                            allclear.append([anchor,rotation,label,k,num(x+W/2),num(W/2-x),num(H/2-y),num(y+H/2),num(cdist),num(cdist-1.1),num(gapdrill),num(gapkeep)])
                    metrics[anchor][rotation][label]=dict(width_mm=w,bounds_mm=list(map(num,[min(xs),min(ys),max(xs),max(ys)])),span_mm=list(map(num,[max(xs)-min(xs),max(ys)-min(ys)])),minimum_center_edge_mm=num(center_edge),minimum_envelope_edge_mm=num(edge),minimum_pair_separation_mm=num(min(ps)[0]),minimum_pair=list(min(ps)[1:]),overlapping_pairs=sum(g<-1e-8 for g,a,b in ps),minimum_envelope_keepout_gap_mm=num(min(circ)[0]),limiting_keepout_key=min(circ)[1])
        csvout(f'clearances-{p}mm.csv',['anchor','rotation','envelope','key','center_left_edge_mm','center_right_edge_mm','center_top_edge_mm','center_bottom_edge_mm','nearest_hole_center_mm','center_to_drill_rim_mm','envelope_to_drill_gap_mm','envelope_to_keepout_gap_mm'],allclear)
        csvout(f'pair-screen-{p}mm.csv',['rotation','envelope','key_a','key_b','sat_separation_mm','overlap'],allpairs)
        summary[str(p)]=dict(outline_mm=[W,H],holes_mm=holes,anchor_shift_mm=[num(-F(11,36)*p),num(F(1,8)*p)],center_span_mm=[num(F(55,9)*p),4*p],one_pitch_policy_required_outline_mm=[num((F(55,9)+1)*p+6),5*p+24],metrics=metrics)
    put('geometry-summary.json',json.dumps(summary,indent=2)+'\n')
    inputs=list((HERE/'inputs').iterdir())+[ROOT/f'hardware/jitx/wing/generated/representative21-{p}mm/{f}' for p in (16,17) for f in ('definition.json','placements.csv')]
    put('input-hashes.json',json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inputs)},indent=2)+'\n')
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    for name,content in OUTPUT.items():
        if args.check:
            assert (HERE/name).read_bytes()==content.encode(),f'Drift: {name}'
        else:
            (HERE/name).write_text(content)
    print(f'{"Verified" if args.check else "Generated"} {len(OUTPUT)} data files; 21 source centers agree; both old CSV/definition/placements frames agree; 210 pairs × 4 envelopes × 2 rotations × 2 pitches screened.')
if __name__=='__main__': main()
