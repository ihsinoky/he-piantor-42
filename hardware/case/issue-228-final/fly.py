"""Phase C: official Fly solid, local north seat, connector and cable reservations.

Positive assembly Y is south. The official board receives a rigid Z180 rotation;
its geometry is never replaced or modified. Mating envelopes are named separately.
"""
from base import *
from build123d import Axis, Edge, sweep

MODEL=HERE/'inputs/TheFly_DaughterBoard_V4.2.stp'
REV6=ROOT/'hardware/kicad/qualification/issue-226-main-rev6/inspection/final/main.kicad_pcb'
MOUTH=4.378
BOTTOM=10.
CASE_TOP=15.2
FLY_TOP=15.2

def outline_polygon(s):
    f=max((f for f in s.faces() if abs(f.center().Z)<1e-6),key=lambda f:f.area)
    pts=[]
    for e in f.outer_wire().order_edges():
        n=max(1,math.ceil(e.length/.02))
        pts.extend([(v.X,v.Y) for v in e.positions([i/n for i in range(n)])])
    return Polygon(pts)

def prepare(outer,inputs,boards,pitch):
    inputs.extend([MODEL,REV6])
    official=import_step(MODEL)
    solids=official.solids();pcb=solids[0];b=pcb.bounding_box()
    assert all(abs(a-b)<1e-5 for a,b in zip(size(pcb),[23.572,8.30,1.59]))
    circles={(round(e.radius,5),round(e.arc_center.X,5),round(e.arc_center.Y,5)) for e in pcb.edges() if e.geom_type.name=='CIRCLE'}
    assert {(1.1,-9.5,0.),(1.1,9.5,0.),(2.286,-9.5,0.),(2.286,9.5,0.)}<=circles
    wall=outer.boundary.intersection(LineString([(0,-100),(0,-40)])).y
    cy=wall+MOUTH+.30
    moved=[]
    for i,q in enumerate(solids):
        t=q.rotate(Axis.Z,180).translate((0,cy,BOTTOM));t.label=f'Fly-official-{i:02d}';moved.append(t)
    solid=Compound(children=moved);solid.label='fly'
    # The real PCB outer boundary (scallops/lobes), used only for XY audit data.
    from shapely.affinity import rotate,translate
    polygon=translate(rotate(outline_polygon(pcb),180,origin=(0,0)),yoff=cy)
    # Follow the actual scallops/lobes at the front rather than cutting a thin
    # rectangular lip beside the flush USB mouth. 0.005 simplification error
    # stays inside the 0.5 mm nominal PCB clearance allowance.
    protected=unary_union([boards['wing_'+side].buffer(2.502,join_style=2) for side in ['left','right']])
    seat=polygon.buffer(.5,resolution=48).simplify(.005,preserve_topology=True).union(box(-12.30,cy-1.65,12.30,-18.)).difference(protected)
    if pitch==16:
        # The full Wing wall band crosses the Fly at this pitch. Relieve only
        # the PCB-height scalloped pocket; retain the protected deep cavity.
        relief=polygon.buffer(.5,resolution=48).simplify(.005,preserve_topology=True)
        wing_pockets=unary_union([boards['wing_'+side].buffer(.502,join_style=2) for side in ['left','right']])
        assert relief.disjoint(wing_pockets)
        seat=seat.union(relief)
    deep=box(-12.3,cy-1.65,12.3,-18).difference(protected)
    legs=box(-4.9,cy-4.1,4.9,cy-1.5).difference(protected)
    opening=box(-8.,wall-25,8.,cy+3.).difference(protected)
    tower_polygon=outer.intersection(box(-12.3,wall-1,12.3,wall+2.)).difference(protected)
    # Restore the complete MH1/MH2 support up to Z10 after the shallow relief.
    # At 16 mm the old wall band also crosses their top rims; only the real
    # Wing pockets constrain boss/pilot restoration. 17 mm stays unchanged.
    protected_solid=prism(wing_pockets if pitch==16 else protected,2,40)
    holes=[dict(board='fly',ref=f'MH{i}',xy=[x,cy],diameter=2.2,boss_diameter=4.5) for i,x in enumerate([-9.5,9.5],1)]
    return dict(solid=solid,polygon=polygon,holes=holes,center_y=cy,wall_y=wall,board_bottom=BOTTOM,tower_polygon=tower_polygon,protected=protected_solid,
                seat_cut=prism(seat,BOTTOM-.2,6.2).fuse(prism(deep,2,BOTTOM-2)).fuse(prism(legs,BOTTOM-.7,.7)),opening_cut=prism(opening,BOTTOM-.3,7),
                local_edit_xy=coords(seat.union(opening.intersection(outer))))

