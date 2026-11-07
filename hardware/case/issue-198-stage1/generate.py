"""Issue #198 Stage 1. Nominal mechanical study, not a production release.
Run from any directory with build123d 0.13, shapely 2.2, sexpdata 1.0.2.
All XY exported in assembly frame (X right, Y south), Z up, mm.
"""
from pathlib import Path
import argparse, csv, hashlib, itertools, json, math, sys
sys.dont_write_bytecode = True
import sexpdata
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from build123d import (Face, Wire, Vector, Solid, Plane, Compound, extrude,
                      export_step, export_stl)

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
A2 = ROOT / 'hardware/kicad/qualification/issue-196-main-rev4-phasea2'
PB = ROOT / 'hardware/kicad/qualification/issue-196-main-rev4-phaseb'
# Explicit design proposals; component heights / cable radii are unqualified.
P = dict(bottom=2., pcb_bottom=10., pcb_thickness=1.2, udb_thickness=1.6,
         cavity_clearance=.5, wall=2., upper_wall_height=4., boss_diameter=4.5,
         screw_pilot_diameter=1.7, udb_boss_diameter=3.5,
         switch_square=15.8, keycap_square=17.0, keycap_height=14.,
         key_wall_clearance=.25, split_x=3.5, cable_diameter=2.,
         gh_mated_height=7., bend_radius=5., bottom_component_height=3.)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, x): p.write_text(json.dumps(x, indent=2, ensure_ascii=False)+'\n')
def tag(n): return str(n[0]) if isinstance(n, list) and n else ''
def children(n, t): return [v for v in n if isinstance(v, list) and tag(v)==t]
def child(n,t): return next(iter(children(n,t)), None)
def ref(n):
    for v in children(n,'property') + children(n,'fp_text'):
        if str(v[1]).lower()=='reference': return str(v[2])
    return None

def read_board(p): return sexpdata.loads(p.read_text())
def xy(n): return list(map(float,n[1:3]))
def rows(p):
    with p.open() as f: return list(csv.DictReader(f))
def coords(g): return [list(q) for q in list(g.exterior.coords)[:-1]]
def polygons(g):
    if g.is_empty: return []
    if g.geom_type=='Polygon': return [g]
    return [p for c in g.geoms for p in polygons(c)]
def prism(g,z,h):
    solids=[]
    for poly in polygons(g):
        outer=Wire.make_polygon([Vector(x,y,z) for x,y in list(poly.exterior.coords)[:-1]],close=True)
        inner=[Wire.make_polygon([Vector(x,y,z) for x,y in list(r.coords)[:-1]],close=True) for r in poly.interiors]
        solids.append(extrude(Face(outer,inner),amount=h,dir=(0,0,1)))
    assert solids
    return solids[0] if len(solids)==1 else Compound(children=solids)
def cylinder(x,y,r,z,h): return Solid.make_cylinder(r,h,Plane(origin=(x,y,z)))
def size(shape):
    b=shape.bounding_box();return [b.size.X,b.size.Y,b.size.Z]
def rect_key(x,y,a,w):
    c=math.cos(math.radians(a));s=math.sin(math.radians(a))
    return Polygon([(x+c*u-s*v,y+s*u+c*v) for u,v in [(-w/2,-w/2),(w/2,-w/2),(w/2,w/2),(-w/2,w/2)]])

