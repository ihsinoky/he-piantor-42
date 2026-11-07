"""Issue #200 geometry study only. Python 3 + shapely 2.2.0 + sexpdata 1.0.2.
Run from anywhere; writes only beside this script and docs/issue-200-wing-rev3-stage1.md.
The native boards are parsed, never modified. All distances are nominal mm.
"""
from pathlib import Path
import csv, json, math, hashlib, collections
import sexpdata
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from shapely.affinity import affine_transform
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
W=ROOT/'hardware/kicad/qualification/issue-194-wing-rev2'
C=ROOT/'hardware/case/issue-194-rev2'
inputs={}
def use(p):
    inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest();return p

def load(p):return json.loads(use(p).read_text())
def rows(p):return list(csv.DictReader(use(p).open()))
def coords(p):return [list(x) for x in list(p.exterior.coords)[:-1]]
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def children(n,t):return [x for x in n if tag(x)==t]
def child(n,t):return next(iter(children(n,t)),None)
def val(n,t,default=None):
    v=child(n,t);return v[1] if v is not None else default

def xy(n):return [float(n[1]),float(n[2])]
def square(x,y,a,w):
    a=math.radians(a);c,s=math.cos(a),math.sin(a)
    return Polygon([(x+c*u-s*v,y+s*u+c*v) for u,v in [(-w/2,-w/2),(w/2,-w/2),(w/2,w/2),(-w/2,w/2)]])