def main_header(ctx):
    # Rev.6 J4 pose/MPN checked from actual PCB. No Main pocket or mount changes.
    n=next(n for n in children(read_board(REV6),'footprint') if ref(n)=='J4')
    assert xy(child(n,'at'))==[100.,90.] and float(child(n,'at')[3])==180
    assert any(str(v[1])=='Value' and str(v[2])=='781710004' for v in children(n,'property'))
    source=import_step(MODEL).solids()[67]
    # Align source terminal row Y=1.05422375 with Rev.6 pad row Y=21.875.
    shape=source.rotate(Axis.Y,180).translate((0,20.82077624511719,11.2))
    b=shape.bounding_box();g=box(b.min.X,b.min.Y,b.max.X,b.max.Y)
    return shape,g,1.45,'official Fly 781710004 solid, rigidly aligned to unchanged Main Rev.6 J4 pad row'

def smooth_path(points,r=5.):
    points=[Vector(*p) for p in points];corners=[]
    for a,b,c in zip(points,points[1:],points[2:]):
        u=(a-b).normalized();v=(c-b).normalized();theta=math.acos(max(-1,min(1,u.dot(v))))
        trim=r/math.tan(theta/2);start=b+u*trim;end=b+v*trim
        center=b+(u+v).normalized()*(r/math.sin(theta/2))
        mid=center+((start-center).normalized()+(end-center).normalized()).normalized()*r
        corners.append((start,mid,end,trim))
    edges=[];prev=points[0]
    for i,(start,mid,end,trim) in enumerate(corners):
        assert (start-prev).dot((points[i+1]-points[i]).normalized())>0,(i,trim)
        edges.extend([Edge.make_line(prev,start),Edge.make_three_point_arc(start,mid,end)]);prev=end
    edges.append(Edge.make_line(prev,points[-1]));return Wire(edges)

def nominal_cable_points(cy):
    return [(0,cy+2.87,8.6),(0,cy+10,8.6),(-7,cy+17,8.6),(-7,cy+29,18.2),(-7,7,18.2),(0,14,12.6),(0,17.435,12.6)]

def connected_cable(cy):
    """Open, connected service detour: baseline route + all 170mm length budget.

    Replaces the central transit with an elevated loop, not a disconnected ring.
    All corners are the same analytic R5 arcs used by the nominal route.
    The north crossbar position absorbs the pitch-dependent length difference.
    """
    def points(north):
        return [(0,cy+2.87,8.6),(0,cy+10,8.6),(-7,cy+17,8.6),
                (-7,-29.5,25),(-7,-12,25),(7,-12,25),(7,north,25),
                (-7,north,25),(-7,-29,25),(7,-29,18.2),
                (7,7,18.2),(0,14,12.6),(0,17.435,12.6)]
    trial=smooth_path(points(-44))
    north=-44+(trial.length-170)/2  # Two parallel straight legs vary together.
    pts=points(north);path=smooth_path(pts)
    assert abs(path.length-170)<1e-9,path.length
    cable=sweep(Face(Wire.make_circle(1,Plane(origin=pts[0],z_dir=(0,1,0)))),path=path)
    assert cable.is_valid and len(cable.solids())==1
    assert abs(cable.volume-math.pi*path.length)<1e-5,(cable.volume,path.length)
    return cable,path,pts

def volume(a,b):
    v=a.intersect(b);return sum(q.volume for q in v) if v else 0.

def usb_plug(cy):
    # Real mating shell is 8.25 x 2.40; 8.9 x 3.2 is a receptacle envelope.
    # 0.20 shell wall, rounded R1.0 outer / R0.8 inner, 6.65 exposed length.
    outer=box(-3.125,3.32-.2,3.125,3.32+.2).buffer(1,resolution=32)
    inner=box(-3.125,3.32-.2,3.125,3.32+.2).buffer(.8,resolution=32)
    def along_y(g,y,length):
        def w(coords):return Wire.make_polygon([Vector(x,y,BOTTOM+z) for x,z in list(coords)[:-1]],close=True)
        return extrude(Face(w(g.exterior.coords),[w(r.coords) for r in g.interiors]),amount=length,dir=(0,1,0))
    mouth=cy-MOUTH;tip=mouth+6.2;rear=tip-6.65
    shell=along_y(outer.difference(inner),rear,6.65)
    overmold=prism(box(-6,rear-15,6,rear),BOTTOM+.32,6)
    exit=Solid.make_cylinder(2,25,Plane(origin=(0,rear-15,BOTTOM+3.32),z_dir=(0,-1,0)))
    shell.label='USB-reference-shell';overmold.label='USB-reference-overmold';exit.label='USB-reference-cable-exit'
    return dict(zip(['USB-reference-shell','USB-reference-overmold','USB-reference-cable-exit'],[shell,overmold,exit]))

