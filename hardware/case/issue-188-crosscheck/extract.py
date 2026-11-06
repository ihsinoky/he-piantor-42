"""Read-only stdlib extraction. Run from any cwd; JSON to stdout; no CAD writes."""
from pathlib import Path
import ast, csv, hashlib, io, json, math, re, zipfile
ROOT = Path(__file__).resolve().parents[3]
# Reuse only function definitions from the Stage 1 parser, not its top-level run.
source = ROOT / 'hardware/case/issue-150-stage1/measure.py'
ns = dict(Path=Path, ROOT=ROOT, hashlib=hashlib, json=json, math=math, re=re)
module = ast.parse(source.read_text())
exec(compile(ast.Module(body=[n for n in module.body if isinstance(n, ast.FunctionDef)], type_ignores=[]), str(source), 'exec'), ns)
parse, children, child, inventory = (ns[k] for k in ('parse','children','child','inventory'))
inputs = {}
def read(p):
    data = (ROOT/p).read_bytes()
    inputs[str(p)] = hashlib.sha256(data).hexdigest()
    return data

def board(p):
    read(p)
    return inventory(p), parse(p)
def bounds(points):
    return [min(p[0] for p in points), min(p[1] for p in points), max(p[0] for p in points), max(p[1] for p in points)]
def cam(edge, drill, inv):
    # Intentionally scoped to these straight-line metric 4.6 Gerbers / decimal Excellon.
    s = edge.decode()
    assert '%FSLAX46Y46*%' in s and '%MOMM*%' in s and 'G01*' in s
    points = [(int(x)/1e6,-int(y)/1e6) for x,y in re.findall(r'X(-?\d+)Y(-?\d+)D0[12]\*',s)]
    assert len(points) == 8
    segments = sorted(tuple(sorted((points[i],points[i+1]))) for i in range(0,8,2))
    assert segments == sorted(tuple(sorted(tuple(p) for p in e)) for e in inv['edges'])
    s = drill.decode(); assert 'METRIC' in s and 'G90' in s
    tools = {t:float(d) for t,d in re.findall(r'^T(\d+)C([\d.]+)$',s,re.M)}
    holes=[]; tool=None
    for line in s.splitlines():
        if re.fullmatch(r'T\d+',line): tool=line[1:]
        m=re.fullmatch(r'X(-?[\d.]+)Y(-?[\d.]+)',line)
        if m: holes.append((float(m[1]),-float(m[2]),tools[tool]))
    assert sorted(holes)==sorted((h['x'],h['y'],float(h['drill'][0])) for h in inv['holes'])
    return dict(bounds_xy_mm=bounds(points),npth=holes,all_edges_and_npth_match_native=True)

def fp_geometry(b, ref):
    f=next(f for f in children(b,'footprint') if any(p[1:3]==['Reference',ref] for p in children(f,'property')))
    at=list(map(float,child(f,'at')[1:])); a=math.radians(at[2] if len(at)>2 else 0)
    def xy(p):
        x,y=map(float,p[1:3]); return [at[0]+x*math.cos(a)+y*math.sin(a),at[1]-x*math.sin(a)+y*math.cos(a)]
    out={'at':at,'layer':child(f,'layer')[1]}
    # Footprints carry pads only (no Fab/CrtYd outline, no 3D model); body size is a doc value.
    pts=[]
    for pad in children(f,'pad'):
        px,py=xy(child(pad,'at')); w,h=map(float,child(pad,'size')[1:3])
        pts+=[(px-w/2,py-h/2),(px+w/2,py+h/2)]
    out['pad_bounds_xy']=bounds(pts)
    out['n_pads']=len(children(f,'pad'))
    out['3d_model_count']=len(children(f,'model'))
    return out
mainbase='hardware/kicad/qualification/issue-185-main-rev3/'
main,b=board(mainbase+'inspection/final/main.kicad_pcb')
old=json.loads(read('hardware/case/issue-150-stage1/measurements.json'))
oldmain=old['main']
connectors={r:fp_geometry(b,r) for r in ('J1','J2','J3')}
holes={h['ref']:h for h in main['holes'] if h['ref'].startswith('H')}
expected={'H1':(79,92),'H2':(121,81),'H3':(79,119),'H4':(102,111.5)}
for r,p in expected.items():
    h=holes[r]; assert (h['x'],h['y'])==p and h['drill']==['2.2']
