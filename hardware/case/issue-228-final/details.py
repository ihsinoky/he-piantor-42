"""Detailing and measured acceptance checks; uses Stage1 coordinate extraction."""
from base import *
from build123d import Edge, sweep, import_step

def tube(v,z=23.2):
    h=v['harness'];w=h['waypoints_assembly'];arcs=h['fillet_arcs'];r=5.
    start=w[0];end=w[-1]
    def advance(a,b,d):
        l=math.dist(a,b);return [a[i]+(b[i]-a[i])*d/l for i in range(2)]
    a=advance(start,arcs[0]['start'],r);b=advance(end,arcs[-1]['end'],r)
    def V(q,zz=z):return Vector(q[0],q[1],zz)
    # Endpoint exits are vertical. Exact R5 quarter circles transition to the planar route.
    d=[(a[i]-start[i])/r for i in range(2)]
    q=[start[i]+d[i]*r*(1-math.cos(math.pi/4)) for i in range(2)]
    edges=[Edge.make_three_point_arc(V(start,z-r),V(q,z-r+r*math.sin(math.pi/4)),V(a))]
    prev=a
    for arc in arcs:
        edges.append(Edge.make_line(V(prev),V(arc['start'])))
        c=arc['center'];angle=math.atan2(arc['start'][1]-c[1],arc['start'][0]-c[0])+math.radians(arc['sweep_deg'])/2
        mid=[c[0]+r*math.cos(angle),c[1]+r*math.sin(angle)]
        edges.append(Edge.make_three_point_arc(V(arc['start']),V(mid),V(arc['end'])))
        prev=arc['end']
    edges.append(Edge.make_line(V(prev),V(b)))
    d=[(end[i]-b[i])/r for i in range(2)]
    q=[b[i]+d[i]*r*math.sin(math.pi/4) for i in range(2)]
    edges.append(Edge.make_three_point_arc(V(b),V(q,z-r+r*math.cos(math.pi/4)),V(end,z-r)))
    path=Wire(edges)
    shape=sweep(Face(Wire.make_circle(1,Plane(origin=V(start,z-r)))),path=path)
    assert shape.is_valid
    return shape,path