def harness(ctx,body,parts,components,cables,hardware,storage,key_solids):
    f=ctx['fly'];cy=f['center_y'];out=ctx['out'];shapes=usb_plug(cy)
    # Molex 781720000-SD: 4-way A=5.0, body length3.5, height1.3;
    # 781710000-SD mated stack1.9. Conservative solid mating reservations.
    flyplug=prism(box(-2.5,cy-.63,2.5,cy+2.87),BOTTOM-1.9,1.3)
    mainplug=prism(box(-2.5,17.435,2.5,20.935),11.8,1.3)
    flyplug.label='EZmate-Fly-plug';mainplug.label='EZmate-Main-plug'
    shapes.update({'EZmate-Fly-plug':flyplug,'EZmate-Main-plug':mainplug})
    nominal=smooth_path(nominal_cable_points(cy))
    cable,path,pts=connected_cable(cy)
    cable.label='EZmate-170mm-route';shapes[cable.label]=cable
    assert cable.is_valid and abs(path.length-170)<1e-9
    obstacles={'case':body,**{'part-'+k:v for k,v in parts.items() if not k.startswith('tray')},**{'Main-'+k:v for k,v in components.items() if k!='J4'},**cables,**hardware}
    obstacles.update({'pcb-'+s.label:s for s in ctx['board_solids'] if s.label!='fly'})
    obstacles.update({'storage-'+k:v for k,v in storage.items()})
    obstacles.update({'keycap-'+str(i):v for i,v in enumerate(key_solids)})
    obstacles.update({q.label:q for q in f['solid'].children if q.label!='Fly-official-67'})
    gaps={k:cable.distance_to(v) for k,v in obstacles.items()}
    # Source header / receptacle are intended mates; real PCB is always an obstacle.
    pcb=f['solid'].children[0]
    gaps['pcb-fly']=cable.distance_to(pcb)
    print('Fly route minimum:',sorted(gaps.items(),key=lambda p:p[1])[:8],flush=True)
    assert min(gaps.values())>.2,sorted(gaps.items(),key=lambda p:p[1])[:8]
    for name in ['EZmate-Fly-plug','EZmate-Main-plug']:
        assert shapes[name].distance_to(body)>.2,(name,shapes[name].distance_to(body))
    mate=[dict(a='USB-reference-shell',b=q.label,volume_mm3=volume(shapes['USB-reference-shell'],q)) for q in f['solid'].children]
    mate=[v for v in mate if v['volume_mm3']>1e-4]
    data=dict(board_bottom_z_mm=BOTTOM,case_local_top_z_mm=FLY_TOP,board_size_mm=[23.572,8.3,1.59],transform=dict(rotation_z_deg=180,translation_mm=[0,cy,BOTTOM]),
      wall_outer_y_at_x0_mm=f['wall_y'],mouth_y_mm=cy-MOUTH,mouth_recess_mm=.3,mouth_source_y_mm=MOUTH,
      hole_spacing_mm=19,holes_diameter_mm=2.2,boss_diameter_mm=4.5,pilot_diameter_mm=1.7,screw='M2x6 thread-forming with 0.5 mm insulating washer',screw_engagement_mm=3.91,
      opening=dict(width_mm=16,z_min_mm=BOTTOM-.3,z_max_mm=BOTTOM+6.7,case_top_z_mm=FLY_TOP,open_above_case=True,center_x_mm=0),
      usb=dict(shell_outer_xz_mm=[8.25,2.4],shell_wall_mm=.2,exposed_shell_length_mm=6.65,engagement_mm=6.2,overmold_xyz_mm=[12,15,6],cable_diameter_mm=4,cable_exit_length_mm=25,connector_internal_overlaps=mate,qualification='Intended mating volumes reported separately; strict connector-internal zero-overlap is NOT demonstrated.'),
      ezmate=dict(part_number='781720004',housing_xyz_mm=[5,3.5,1.3],mated_stack_mm=1.9,source='https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/781/78172/781720002_sd.pdf'),
      cable=dict(nominal_mm=170,route_length_mm=nominal.length,service_allowance_mm=30,remaining_mm=170-nominal.length-30,connected_length_mm=path.length,stored_service_detour_mm=path.length-nominal.length,unmodeled_mm=0.,stored_loop_includes_service_allowance=True,placement='Central bay; elevated open service detour at Z25 (tube top Z26), rising north of rack and descending east; replaces nominal central transit.',diameter_mm=2,bend_radius_mm=5,waypoints_mm=pts,nominal_waypoints_mm=nominal_cable_points(cy),clearances_mm=gaps,minimum_mm=min(gaps.values()),threshold_mm=.2),local_edit_xy_mm=f['local_edit_xy'])
    return shapes,data