readback=json.loads(read(mainbase+'geometry-check.json'))
assert readback['board_sha256']==main['sha256']
reservations=[]
for z in children(b,'zone'):
    if not children(z,'keepout'): continue
    coords=child(child(z,'polygon'),'pts')
    pts=[list(map(float,p[1:3])) for p in children(coords,'xy')]
    for r,(x,y) in expected.items():
        radii=[math.hypot(px-x,py-y) for px,py in pts]
        if max(abs(v-2.5) for v in radii)<0.001:
            reservations.append(dict(ref=r,layers=child(z,'layers')[1:],vertex_radius_range_mm=[min(radii),max(radii)],keepout=child(z,'keepout')))
assert len(reservations)==4
for z in reservations:
    assert sorted(z['layers'])==['B.Cu','F.Cu','In1.Cu','In2.Cu']
    for kind in ('tracks','vias','copperpour'): assert [kind,'not_allowed'] in z['keepout']
maincam=cam(read(mainbase+'manufacturing/gerber/main-stage2-Edge_Cuts.gm1'),read(mainbase+'manufacturing/gerber/main-stage2-NPTH.drl'),main)
# Signed distance above the north support edge H1 -> H2, positive outside.
def outside(p): return (11*(79-p[0])+42*(92-p[1]))/math.hypot(42,11)
j3x,j3y=connectors['J3']['at'][:2]; j3fab=[j3x-10.375,j3y+0.2,j3x+10.375,j3y+4.45]  # design value: docs/issue-163 body projection X94.625-115.375/Y73.2-77.45
corners=[(x,y) for x in (j3fab[0],j3fab[2]) for y in (j3fab[1],j3fab[3])]
mount=[]
for r,h in holes.items():
    x,y=h['x'],h['y']; x0,y0,x1,y1=main['bounds_xy_mm']
    mount.append(dict(ref=r,xy=[x,y],nearest_edge_mm=min(x-x0,x1-x,y-y0,y1-y),boss_4_5_to_edge_mm=min(x-x0,x1-x,y-y0,y1-y)-2.25,reservation_radial_margin_mm=2.5-2.25))

def rect_gap(a,b):
    dx=max(a[0]-b[2],b[0]-a[2],0); dy=max(a[1]-b[3],b[1]-a[3],0); return math.hypot(dx,dy)
def overlap(a,b): return a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]
def all_pads(bd):
    out=[]
    for f in children(bd,'footprint'):
        ref=next(p[2] for p in children(f,'property') if p[1]=='Reference')
        at=list(map(float,child(f,'at')[1:])); fa=at[2] if len(at)>2 else 0
        a=math.radians(fa)
        for pad in children(f,'pad'):
            pa=list(map(float,child(pad,'at')[1:])); px,py=pa[0],pa[1]
            rot=(pa[2] if len(pa)>2 else 0)  # KiCad stores absolute pad angle in file
            w,h=map(float,child(pad,'size')[1:3])
            if round(rot)%180==90: w,h=h,w
            cx=at[0]+px*math.cos(a)+py*math.sin(a); cy=at[1]-px*math.sin(a)+py*math.cos(a)
            kind=pad[2]
            out.append(dict(ref=ref,kind=kind,shape=pad[3],rect=[cx-w/2,cy-h/2,cx+w/2,cy+h/2],layers=child(pad,'layers')[1:]))
    return out
pads=all_pads(b)
service=[92,71.5,118,79]
ghr=[105-18.75/2,75.325-4.15/2,105+18.75/2,75.325+4.15/2]  # GHR-14V-S projection centred on header body (design value, latch datum unknown)
near_service=sorted({q['ref'] for q in pads if not q['ref'].startswith(('J3','H')) and rect_gap(q['rect'],service)<=0.5})
service_overlap=sorted({q['ref'] for q in pads if not q['ref'].startswith(('J3','H')) and overlap(q['rect'],service)})
hole_pad_clear=[]
for r,h in holes.items():
    best=min(((math.hypot(max(q['rect'][0]-h['x'],0,h['x']-q['rect'][2]),max(q['rect'][1]-h['y'],0,h['y']-q['rect'][3])),q['ref']) for q in pads if not q['ref'].startswith('H') and q['kind']!='np_thru_hole'))
    hole_pad_clear.append(dict(hole=r,nearest_pad_ref=best[1],center_to_pad_edge_mm=best[0],to_boss_4_5_mm=best[0]-2.25,to_reservation_5_0_mm=best[0]-2.5))
def hull(pts):
    pts=sorted(set(pts))
    def cr(o,a,c): return (a[0]-o[0])*(c[1]-o[1])-(a[1]-o[1])*(c[0]-o[0])
    lo=[];up=[]
    for p in pts:
        while len(lo)>1 and cr(lo[-2],lo[-1],p)<=0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up)>1 and cr(up[-2],up[-1],p)<=0: up.pop()
        up.append(p)
    return lo[:-1]+up[:-1]