def circle(x,y,r):return Point(x,y).buffer(r,quad_segs=32)
def transform(g,m,t):return affine_transform(g,[*m[0],*m[1],*t])
def tx(p,m,t):return [sum(m[i][j]*p[j] for j in range(2))+t[i] for i in range(2)]
def inv(p,m,t):return [sum(m[j][i]*(p[j]-t[j]) for j in range(2)) for i in range(2)]
def mirror(g,s):return affine_transform(g,[s,0,0,1,0,0])
def writecsv(name,data,fields):
    with (HERE/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(data)
def roundroute(points,r=5.):
    # Exact circular fillets; polyline approximation chord error <0.00005 mm.
    samples=[points[0]]; arcs=[];removed=0.;added=0.
    for a,b,c in zip(points,points[1:],points[2:]):
        u=[(b[i]-a[i])/math.dist(a,b) for i in range(2)]
        v=[(c[i]-b[i])/math.dist(b,c) for i in range(2)]
        phi=math.acos(max(-1,min(1,sum(x*y for x,y in zip(u,v)))))
        if phi<1e-9: samples.append(b);continue
        trim=r*math.tan(phi/2);assert trim<min(math.dist(a,b),math.dist(b,c))/2
        q=[b[i]-trim*u[i] for i in range(2)];e=[b[i]+trim*v[i] for i in range(2)]
        sign=1 if u[0]*v[1]-u[1]*v[0]>0 else -1
        center=[q[0]-sign*r*u[1],q[1]+sign*r*u[0]]
        theta=math.atan2(q[1]-center[1],q[0]-center[0]);n=max(2,math.ceil(phi/math.radians(.5)))
        samples.append(q)
        samples.extend([[center[0]+r*math.cos(theta+sign*phi*j/n),center[1]+r*math.sin(theta+sign*phi*j/n)] for j in range(1,n+1)])
        assert math.dist(samples[-1],e)<1e-8
        arcs.append(dict(center=center,start=q,end=e,radius_mm=r,sweep_deg=sign*math.degrees(phi)))
        removed+=2*trim;added+=r*phi
    samples.append(points[-1]);length=sum(math.dist(a,b) for a,b in zip(points,points[1:]))-removed+added
    return samples,arcs,length

def native_inventory(pcb,removed,new,definition):
    """All native copper primitives intersecting removed substrate (finite widths).
    Footprints use pad extents + explicit conservative body boxes, not centers only.
    Zone outlines and EACH filled_polygon are separately inventoried, by UUID/index.
    """
    data=[];components=[];holes=[];nets={str(n[1]):str(n[2]) for n in children(pcb,'net')}
    def net(n):return nets.get(str(val(n,'net','')),str(val(n,'net','')))
    def record(n,g,kind,idx,layer=None,name=None):
        if g.is_empty or g.intersection(removed).area<1e-10:return
        it=g.intersection(removed)
        data.append(dict(kind=kind,index=idx,uuid=str(val(n,'uuid','')),net=name if name is not None else net(n),layer=layer or str(val(n,'layer','')),removed_area_mm2=it.area,geometry_bbox_local=list(g.bounds)))
    for idx,n in enumerate(pcb):
        typ=tag(n)
        if typ=='segment':
            a=xy(child(n,'start'));b=xy(child(n,'end'))
            g=LineString([(a[0]-100,100-a[1]),(b[0]-100,100-b[1])]).buffer(float(val(n,'width'))/2)
            record(n,g,'segment',idx)
        elif typ=='via':
            x,y=xy(child(n,'at'));record(n,circle(x-100,100-y,float(val(n,'size'))/2),'via',idx,layer=','.join(map(str,child(n,'layers')[1:])))
        elif typ=='arc':
            raise AssertionError('Native copper arc needs explicit implementation')
        elif typ=='zone':
            for j,poly in enumerate(children(n,'polygon')):
                pts=children(child(poly,'pts'),'xy')
                g=Polygon([(float(q[1])-100,100-float(q[2])) for q in pts]);record(n,g,'zone_outline',f'{idx}:{j}')
            for j,poly in enumerate(children(n,'filled_polygon')):
                pts=children(child(poly,'pts'),'xy')
                g=Polygon([(float(q[1])-100,100-float(q[2])) for q in pts])
                if not g.is_valid:g=g.buffer(0)
                record(n,g,'zone_fill',f'{idx}:{j}',layer=str(val(poly,'layer','')))
        elif typ=='footprint':
            ref=next(str(q[2]) for q in children(n,'property') if str(q[1])=='Reference')
            a=child(n,'at');x,y=float(a[1])-100,100-float(a[2]);ang=float(a[3]) if len(a)>3 else 0
            pads=[]
            for pad in children(n,'pad'):
                at=child(pad,'at');sz=child(pad,'size');px,py=float(at[1]),-float(at[2]);ca,sa=math.cos(math.radians(ang)),math.sin(math.radians(ang))
                pa=(float(at[3]) if len(at)>3 else ang) # native pad angle absolute
                # Rectangular pad dimensions with native absolute pad angle.
                base=box(-float(sz[1])/2,-float(sz[2])/2,float(sz[1])/2,float(sz[2])/2)
                cp,sp=math.cos(math.radians(pa)),math.sin(math.radians(pa))
                g=affine_transform(base,[cp,-sp,sp,cp,x+ca*px-sa*py,y+sa*px+ca*py]);pads.append(g)
                pn=child(pad,'net');record(pad,g,'pad',f'{ref}:{pad[1]}',layer=','.join(map(str,child(pad,'layers')[1:])),name=str(pn[2]) if pn else '')
            if ref.startswith('H') and ref[1:].isdigit():
                holes.append(dict(ref=ref,local=[x,y],removed=removed.intersects(circle(x,y,2.5)),retained_with_3mm_border=new.covers(circle(x,y,3))))
            else:
                comp=next((c for c in definition['components'] if c['reference']==ref),None)
                sizes={'hall':(3.0,3.0),'capacitor':(1.8,1.0),'mux':(5.1,6.6),'connector':(22.,8.),'testpoint':(1.,1.)}
                if comp:
                    w,h=sizes[comp['kind']];ca,sa=math.cos(math.radians(ang)),math.sin(math.radians(ang))
                    body=affine_transform(box(-w/2,-h/2,w/2,h/2),[ca,-sa,sa,ca,x,y]);pads.append(body)
                g=unary_union(pads)
                if g.intersection(removed).area>1e-10:components.append(dict(ref=ref,kind=comp['kind'] if comp else 'unknown',local=[x,y],envelope_bbox=list(g.bounds),removed_area_mm2=g.intersection(removed).area))
    return data,components,holes

allresults=[];allinventory=[];svgs={}
source198=use(HERE/'inputs/issue198/generate.py')
plan=load(ROOT/'hardware/kicad/qualification/issue-196-main-rev4-phasea2/geometry-plan.json')
# Verify actual final Main connector poses and edge against #198 snapshots below.
mainpcb=sexpdata.loads(use(ROOT/'hardware/kicad/qualification/issue-196-main-rev4-phaseb/inspection/final/main.kicad_pcb').read_text())
mainparts={next(str(q[2]) for q in children(n,'property') if str(q[1])=='Reference'):n for n in children(mainpcb,'footprint')}
for ref,pose in [('J2',[-15.5,43]),('J3',[15.5,43])]:
    at=xy(child(mainparts[ref],'at'));assert math.dist([at[0]-100,at[1]-70],pose)<1e-6
for pitch in (16,17):
    assembly=load(HERE/f'inputs/issue198/dimensions-{pitch}mm.json')
    for sourcepath,digest in assembly['inputs_sha256'].items():
        assert hashlib.sha256(use(ROOT/sourcepath).read_bytes()).hexdigest()==digest
    main=Polygon(assembly['boards']['main']['outline']);udb=Polygon(assembly['boards']['udb']['outline'])
    assert all(abs(a-b)<1e-6 for a,b in zip(udb.bounds,[-9,-36.25,9,-19.75]))
    outlines={};variant={};caps_all=[];draw=[]
    for side,sign in [('left',1),('right',-1)]:
        name=f'{pitch}mm-{side}';d=load(W/f'wing-rev2-{name}/definition.json');use(W/f'wing-rev2-{name}/bom.csv');use(W/f'wing-rev2-{name}/cpl.csv')
        kr=rows(C/f'keys-{name}.csv');hr=rows(C/f'holes-{name}.csv');orr=rows(C/f'outline-{name}.csv')
        old=Polygon([(float(x['x_mm']),float(x['y_mm'])) for x in orr]);assert old.equals(Polygon(d['outline_mm']))
        tr=assembly['wing_transforms'][side];m,t=tr['matrix'],tr['translation']
        sw=[square(*[float(k[v]) for v in ['x_mm','y_mm','rotation_deg']],15.8) for k in kr]
        cap=[transform(square(*[float(k[v]) for v in ['x_mm','y_mm','rotation_deg']],17),m,t) for k in kr]
        caps_all+=cap
        xmin,ymin,xmax,ymax=old.bounds
        # Conservative stair: axis-aligned bounds of 2mm-expanded switch envelopes,
        # vertically swept to old north edge; no key/sensor coordinates changed.
        expanded=[g.buffer(2,join_style=2).bounds for g in sw]
        slabs=[box(max(xmin,a),b,min(xmax,c),ymax) for a,b,c,e in expanded]
        south=unary_union(slabs)
        # Extend extreme columns to original side edges (at most sub-mm).
        bounds=sorted(expanded,key=lambda b:b[0]);left=bounds[0];right=max(expanded,key=lambda b:b[2])
        south=unary_union([south,box(xmin,left[1],left[2],ymax),box(right[0],right[1],xmax,ymax)])
        assert south.geom_type=='Polygon' and not south.interiors
        tab=mirror(box(-42,-45,-12,-18),sign)
        # inverse affine because both Wing matrices are orthogonal.
        tablocal=Polygon([inv(q,m,t) for q in coords(tab)])
        new=unary_union([south,tablocal]);assert new.is_valid and new.geom_type=='Polygon' and not new.interiors
        outlines[side]=transform(new,m,t)
        removed=old.difference(new)
        refasm=[-26*sign,-41];reflocal=inv(refasm,m,t)
        body=mirror(box(-37,-42,-15,-35),sign) # conservative maximum incl pads
        access=mirror(box(-42,-52,-10,-25),sign)
        assert outlines[side].covers(body)
        assert min(access.distance(g) for g in cap)>0
        assert all(new.covers(g) for g in sw)
        for h in hr:
            if h['kind']=='locator':
                assert new.covers(circle(float(h['x_mm']),float(h['y_mm']),float(h['diameter_mm'])/2))
        assert sum(h['kind']=='locator' for h in hr)==42
        # A rigid top-side rotation only; never mirror the copper pin order.
        angle=30 if side=='left' else -30
        pincontract=next(c for c in d['components'] if c['reference']=='J_WING')['pins']
        board=sexpdata.loads(use(W/f'wing-rev2-{name}/main.kicad_pcb').read_text())
        # Check source native outline and every defined component pose, including sensors.
        nativeparts={next(str(q[2]) for q in children(n,'property') if str(q[1])=='Reference'):n for n in children(board,'footprint')}
        nativeedges=[]
        for edge in children(board,'gr_line'):
            if str(val(edge,'layer'))=='Edge.Cuts':
                for end in ['start','end']:
                    q=xy(child(edge,end));nativeedges.append([q[0]-100,100-q[1]])
        assert Polygon(nativeedges).convex_hull.symmetric_difference(old).area<1e-3
        for component in d['components']:
            pose=xy(child(nativeparts[component['reference']],'at'))
            assert math.dist([pose[0]-100,100-pose[1]],[component['x_mm'],component['y_mm']])<1e-6
        nativepins={str(p[1]):str(child(p,'net')[2]) if child(p,'net') else None for p in children(nativeparts['J_WING'],'pad')}
        assert nativepins==pincontract
        for k,original in zip(kr,d['keys']):
            assert k['key']==original['key'] and k['sensor']==original['sensor']
            assert abs(float(k['rotation_deg'])-original['rotation_ccw_deg'])<1e-8
            assert math.dist([float(k['x_mm']),float(k['y_mm'])],[original['x_mm'],original['y_mm']])<1e-8
        proposedpads=[]
        ca,sa=math.cos(math.radians(angle)),math.sin(math.radians(angle))
        for p in children(nativeparts['J_WING'],'pad'):
            q=xy(child(p,'at'));local=[reflocal[0]+ca*q[0]+sa*q[1],reflocal[1]+sa*q[0]-ca*q[1]]
            proposedpads.append(dict(number=str(p[1]),net=nativepins[str(p[1])],local=local,assembly=tx(local,m,t),size_mm=list(map(float,child(p,'size')[1:3]))))
        invdata,compdata,holes=native_inventory(board,removed,new,d)
        candidates=[]
        switchunion=unary_union(sw)
        # Candidate holes in retained material, with >=3mm edge / phi5+0.25 switch clearance.
        retainedparts=[c for c in d['components'] if c['reference']!='J_WING' and c['reference'] not in {x['ref'] for x in compdata}]
        obstacles=[]
        for c in retainedparts:
            wh={'hall':(3,3),'capacitor':(1.8,1),'mux':(5.1,6.6),'testpoint':(1,1)}[c['kind']]
            obstacles.append(box(c['x_mm']-wh[0]/2,c['y_mm']-wh[1]/2,c['x_mm']+wh[0]/2,c['y_mm']+wh[1]/2))
        for h in holes:
            if h['retained_with_3mm_border']:continue
            poss=[]
            for ix in range(math.ceil(xmin+3),math.floor(xmax-3)+1):
                for iy in range(math.ceil(ymin),math.floor(ymax-3)+1):
                    pt=Point(ix,iy)
                    if not new.covers(circle(ix,iy,3)) or switchunion.distance(pt)<2.75:continue
                    if any(g.distance(pt)<2.75 for g in obstacles):continue
                    if any(math.dist([ix,iy],x['local'])<6 for x in holes if x['retained_with_3mm_border']):continue
                    if any(math.dist([ix,iy],x['candidate_local'])<6 for x in candidates):continue
                    poss.append((math.dist(h['local'],[ix,iy]),ix,iy))
            assert poss
            _,x,y=min(poss);candidates.append(dict(ref=h['ref'],old_local=h['local'],candidate_local=[x,y],candidate_assembly=tx([x,y],m,t),edge_mm=new.boundary.distance(Point(x,y)),switch_keepout_gap_mm=switchunion.distance(Point(x,y))-2.5))
        newcenters=[h['local'] for h in holes if h['retained_with_3mm_border']]+[h['candidate_local'] for h in candidates]
        plane_domain=new.buffer(-.3).difference(unary_union([circle(*p,2.6) for p in newcenters]))
        # A .30mm-wide connection can survive the geometric bottlenecks in this substrate model.
        eroded_domain=plane_domain.buffer(-.15)
        assert plane_domain.geom_type=='Polygon'
        eroded_parts=list(getattr(eroded_domain,'geoms',[eroded_domain]))
        core=max(eroded_parts,key=lambda g:g.area)
        assert all(core.covers(Point(k['x_mm'],k['y_mm'])) for k in d['sensor_sites'])
        assert core.covers(Point(*reflocal))
        for item in invdata:allinventory.append(dict(variant=name,**item))
        counts=collections.Counter((z['kind'],z['net'],z['layer']) for z in invdata)
        southline=[]
        for a,b in zip(coords(south),coords(south)[1:]+coords(south)[:1]):
            if abs(a[1]-ymax)<1e-8 and abs(b[1]-ymax)<1e-8:continue
            if abs(a[0]-b[0])<1e-8 and (abs(a[0]-xmin)<1e-8 or abs(a[0]-xmax)<1e-8):continue
            southline.append([a,b])
        southdistance=min(LineString(edge).distance(g) for edge in southline for g in sw)
        assert southdistance>=2-1e-8
        growth=old.union(tablocal)
        result=dict(variant=name,pitch_mm=pitch,side=side,transform=tr,
          original_outline_local=coords(old),tab_local=coords(tablocal),tab_assembly=coords(tab),south_base_outline_local=coords(south),south_trim_line_local=southline,
          outline_local=coords(new),outline_assembly=coords(outlines[side]),removed_region_wkt=removed.wkt,
          size=dict(old_bbox=list(old.bounds),tab_only_bbox=list(growth.bounds),new_bbox=list(new.bounds),old_area_mm2=old.area,tab_added_area_mm2=growth.area-old.area,trim_removed_area_mm2=removed.area,south_added_area_mm2=south.difference(old).area,new_area_mm2=new.area),
          connector=dict(reference='J_WING',local=reflocal,assembly=refasm,local_ccw_deg=angle,assembly_long_axis_deg=0,pins=pincontract,pads=proposedpads,body_assembly=coords(body),finger_and_plug_access_assembly=coords(access),access_z_mm=[11.2,41.2],body_to_keycap_mm=min(body.distance(g) for g in cap),access_to_keycap_mm=min(access.distance(g) for g in cap)),
          south_margin_min_mm=southdistance,plane_substrate_model=dict(edge_setback_mm=.3,mount_reservation_radius_mm=2.6,connected=True,required_sites_connected_after_015mm_erosion=True,erosion_component_count=len(eroded_parts),erosion_other_islands_area_mm2=eroded_domain.area-core.area,area_mm2=plane_domain.area,excludes='mount keepouts only; pads/tracks and thermals require Stage2 routing verification'),inventory_components=compdata,mounting_holes=holes,mounting_candidates=candidates,
          inventory_counts=[dict(kind=k[0],net=k[1],layer=k[2],count=v) for k,v in sorted(counts.items())],native_entity_count=len(invdata),
          invariant=dict(key_count=len(kr),sensor_sites=d['sensor_sites'],keys=d['keys'],routing_rules=d['routing_rules'],connector_pin_contract=pincontract))
        variant[side]=result
        draw.append((outlines[side],cap,body,access,transform(removed,m,t)))
    for side,sign in [('left',1),('right',-1)]:
        result=variant[side];connector=result['connector'];other='right' if side=='left' else 'left'
        tab=Polygon(result['tab_assembly']);body=Polygon(connector['body_assembly']);access=Polygon(connector['finger_and_plug_access_assembly'])
        obstacles={'main':main,'udb':udb,'opposite_wing':outlines[other]}
        result['clearances']={name:dict(pcb_mm=outlines[side].distance(g),tab_mm=tab.distance(g),connector_mm=body.distance(g),access_mm=access.distance(g),pcb_overlap_mm2=outlines[side].intersection(g).area) for name,g in obstacles.items()}
        assert all(z['pcb_mm']>=2-1e-6 and z['pcb_overlap_mm2']<1e-8 for z in result['clearances'].values())
        way=[[-15.5*sign,43],[-13*sign,32],[-13*sign,-32],[-18*sign,-41],[-26*sign,-41]]
        smooth,arcs,length=roundroute(way)
        path=LineString(smooth);swept=path.buffer(1)
        assert all(not swept.intersects(g) for g in caps_all)
        polylen=sum(math.dist(a,b) for a,b in zip(way,way[1:]));chord=math.dist(way[0],way[-1]);required=polylen+30
        result['harness']=dict(main_ref='J2' if side=='left' else 'J3',waypoints_assembly=way,fillet_radius_mm=5,fillet_arcs=arcs,smooth_samples_assembly=smooth,chord_mm=chord,polyline_mm=polylen,smooth_length_mm=length,allowance_mm=30,required_mm=required,nominal_mm=200,nominal_minus_required_mm=200-required,keycap_intersections=sum(swept.intersects(g) for g in caps_all),centerline_keycap_min_mm=min(path.distance(g) for g in caps_all),cable_surface_keycap_min_mm=min(swept.distance(g) for g in caps_all),cable_surface_udb_min_mm=swept.distance(udb))
        allresults.append(result)
    # Same assembly frame; board outlines, old removed substrate, envelopes and smooth route.
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-160 -80 320 175" width="1600" height="875"><rect x="-160" y="-80" width="320" height="175" fill="white"/>',f'<text x="-155" y="-70" font-size="4">Issue 200 Stage 1 / {pitch}mm / X right, Y south / cyan: access; orange: cable</text>']
    def drawpoly(g,fill,stroke,opacity=1):
        polys=[g] if g.geom_type=='Polygon' else [x for x in getattr(g,'geoms',[]) if x.geom_type=='Polygon']
        for p in polys:svg.append('<polygon points="'+' '.join(f'{x:.4f},{y:.4f}' for x,y in p.exterior.coords)+f'" fill="{fill}" stroke="{stroke}" stroke-width=".25" opacity="{opacity}"/>')
    for g in [main,udb]:drawpoly(g,'#ddd','#333')
    for g,caps,body,access,removed in draw:
        drawpoly(g,'#b7dec9','#185');drawpoly(removed,'#faa','#a55',.5)
        for c in caps:drawpoly(c,'none','#637')
        drawpoly(access,'#aff','#188',.45);drawpoly(body,'#555','#111')
    for res in variant.values():
        svg.append('<polyline points="'+' '.join(f'{x:.4f},{y:.4f}' for x,y in res['harness']['smooth_samples_assembly'])+'" fill="none" stroke="#e80" stroke-width="2"/>')
        for h in res['mounting_candidates']:
            x,y=h['candidate_assembly'];svg.append(f'<circle cx="{x}" cy="{y}" r="2.5" fill="none" stroke="#11e" stroke-width=".4"/>')
    svg.append('</svg>');(HERE/f'review-{pitch}mm.svg').write_text('\n'.join(svg)+'\n')

save=dict(schema='issue200-stage1-v1',status='geometry_proposal_not_routed',units='mm',frame_local='Wing top view X right Y north; CCW degrees',frame_assembly='top view X right Y south, Z up; same as Issue198',issue198_commit='6a596e237d60e5054fb8bfdaf8d39b642b5574a0',assumptions=dict(switch_square=15.8,keycap_square=17,south_margin=2,cable_diameter=2,cable_min_bend_radius=5,allowance=30,gh_max_envelope_width=22,gh_max_envelope_depth=7,access_width=32,access_depth=27),variants=allresults,inputs_sha256=inputs)
(HERE/'geometry.json').write_text(json.dumps(save,indent=2,ensure_ascii=False)+'\n')
writecsv('trim-inventory.csv',[dict(**{k:v for k,v in x.items() if k!='geometry_bbox_local'},geometry_bbox_local=json.dumps(x['geometry_bbox_local'])) for x in allinventory],['variant','kind','index','uuid','net','layer','removed_area_mm2','geometry_bbox_local'])
import subprocess,sys
subprocess.run([sys.executable,str(HERE/'report.py')],check=True)
print('PASS: four variants; geometry.json, trim-inventory.csv, two SVGs and report generated')