def finish(args,ctx):
    out=ctx['out'];body=ctx['body'];boards=ctx['boards'];holes=ctx['holes'];outer=ctx['outer'];variants=ctx['variants'];top=ctx['top']
    print('Detailing',flush=True)
    parts={};hardware={};joints=[];feet=[]
    # Underside plates + vertical locating pegs. Pads keep >=2.1 material over sockets.
    for j,y in enumerate([-8.,55.],1):
        g=box(-10.5,y-8,17.5,y+8)
        outer=outer.union(g) # local reinforcement extends the neck only below PCBs
        body=body.fuse(prism(g,0,3.5))
        plate=prism(g,-3,3)
        for x in [-5.,12.]:
            body=body.fuse(cylinder(x,y,3.5,0,8))
            body=body.cut(cylinder(x,y,.85,0,6))
            plate=plate.cut(cylinder(x,y,1.2,-3,3))
            screw=cylinder(x,y,.8,-3,8).fuse(cylinder(x,y,2,-4.6,1.6))
            hardware[f'joint-screw-{j}-{x}']=screw
        for x in [-1.,8.]:
            plate=plate.fuse(cylinder(x,y+4,1.5,0,1.2))
            body=body.cut(cylinder(x,y+4,1.65,0,1.4))
        parts[f'splice-{j}']=plate
        joints.append(dict(center=[3.5,y],plate=[28,16,3],screws_xy=[[-5,y],[12,y]],pilot_diameter=1.7,pilot_depth=6,peg_xy=[[-1,y+4],[8,y+4]],peg_diameter=3,socket_diameter=3.3,peg_height=1.2,socket_depth=1.4))
    # Feet are purchased adhesive rubber, with a recessed registration circle.
    for h in holes:
        if not h['board'].startswith('wing'):continue
        x,y=h['xy']
        if abs(x)<10:x=math.copysign(24,x) # clear the north splice plate
        assert outer.covers(Point(x,y).buffer(5))
        body=body.fuse(cylinder(x,y,5,0,2.4)) # >=2mm remains over the 0.4mm recess
        foot=cylinder(x,y,4,-6,6.4)
        body=body.cut(cylinder(x,y,4.2,0,.4))
        hardware['rubber-'+h['board']+'-'+h['ref']]=foot
        feet.append(dict(xy=[x,y],diameter=8,height=6,seat_depth=.4))
    print('Feet done',flush=True)
    # All PCB screws: M2x6 plastic thread-forming, with 0.5 insulating washers.
    # Fly uses the same M2x6 / 0.5 mm insulating washer scheme at two NPTH sites.
    for h in holes:
        x,y=h['xy'];thick=1.59 if h['board']=='fly' else P['pcb_thickness']
        z=(ctx['fly']['board_bottom'] if h['board']=='fly' else P['pcb_bottom'])+thick
        washer=cylinder(x,y,2.25,z,.5).cut(cylinder(x,y,1.1,z,.5))
        screw=cylinder(x,y,.8,z+.5-6,6).fuse(cylinder(x,y,1.7,z+.5,1.6))
        hardware['washer-'+h['board']+'-'+h['ref']]=washer
        hardware['screw-'+h['board']+'-'+h['ref']]=screw
        h.update(screw='M2x6 nylon thread-forming' if h['board']=='fly' else 'M2x6 polymer-compatible thread-forming',washer_thickness=.5,engagement_mm=6-thick-.5,seat_z_mm=z)
    parts['tray-left']=Compound(children=list(body.intersect(prism(box(-300,-200,3.5,200),-1,40))))
    parts['tray-right']=Compound(children=list(body.intersect(prism(box(3.5,-200,300,200),-1,40))))
    # Main placement is checked against every final-board footprint by base.generate.
    components={};component_data=[]
    bomfile=PB/'main-bom.csv';ctx['inputs'].append(bomfile)
    bom={r['ref']:r for r in rows(bomfile)}
    rev6bom=ROOT/'hardware/kicad/qualification/issue-226-main-rev6/main-bom.csv'
    ctx['inputs'].append(rev6bom)
    bom['J4']=next(r for r in rows(rev6bom) if r['ref']=='J4')
    for c in ctx['plan']['main']['placements']:
        ref=c['ref']
        if ref.startswith('H'):continue
        h=7. if ref in ('J2','J3') else 3. if ref=='J4' else 5.
        basis='Stage1 mated GH reservation' if ref in ('J2','J3') else 'conservative design reservation, not manufacturer maximum'
        g=Polygon(c['envelope_xy_mm'])
        if ref=='L1':
            # Coilcraft XFL4020 drawing: 4.3x4.3x2.1 max; adds solder allowance.
            x,y=c['at_mm'];g=g.union(box(x-2.15,y-2.15,x+2.15,y+2.15));h=2.3
            basis='Coilcraft XFL4020 2.1 max +0.2 solder; 4.3 square body'
        if ref=='U6':h=1.2;basis='TI RNM0015A 1.0 max +0.2 solder'
        if ref=='J4':
            from fly import main_header
            components[ref],g,h,basis=main_header(ctx)
        else:components[ref]=prism(g,top,h)
        component_data.append(dict(ref=ref,part_number=bom.get(ref,{}).get('part_number'),height_mm=h,basis=basis,xy=coords(g)))
    print('Components done',flush=True)
    routes=[];cables={}
    wing_components={side:prism(Polygon(v['connector']['body_assembly']),top,7) for side,v in variants.items()}
    for side,shape in wing_components.items():shape.label='Wing-GH-envelope-'+side
    for side,v in variants.items():
        print('Route',side,flush=True)
        cable,path=tube(v);cables['GH-'+side]=cable
        distances=[dict(ref=n,gap_mm=cable.distance_to(s)) for n,s in components.items() if n!=v['harness']['main_ref']]
        assert min(d['gap_mm'] for d in distances)>.2
        # Mating region at the intended connector is excluded, every other component checked.
        key_solids=[prism(k,top,P['keycap_height']) for values in ctx['keycaps'].values() for k in values]
        keygap=min(cable.distance_to(k) for k in key_solids)
        assert keygap>.2
        wallgap=cable.distance_to(body);assert wallgap>.2
        boardgap=min(cable.distance_to(s) for s in ctx['board_solids']);assert boardgap>.2
        routes.append(dict(side=side,source_planar_mm=v['harness']['smooth_length_mm'],source_required_mm=v['harness']['required_mm'],actual_3d_mm=path.length,with_30mm_allowance_mm=path.length+30,nominal_200_slack_mm=200-path.length,endpoint_z_mm=18.2,cruise_z_mm=23.2,radius_mm=5,main_component_distances=distances,keycap_min_mm=keygap,case_min_mm=wallgap,pcb_min_mm=boardgap))
    print('Routes done',flush=True)
    # Final 200mm harness: racetrack storage capacity after 30mm approach/service allowance.
    # This separate envelope is not a connected 200mm centerline.
    slack_models={};slack_data=[]
    for route in routes:
        sign=-1 if route['side']=='left' else 1
        extra=route['nominal_200_slack_mm']-30;r=5.;straight=(extra-2*math.pi*r)/2
        x=sign*18.;y0=-44.;y1=y0+straight
        ring=LineString([(x,y0),(x,y1)]).buffer(r,resolution=48).boundary
        # Capsule tube at elevated routing height; inside open Main cavity / between keys.
        polygon=ring.buffer(1,resolution=16)
        slack=prism(polygon,22.2,2)
        slack_models['slack-'+route['side']]=slack
        # Storage clearance checked, no implication of prequalified wire bending.
        # Exact Cartesian-product distance for vertical prisms, avoids OCP work
        # on hundreds of tiny capsule edges. The cable route itself uses OCP distances.
        gaps={c['ref']:math.hypot(polygon.distance(Polygon(c['xy'])),max(0.,22.2-(top+c['height_mm']),top-24.2)) for c in component_data}
        assert min(gaps.values())>.2
        keygap=min(polygon.distance(k) for vs in ctx['keycaps'].values() for k in vs) # Z intervals overlap
        assert keygap>.2,(route['side'],keygap)
        slots=[]
        slack_data.append(dict(side=route['side'],length_mm=extra,approach_and_service_allowance_mm=30,radius_mm=r,straight_mm=straight,center_xy=[x,y0],z_mm=[22.2,24.2],tie_slots=slots,keycap_min_mm=keygap,main_min_mm=min(gaps.values()),note='200mm harness is the final spec (PO 2026-11-07, D-034): service-loop length budget; tie at Z22.2 on removable central rack. Closed capsule is storage envelope, not a second cable or connected 200mm centerline; separate from nominal route STEP.'))
    # A detachable rack stands in the PCB-free central neck, holding loops with ties.
    # Print inverted on its crossbar: the single column then grows vertically.
    rack=prism(box(-32,-16.5,32,-11.5),20.2,2.)
    rack=rack.fuse(prism(box(-25,-26.5,25,-21.5),20.2,2.))
    rack=rack.fuse(prism(box(-2,-26.5,2,-11.5),20.2,2.))
    rack=rack.fuse(cylinder(1,-14,2,2,18.2))
    body=body.cut(cylinder(1,-14,2.2,2,1.5))
    for x in [-30,-16,16,30]:
        rack=rack.cut(prism(box(x-.7,-15.5,x+.7,-12.5),20.19,2.02))
    for xx in [-24,-12,12,24]:
        rack=rack.cut(prism(box(xx-.6,-25.5,xx+.6,-22.5),20.19,2.02))
    parts['cable-rack']=rack
    # Recut tray after all floor details.
    for side,clip in [('left',box(-300,-200,3.5,200)),('right',box(3.5,-200,300,200))]:
        parts['tray-'+side]=Compound(children=list(body.intersect(prism(clip,-1,50))))
    print('Storage done',flush=True)
    # Main 3 + Fly 2 + Wing 4 per side = 13 PCB fixing points.
    assert len(holes)==13,len(holes)
    for side,v in variants.items():
        assert math.dist(v['connector']['assembly'],[-27 if side=='left' else 27,-41])<1e-9
        assert math.dist(v['harness']['waypoints_assembly'][-1],v['connector']['assembly'])<1e-9
    bosses=[]
    for h in holes:
        x,y=h['xy'];r=h['boss_diameter']/2;pr=P['screw_pilot_diameter']/2
        owner=[s for k in ('tray-left','tray-right') for s in parts[k].solids() if s.is_inside(Vector(x+(r+pr)/2,y,6))]
        pilot_open=not any(s.is_inside(Vector(x,y,6)) for k in ('tray-left','tray-right') for s in parts[k].solids())
        top_z=max(s.bounding_box().max.Z for s in owner) if owner else None
        assert len(owner)==1 and pilot_open,(h['board'],h['ref'])
        bosses.append(dict(board=h['board'],ref=h['ref'],xy=[x,y],boss_diameter=h['boss_diameter'],pilot_diameter=P['screw_pilot_diameter'],boss_top_z_mm=ctx['fly']['board_bottom'] if h['board']=='fly' else P['pcb_bottom'],material_at_boss_wall=True,pilot_open=pilot_open))
    from fly import harness
    fly_parts,fly_data=harness(ctx,body,parts,components,cables,hardware,slack_models,key_solids)
    printing=[]
    for name,s in parts.items():
        assert s.is_valid and len(s.solids())==1,(name,len(s.solids()))
        s.label=name
        export_step(s,out/f'{name}.step');export_stl(s,out/f'{name}.stl',tolerance=.005,angular_tolerance=.025)
        dims=size(s);brim=[dims[0]+10,dims[1]+10]
        assert max(brim)<=220
        printing.append(dict(name=name,size_mm=dims,with_5mm_brim_xy_mm=brim,orientation=('invert: crossbar Z22.2 on bed' if name=='cable-rack' else 'floor on bed; splice plate Z-3 on bed'),volume_mm3=s.volume))
    for name,s in hardware.items():s.label=name
    for name,s in cables.items():s.label=name
    for name,s in components.items():s.label='Main-envelope-'+name
    assembly=Compound(children=list(parts.values())+ctx['board_solids']+list(hardware.values())+list(cables.values())+list(components.values())+list(wing_components.values())+list(fly_parts.values()))
    export_step(assembly,out/'assembly.step')
    export_step(Compound(children=list(fly_parts.values())),out/'fly-harness-and-usb.step')
    export_step(Compound(children=list(cables.values())),out/'harness.step')
    export_step(Compound(children=list(slack_models.values())),out/'storage-200mm.step')
    clearances=[dict(a=a,b=b,gap_mm=g.distance(h),overlap_mm2=g.intersection(h).area) for (a,g),(b,h) in itertools.combinations(boards.items(),2)]
    assert all(x['overlap_mm2']<1e-8 for x in clearances)
    for h in holes:assert boards[h['board']].covers(Point(*h['xy']).buffer(h['diameter']/2))
    data=dict(fly=fly_data,schema='issue198-final-v1',pitch_mm=args.pitch,source='Wing Rev3 final CSV (Issue #200, PR #201, D-034); harness 200mm final (PO 2026-11-07)',parameters={**P,'palm_offset_mm':args.palm_offset},wing_transforms=ctx['transforms'],boards={k:coords(v) for k,v in boards.items()},mounts=holes,boss_check=bosses,fixed_point_count=len(holes),joints=joints,feet=feet,main_components=component_data,routes=routes,storage_200mm=slack_data,pcb_clearances=clearances,printing=printing,palm_high_wall_overlap_mm2=ctx['upper'].intersection(unary_union(ctx['palms'])).area,keycap_wall_min_mm=ctx['upper'].distance(ctx['key_union']),inputs_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(ctx['inputs']))},assembly_solid_count=sum(len(s.solids()) for s in list(parts.values())+ctx['board_solids']+list(hardware.values())+list(cables.values())+list(components.values())+list(wing_components.values())+list(fly_parts.values())),surface_approximation_mm=.002,fasteners=dict(pcb_screws=len(holes),pcb_insulating_washers=len(holes),splice_screws=4,splice_screw_spec='M2x8 thread-forming, core diameter1.6 in CAD; thread crest2.0 nominal',rubber_feet=len(feet)),height_sources=dict(L1='https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xfl/xfl4020/',U6='https://www.ti.com/lit/ds/symlink/tps63070.pdf'))
    save(out/'dimensions.json',data)
    # Top view with route, joint and rubber-foot locations, no external rendering dependency.
    x0,y0,x1,y1=outer.bounds
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0-5} {y0-8} {x1-x0+10} {y1-y0+16}" width="1400" height="750">']
    def draw(g,fill,stroke):
        for poly in polygons(g):svg.append('<polygon points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in poly.exterior.coords)+f'" fill="{fill}" stroke="{stroke}" stroke-width=".3"/>')
    draw(outer,'#ddd','#444');draw(ctx['upper'],'#a88','#744')
    for g in boards.values():draw(g,'#acd','#357')
    for vs in ctx['keycaps'].values():
        for g in vs:draw(g,'none','#777')
    for v in variants.values():svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in v['harness']['smooth_samples_assembly'])+'" fill="none" stroke="#e60" stroke-width="2"/>')
    for sd in slack_data:
        x,y=sd['center_xy'];draw(LineString([(x,y),(x,y+sd['straight_mm'])]).buffer(5),'none','#a2a')
    for f in feet:draw(Point(*f['xy']).buffer(4),'none','#222')
    svg.append(f'<path d="M3.5,{y0} V{y1}" stroke="blue" stroke-dasharray="2 2"/>')
    svg.append('</svg>');(out/'review.svg').write_text('\n'.join(svg))
    save(out/'exports-sha256.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.suffix in ('.step','.stl','.svg','.json') and p.name not in ('exports-sha256.json','verification.json')})
    print(json.dumps(dict(routes=routes,printing=printing),indent=2))