poly=hull([(h['x'],h['y']) for h in holes.values()])
def seg_dist(p,a,c):
    vx,vy=c[0]-a[0],c[1]-a[1]; t=max(0,min(1,((p[0]-a[0])*vx+(p[1]-a[1])*vy)/(vx*vx+vy*vy))); return math.hypot(p[0]-a[0]-t*vx,p[1]-a[1]-t*vy)
def inside(p): return all((poly[(i+1)%len(poly)][0]-poly[i][0])*(p[1]-poly[i][1])-(poly[(i+1)%len(poly)][1]-poly[i][1])*(p[0]-poly[i][0])>=0 for i in range(len(poly))) or all((poly[(i+1)%len(poly)][0]-poly[i][0])*(p[1]-poly[i][1])-(poly[(i+1)%len(poly)][1]-poly[i][1])*(p[0]-poly[i][0])<=0 for i in range(len(poly)))
def dist_to_polygon(p): return 0.0 if inside(p) else min(seg_dist(p,poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly)))
support={}
for r in ('J1','J2','J3'):
    rects=[q['rect'] for q in pads if q['ref']==r]
    pts=[(x,y) for q in rects for x in (q[0],q[2]) for y in (q[1],q[3])]
    support[r]=dict(pad_corners_outside_hull_max_mm=max(dist_to_polygon(p) for p in pts),pad_corners_outside_hull_min_mm=min(dist_to_polygon(p) for p in pts),corners_inside_hull=sum(inside(p) for p in pts),corners_total=len(pts),pad_bounds_xy=bounds(pts))
support['hull_vertices_xy']=poly
support['hull_area_mm2']=abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly))))/2
layers_of_parts=sorted({l for f in children(b,'footprint') for l in [child(f,'layer')[1]]})
vias=[list(map(float,child(v,'at')[1:3])) for v in children(b,'via')]
north_vias=[v for v in vias if v[1]<85 and 90<v[0]<120]
# Component-set difference against the Stage 1 Main (#121 base)
cur={c['ref']:c for c in main['components']}; prev={c['ref']:c for c in oldmain['components']}
comp_diff=dict(added=sorted(set(cur)-set(prev)),removed=sorted(set(prev)-set(cur)),moved=sorted(r for r in cur if r in prev and cur[r]['at']!=prev[r]['at']),value_changed=sorted(r for r in cur if r in prev and cur[r]['value']!=prev[r]['value']),n_stage150=len(prev),n_rev3=len(cur))
holes_stage=[h for h in oldmain['holes']]
mech=dict(service_rectangle_xy_mm=service,ghr_projection_xy_mm=ghr,pads_within_0_5mm_of_service_rect=near_service,pads_overlapping_service_rect=service_overlap,hole_to_pad=hole_pad_clear,support_hull=support,footprint_layers=layers_of_parts,north_region_vias_x90_120_y_lt_85=north_vias,component_diff=comp_diff,stage150_holes=holes_stage)
wings={}; rows=[]; wing_boards={}
frozen=json.loads(read('hardware/case/issue-150-stage1/inputs/issue149-interface.json'))
for pitch in (16,17):
    base=f'hardware/kicad/qualification/issue-149-wing-silkscreen/{pitch}mm/'
    inv,wb=board(base+f'wing-{pitch}mm-silk149.kicad_pcb')
    stage=old['wings'][str(pitch)]['native']
    for k in ('bounds_xy_mm','thickness_mm','holes','components'): assert inv[k]==stage[k]==frozen[str(pitch)]['geometry'][k],k
    wing_boards[pitch]=(inv,wb)
    byref={c['ref']:c for c in inv['components']}
    keys=list(csv.DictReader(io.StringIO(read(f'hardware/case/issue-150-stage1/keys-{pitch}mm.csv').decode())))
    assert len(keys)==21
    for k in keys:
        c=byref[k['sensor']]; dx=c['at'][0]-float(k['kicad_x_mm']); dy=c['at'][1]-float(k['kicad_y_mm'])
        angle=c['at'][2] if len(c['at'])>2 else 0
        assert dx==dy==angle==float(k['rotation_deg'])==0 and c['layer']=='F.Cu'
        rows.append(dict(pitch_mm=pitch,key=k['key'],sensor=k['sensor'],x_mm=c['at'][0],y_mm=c['at'][1],dx_mm=dx,dy_mm=dy,rotation_deg=angle,layer=c['layer']))
    zp=f'hardware/kicad/qualification/issue-149-wing-silkscreen/wing-{pitch}mm-silk149-review.zip'
    with zipfile.ZipFile(io.BytesIO(read(zp))) as z:
        names=z.namelist(); en=next(n for n in names if 'Edge_Cuts' in n); dn=next(n for n in names if 'NPTH' in n)
        ed,dr=z.read(en),z.read(dn)
        assert ed==read(base+'gerber/'+Path(en).name) and dr==read(base+'gerber/'+Path(dn).name)
        manufacturing=cam(ed,dr,inv)
    wings[str(pitch)]=dict(native=inv,zip_path=zp,manufacturing=manufacturing,stage150_and_frozen149_match=True,keys_checked=21,maximum_key_delta_mm=0)