def generate(args):
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    inputs=[]
    def use(p): inputs.append(p);return p
    plan=json.loads(use(A2/'geometry-plan.json').read_text())
    pcbfile=use(PB/'inspection/final/main.kicad_pcb')
    pcb=read_board(pcbfile)
    footprints=children(pcb,'footprint')
    mainparts={ref(n):n for n in footprints}
    # Check actual Phase B poses, not just a historical plan or PASS flag.
    for comp in plan['main']['placements']:
        at=child(mainparts[comp['ref']],'at')
        assert math.dist([float(at[1])-100,float(at[2])-70],comp['at_mm'])<2e-6
        assert abs((float(at[3]) if len(at)>3 else 0)-comp['angle_deg'])<1e-6
    edges=[]
    for n in children(pcb,'gr_line'):
        if str(child(n,'layer')[1])=='Edge.Cuts':
            edges.extend([[v[0]-100,v[1]-70] for v in [xy(child(n,'start')),xy(child(n,'end'))]])
    main=Polygon(edges).convex_hull
    assert main.symmetric_difference(Polygon(plan['main']['outline_xy_mm'])).area<1e-3
    boards={'main':main}; holes=[]; transforms={}; switches={}; keycaps={}; palms=[]; wings={}
    for hole in plan['main']['holes']:
        actual=xy(child(mainparts[hole['ref']],'at'))
        assert math.dist([actual[0]-100,actual[1]-70],hole['xy_mm'])<2e-6
        holes.append(dict(board='main',ref=hole['ref'],xy=hole['xy_mm'],diameter=2.2,boss_diameter=P['boss_diameter']))
    c=math.sqrt(3)/2
    for side,sgn in [('left',1),('right',-1)]:
        op=use(args.csv_dir/f'outline-{args.pitch}mm-{side}.csv')
        local=[[float(r['x_mm']),float(r['y_mm'])] for r in rows(op)]
        a=max(x for x,y in local) if sgn==1 else min(x for x,y in local)
        b=max(y for x,y in local)
        m=[[c,.5*sgn],[.5*sgn,-c]]
        t=[-sgn-m[0][0]*a-m[0][1]*b,-m[1][0]*a-m[1][1]*b]
        def transform(pt): return [sum(m[i][j]*pt[j] for j in range(2))+t[i] for i in range(2)]
        assert math.dist(transform([a,b]),[-sgn,0])<1e-10
        for i in range(2):
            assert math.dist(m[i],plan['wing'][str(args.pitch)][side]['transform_matrix'][i])<1e-12
        transforms[side]=dict(matrix=m,translation=t,datum_local=[a,b],datum_assembly=[-sgn,0])
        name='wing_'+side
        boards[name]=Polygon([transform(pt) for pt in local])
        kr=rows(use(args.csv_dir/f'keys-{args.pitch}mm-{side}.csv'))
        switches[name]=[]; keycaps[name]=[]
        for k in kr:
            vals=[float(k[v]) for v in ['x_mm','y_mm','rotation_deg']]
            for target,width in [(switches[name],P['switch_square']),(keycaps[name],P['keycap_square'])]:
                target.append(Polygon([transform(pt) for pt in coords(rect_key(*vals,width))]))
        for h in rows(use(args.csv_dir/f'holes-{args.pitch}mm-{side}.csv')):
            if h['kind']=='mounting':
                holes.append(dict(board=name,ref=h['reference'],xy=transform([float(h['x_mm']),float(h['y_mm'])]),diameter=float(h['diameter_mm']),boss_diameter=P['boss_diameter']))
        # Entire south band, including chamfer and both corners, is flush.
        south=min(y for x,y in local)
        palm=Polygon([transform(pt) for pt in [(min(x for x,y in local)-10,south-15),(max(x for x,y in local)+10,south-15),(max(x for x,y in local)+10,south+8),(min(x for x,y in local)-10,south+8)]])
        palms.append(palm)
        definition=json.loads(use(ROOT/f'hardware/jitx/wing/generated/wing-rev2-{args.pitch}mm-{side}/definition.json').read_text())
        connector=next(k for k in definition['components'] if k['reference']=='J_WING')
        gh=transform([connector['x_mm'],connector['y_mm']])
        assert math.dist(gh,plan['wing'][str(args.pitch)][side]['J1_xy_mm'])<1e-8
        wings[side]=dict(gh=gh,south_local_y=south,palm_local_y_max=south+8)
    # Source UDB C3: local copy pinned to upstream commit; no schematic image scaling.
    ufile=use(A2/'inputs/udb/c3.kicad_pcb');udb=read_board(ufile)
    mods={ref(n):n for n in children(udb,'module')}
    anchor=xy(child(mods['J2'],'at'))
    def utransform(pt): return [pt[0]-anchor[0],pt[1]-anchor[1]-20]
    # Four R2 corners, sampled at <=2.8125 degrees, from actual legacy Edge.Cuts.
    outline=[]
    for n in udb:
        if tag(n) not in ('gr_line','gr_arc') or str(child(n,'layer')[1])!='Edge.Cuts':continue
        if tag(n)=='gr_line':outline.extend([utransform(xy(child(n,k))) for k in ('start','end')])
        else:
            center=xy(child(n,'start'));end=xy(child(n,'end'))
            angle=float(child(n,'angle')[1]);a=math.atan2(end[1]-center[1],end[0]-center[0]);r=math.dist(center,end)
            for j in range(33):
                theta=a+math.radians(angle)*j/32
                outline.append(utransform([center[0]+r*math.cos(theta),center[1]+r*math.sin(theta)]))
    boards['udb']=Polygon(outline).convex_hull
    assert all(abs(a-b)<1e-8 for a,b in zip(boards['udb'].bounds,plan['udb']['pcb_bbox_xy_mm']))
    for name in ['MH1','MH2','MH3','MH4']:
        mod=mods[name];pad=child(mod,'pad')
        holes.append(dict(board='udb',ref=name,xy=utransform(xy(child(mod,'at'))),diameter=float(child(pad,'drill')[1]),boss_diameter=P['udb_boss_diameter']))
    # USB connector front from C3 Fab geometry (local +Y at rotation 180).
    usb_origin=xy(child(mods['J1'],'at'))
    usb_front=utransform([usb_origin[0],usb_origin[1]-6.8])
    # One bottom sheet; side outlines follow boards, with a short UDB-to-main neck.
    cavity=unary_union([g.buffer(P['cavity_clearance'],join_style=2) for g in boards.values()]+[box(-11,-24,11,12)])
    outer=cavity.buffer(P['wall'],join_style=2)
    assert outer.geom_type=='Polygon'
    ring=outer.difference(cavity)
    key_union=unary_union([p for v in keycaps.values() for p in v])
    upper=ring.difference(unary_union(palms)).difference(key_union.buffer(P['key_wall_clearance'],join_style=2))
    # Open north U-slot instead of a bridged aperture: no unsupported roof.
    usb_slot=box(usb_front[0]-6,-50,usb_front[0]+6,-34)
    upper=upper.difference(usb_slot)
    # Low rim, south flush at Wing top. USB slot begins at UDB top (11.6).
    top=P['pcb_bottom']+P['pcb_thickness']
    body=prism(outer,0,P['bottom']).fuse(prism(ring,P['bottom'],top-P['bottom']))
    if not upper.is_empty:body=body.fuse(prism(upper,top,P['upper_wall_height']))
    for h in holes:
        x,y=h['xy'];boss=cylinder(x,y,h['boss_diameter']/2,P['bottom'],P['pcb_bottom']-P['bottom'])
        body=body.fuse(boss)
        body=body.cut(cylinder(x,y,P['screw_pilot_diameter']/2,P['bottom'],P['pcb_bottom']-P['bottom']+.01))
    # Narrow load-spreading ribs directly under Main J2/J3, no bottom components on Main.
    ribs=[]
    for name in ['J2','J3']:
        comp=next(p for p in plan['main']['placements'] if p['ref']==name)
        x,y=comp['at_mm'];g=box(x-1,y-7,x+1,y+7).intersection(main.buffer(-.5))
        ribs.append(dict(ref=name,polygon=coords(g)))
        body=body.fuse(prism(g,P['bottom'],P['pcb_bottom']-P['bottom']))
    assert body.is_valid and len(body.solids())==1
    # PCB mounting holes are represented in assembly too.
    board_solids=[]
    for name,g in boards.items():
        thick=P['udb_thickness'] if name=='udb' else P['pcb_thickness']
        s=prism(g,P['pcb_bottom'],thick)
        for h in holes:
            if h['board']==name:s=s.cut(cylinder(*h['xy'],h['diameter']/2,P['pcb_bottom'],thick))
        s.label=name;board_solids.append(s)
    body.label='integrated_tray'
    export_step(body,out/'tray.step');export_stl(body,out/'tray.stl',tolerance=.05,angular_tolerance=.15)
    export_step(Compound(children=[body]+board_solids),out/'assembly.step')
    pieces=[]
    for name,clip in [('left',box(-300,-200,P['split_x'],200)),('right',box(P['split_x'],-200,300,200))]:
        part=Compound(children=list(body.intersect(prism(clip,-1,40))));assert part.is_valid and len(part.solids())==1
        export_step(part,out/f'tray-{name}.step');export_stl(part,out/f'tray-{name}.stl',tolerance=.05,angular_tolerance=.15)
        dims=size(part);assert dims[0]<220 and dims[1]<220
        pieces.append(dict(name=name,size_mm=dims,solid_count=len(part.solids()),volume_mm3=part.volume))
    clearances=[]
    for (a,g),(b,h) in itertools.combinations(boards.items(),2):
        overlap=g.intersection(h).area;assert overlap<1e-8
        clearances.append(dict(a=a,b=b,gap_mm=g.distance(h),overlap_mm2=overlap))
    harness=[]
    for h in plan['harness']:
        if h['pitch_mm']!=args.pitch:continue
        route=h['planning_route_xy_mm'];length=sum(math.dist(a,b) for a,b in zip(route,route[1:]))
        assert abs(length+30-h['planning_length_mm'])<1e-8
        # Reproduce original route as a diagnostic, not a qualified harness path.
        swept=LineString(route).buffer(P['cable_diameter']/2,join_style=1)
        collisions=[f'{n}:{i}' for n,v in keycaps.items() for i,k in enumerate(v) if k.intersection(swept).area>1e-8]
        harness.append(dict(side=h['side'],chord_mm=math.dist(route[0],wings[h['side']]['gh']),route_mm=length,with_allowance_mm=length+30,nominal_mm=200,route=route,nominal_cable_keycap_xy_collisions=collisions,route_outside_tray_mm2=swept.difference(outer).area,status='UNRESOLVED_3D_ROUTE: original polyline is a length estimate; may cross keycaps / leave tray'))
    # Measure walls against nominal switch and keycap envelopes, at their applicable Z.
    check=dict(pcb_pairwise=clearances,
        switch_upper_wall_min_mm=min(upper.distance(k) for v in switches.values() for k in v),
        keycap_upper_wall_min_mm=min(upper.distance(k) for v in keycaps.values() for k in v),
        keycap_upper_wall_overlap_mm2=upper.intersection(key_union).area,
        palm_above_pcb_wall_area_mm2=upper.intersection(unary_union(palms)).area,
        boss_axis_to_pcb_hole_max_mm=0.,
        main_phaseb_pose_count_checked=len(plan['main']['placements']),
        main_phaseb_outline_symmetric_difference_mm2=main.symmetric_difference(Polygon(plan['main']['outline_xy_mm'])).area,
        rib_to_main_pcb_gap_mm=0.,
        underside_void_mm=P['pcb_bottom']-P['bottom'],
        wing_bottom_components_to_floor_nominal_mm=P['pcb_bottom']-P['bottom_component_height']-P['bottom'],
        gh_open_top_reservation_z_mm=[top,top+P['gh_mated_height']+P['bend_radius']+P['cable_diameter']/2],
        gh_harness=harness,
        sh=dict(chord_mm=40.,candidate_length_mm=100.,allowance_mm=30.,remaining_mm=30.,status='conditional: open central neck; verify actual housing, 1:1 cable, bend radius and slack retention'),
        usb=dict(origin=utransform(usb_origin),fab_front_xy_mm=usb_front,slot_xy_bounds=list(usb_slot.bounds),slot_z_mm=[top,None],status='open U-slot; height / plug overmould are placeholders; C3 Fab front recessed from north case edge'),
        fasteners='M2 pilot 1.7 proposal, Wing/Main contact diameter 4.5, UDB 3.5; fit and thread engagement unqualified')
    assert check['keycap_upper_wall_overlap_mm2']<1e-8
    assert check['palm_above_pcb_wall_area_mm2']<1e-8
    assert check['keycap_upper_wall_min_mm']>=P['key_wall_clearance']-1e-8
    dims=size(body)
    # Rotation cannot make the tray fit a 220mm square. 0.1-degree sampling
    # plus a conservative angular Lipschitz bound encloses the true minimum.
    vertices=coords(outer);best=(float('inf'),0.)
    for j in range(901):
        theta=math.radians(j/10);ct,st=math.cos(theta),math.sin(theta)
        xs=[ct*x-st*y for x,y in vertices];ys=[st*x+ct*y for x,y in vertices]
        side=max(max(xs)-min(xs),max(ys)-min(ys))
        best=min(best,(side,j/10))
    angular_bound=2*max(math.hypot(x,y) for x,y in vertices)*math.radians(.05)
    assert best[0]-angular_bound>220
    data=dict(schema='issue198-stage1-v1',units='mm',frame='top view X right Y south, Z up; bottom Z=0',pitch_mm=args.pitch,parameters=P,wing_transforms=transforms,wing_details=wings,boards={k:dict(outline=coords(g),bbox=list(g.bounds)) for k,g in boards.items()},mounts=holes,ribs=ribs,checks=check,tray=dict(size_mm=dims,volume_mm3=body.volume,solid_count=len(body.solids()),valid=body.is_valid),printing=dict(bed_mm=[220,220],one_piece_fits=False,best_sampled_square_mm=best[0],best_sampled_rotation_deg=best[1],square_lower_bound_mm=best[0]-angular_bound,angular_search_step_deg=.1,split_plane_x_mm=P['split_x'],pieces=pieces,joining_proposal='two detachable underside 20x12x3 splice plates at Y=-8 and 55; two M2 screws per plate, pilot layout / feet / tolerances deferred to Stage 2; split CAD has plain butt faces'),inputs_sha256={str(p.relative_to(ROOT) if p.is_relative_to(ROOT) else p):sha(p) for p in sorted(set(inputs))},udb_upstream=dict(url='https://github.com/Unified-Daughterboard/UDB-C-Legacy',commit='2ecdd7e0482ecbd3ffe9af04966ab3555f7fc33c',outline_arc_chord_error_mm=2*(1-math.cos(math.pi/128))),unresolved=['GH routed 3D cable and real connector maximum height/radius','SH slack and latch access, USB plug overmould/height','physical switch/keycap envelope and bottom Hall stack','fastener fit, splice details and print shrinkage'])
    save(out/'dimensions.json',data)
    # Review drawing uses the same XY as STEP, includes holes, palm bands and cable diagnostic.
    x0,y0,x1,y1=outer.bounds
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0-5} {y0-12} {x1-x0+10} {y1-y0+20}" width="1400">',f'<text x="{x0}" y="{y0-5}" font-size="3">Issue 198 Stage 1 / {args.pitch}mm / X right, Y south / orange: UNQUALIFIED cable estimate</text>']
    def draw(g,fill,stroke,opacity=1):
        for p in polygons(g): svg.append('<polygon points="'+' '.join(f'{x:.4f},{y:.4f}' for x,y in p.exterior.coords)+f'" fill="{fill}" stroke="{stroke}" stroke-width=".25" opacity="{opacity}"/>')
    draw(outer,'#dfd8c9','#433');draw(upper,'#8d8170','#433')
    for g in boards.values():draw(g,'#73aa93','#264',.75)
    draw(unary_union(palms).intersection(ring),'#ed87a3','#922')
    for v in keycaps.values():
        for k in v:draw(k,'none','#314')
    for h in holes:svg.append(f'<circle cx="{h["xy"][0]}" cy="{h["xy"][1]}" r="{h["diameter"]/2}" fill="white" stroke="#111" stroke-width=".2"/>')
    for h in harness:svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in h['route'])+'" fill="none" stroke="#e70" stroke-width="1"/>')
    svg.append(f'<line x1="{P["split_x"]}" y1="{y0}" x2="{P["split_x"]}" y2="{y1}" stroke="#00f" stroke-width=".4" stroke-dasharray="2 2"/>')
    svg.append('</svg>');(out/'review.svg').write_text('\n'.join(svg)+'\n')
    save(out/'exports-sha256.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.suffix in ('.step','.stl','.svg','.json') and p.name not in ('exports-sha256.json','verification.json')})
    print(json.dumps(dict(pitch=args.pitch,size_mm=dims,pieces=pieces,checks=check),ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pitch',type=int,choices=[16,17],default=17)
    p.add_argument('--csv-dir',type=Path,default=ROOT/'hardware/case/issue-194-rev2')
    p.add_argument('--out',type=Path,default=None)
    args=p.parse_args()
    if args.out is None: args.out=HERE/f'{args.pitch}mm'
    generate(args)
