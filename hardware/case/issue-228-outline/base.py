"""Issue #198 final case data (Wing Rev.3 final CSV, D-034). Nominal mechanical design, not a production release.
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
                      export_step, export_stl, import_step)

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
    inputs=[args.geometry, HERE/'outline.py']
    variants={v['side']:v for v in json.loads(args.geometry.read_text())['variants'] if v['pitch_mm']==args.pitch}
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
        datum=variants[side]['transform']['datum_local']
        a,b=datum
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
        gh=variants[side]['connector']['assembly']
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
    print('Extracted inputs', flush=True)
    # One bottom sheet; side outlines follow boards, with a short UDB-to-main neck.
    cavity=unary_union([g.buffer(P['cavity_clearance']+.002,join_style=2) for g in boards.values()]+[box(-11,-24,11,12)]).simplify(.002,preserve_topology=True)
    legacy_outer=cavity.buffer(P['wall'],join_style=2)
    from outline import proposed_outline, usb_access
    outer=proposed_outline(cavity, boards, P['wall'], P['cavity_clearance']+.002)
    assert outer.geom_type=='Polygon'
    ring=outer.difference(cavity)
    key_union=unary_union([p for v in keycaps.values() for p in v])
    # Added outline material stays flush; preserve the existing high-wall masks.
    upper=legacy_outer.difference(cavity).difference(unary_union(palms)).difference(key_union.buffer(P['key_wall_clearance'],join_style=2)).intersection(outer)
    # Round 2 closes the north silhouette. Continue the existing wall height
    # over the new north material; all added palm material stays flush.
    north_added=ring.difference(legacy_outer).intersection(box(-300,-200,300,-45)).difference(key_union.buffer(P['key_wall_clearance'],join_style=2))
    upper=upper.union(north_added)
    # All stepped south-facing edges, not only the old south strip, stay flush.
    for side,v in variants.items():
        m=transforms[side]['matrix'];t=transforms[side]['translation']
        def tr(q):return [sum(m[i][j]*q[j] for j in range(2))+t[i] for i in range(2)]
        outline=Polygon([[float(r['x_mm']),float(r['y_mm'])] for r in rows(args.csv_dir/f'outline-{args.pitch}mm-{side}.csv')])
        # Union rays going south from every key keeps palm-facing staircase flush.
        palm=unary_union([Polygon([tr((x,y)) for x,y in [(k.bounds[0]-3,k.bounds[1]),(k.bounds[2]+3,k.bounds[1]),(k.bounds[2]+3,-100),(k.bounds[0]-3,-100)]]) for k in [rect_key(float(r['x_mm']),float(r['y_mm']),float(r['rotation_deg']),P['keycap_square']) for r in rows(args.csv_dir/f'keys-{args.pitch}mm-{side}.csv')]])
        palms.append(palm)
    upper=upper.difference(unary_union(palms))
    # Open north U-slot instead of a bridged aperture: no unsupported roof.
    usb_slot=usb_access(outer,usb_front[0])
    upper=upper.difference(usb_slot)
    # Low rim, south flush at Wing top. USB open-top slot begins at flush rim top (11.2 by default).
    top=P['pcb_bottom']+P['pcb_thickness']
    cache_key=hashlib.sha256((sha(Path(__file__))+sha(HERE/'outline.py')+str(args.palm_offset)+''.join(sha(p) for p in sorted(set(inputs)))).encode()).hexdigest()
    cache=ROOT/'.issue228-runtime'/('outline-base-'+str(args.pitch)+'-'+cache_key+'.step')
    if cache.exists():
        body=import_step(cache)
    else:
        print('Building tray', flush=True)
        body=prism(outer,0,P['bottom']).fuse(prism(ring,P['bottom'],top+args.palm_offset-P['bottom']))
        if not upper.is_empty:body=body.fuse(prism(upper,top+args.palm_offset,P['upper_wall_height']-args.palm_offset))
        print('Adding bosses', flush=True)
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
        print('Tray done',flush=True)
        export_step(body,cache)
    # PCB mounting holes are represented in assembly too.
    board_solids=[]
    for name,g in boards.items():
        thick=P['udb_thickness'] if name=='udb' else P['pcb_thickness']
        s=prism(g,P['pcb_bottom'],thick)
        for h in holes:
            if h['board']==name:s=s.cut(cylinder(*h['xy'],h['diameter']/2,P['pcb_bottom'],thick))
        s.label=name;board_solids.append(s)
    body.label='integrated_tray'
    from details import finish
    return finish(args, locals())