# BOM is a part list, with no height field; do not assign absent Z dimensions.
bom=list(csv.DictReader(io.StringIO(read(mainbase+'main-bom.csv').decode())))
for p in ('docs/decisions.md','docs/issue-150-case-stage1.md','docs/issue-160-main-dual-wing-stage2.md','docs/issue-163-main-dual-wing-plan-c.md','docs/issue-175-main-dual-wing-final2.md','docs/issue-185-main-rev3.md','docs/project-status.md','docs/issue-158-vera-wing-stage1.md',mainbase+'README.md','hardware/kicad/qualification/issue-149-wing-silkscreen/publication.json'):
    read(p)
import importlib.util
spec=importlib.util.spec_from_file_location('interference',Path(__file__).resolve().parent/'interference.py'); itf=importlib.util.module_from_spec(spec); spec.loader.exec_module(itf)
interference,zone_maps=itf.run(dict(children=children,child=child,all_pads=all_pads,main_b=b,main=main,connectors=connectors,wings=wing_boards,rows=rows,mech=mech,
    wing_j={p:next(c['at'][:2] for c in wing_boards[p][0]['components'] if c['ref']=='J_WING') for p in wing_boards}))
out=dict(units='mm',frame='KiCad top view X right Y down; separate PCB frames are not an assembly',main=main,stage150_main=oldmain,connectors=connectors,mounting=mount,reservations=reservations,main_manufacturing=maincam,j3_support=dict(body_projection_xy_mm=j3fab,pad_corner_outside_range_mm=[min(outside((x,y)) for x in (connectors['J3']['pad_bounds_xy'][0],connectors['J3']['pad_bounds_xy'][2]) for y in (connectors['J3']['pad_bounds_xy'][1],connectors['J3']['pad_bounds_xy'][3])),max(outside((x,y)) for x in (connectors['J3']['pad_bounds_xy'][0],connectors['J3']['pad_bounds_xy'][2]) for y in (connectors['J3']['pad_bounds_xy'][1],connectors['J3']['pad_bounds_xy'][3]))],north_edge=['H1','H2'],origin_outside_mm=outside(connectors['J3']['at'][:2]),body_center_outside_mm=outside(((j3fab[0]+j3fab[2])/2,(j3fab[1]+j3fab[3])/2)),body_corner_outside_range_mm=[min(map(outside,corners)),max(map(outside,corners))],service_rectangle_xy_mm=[92,71.5,118,79],service_to_H2_reservation_mm=math.hypot(121-118,81-79)-2.5,service_to_H2_boss4_5_mm=math.hypot(3,2)-2.25,service_to_north_edge_mm=1.5),wings=wings,bom_fields=list(bom[0]),height_verdict='判定不能（不足入力：全実装部品の保証最大高さ・実装浮き・下面はんだ・嵌合体とケーブルのZ包絡）',harness=dict(nominal_length=100,stage150_route_target=70,stage150_slack_total=30,conductor_count=14,flat_wire_width_max=14*1.0,proposed_channel_width=18,planar_center_distance_upper_bound_mm={f'R{R}':{'route_70':70-math.pi*R+2*R,'route_100_if_no_slack':100-math.pi*R+2*R} for R in (3,5,8)},j2_j3_pad_row_separation_mm=116-73,actual_route_verdict='判定不能（不足入力：各板の組立位置・角度・Z、ハーネス有効長基準、実線材曲げ条件と固定点）'),mechanics=mech,interference=interference,input_sha256=inputs)
print(json.dumps(out,ensure_ascii=False,indent=2))
# CSV is derived from the same successful comparisons; emitted only on request.
import sys
if '--zonemap' in sys.argv:
    Path(sys.argv[sys.argv.index('--zonemap')+1]).write_text('\n'.join(l for f in 'FB' for l in zone_maps[f]+[''])+'\n')
if '--csv' in sys.argv:
    sys.stdout.seek if False else None
    # JSON remains stdout; CSV path must be explicitly supplied by caller.
    with Path(sys.argv[sys.argv.index('--csv')+1]).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n'); w.writeheader(); w.writerows(rows)
