"""2D-only PO gate; never imports the CAD generator or produces 3D geometry."""
from pathlib import Path
import csv
import hashlib
import json
import math
import os
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / '.issue228-runtime'
os.environ.setdefault('MPLCONFIGDIR', str(RUNTIME / 'mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely import set_precision
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union, nearest_points
from outline import proposed_outline, round1_outline, curve_design, bezier, usb_access
from round3_outline import proposed_outline as round3_outline, curve_design as round3_design
from round2_outline import proposed_outline as round2_outline, curve_design as round2_design


def vertices(g):
    # Remove exact collinear splits from Boolean operations, not shape corners.
    return len(g.simplify(1e-8, preserve_topology=True).exterior.coords)-1


def distance_record(a, b):
    p, q = nearest_points(a, b)
    return dict(mm=a.distance(b), first_xy=list(p.coords[0]), second_xy=list(q.coords[0]))


def main():
    source = ROOT / 'hardware/case/issue-198-final/17mm/dimensions.json'
    data = json.loads(source.read_text())
    boards = {k: Polygon(v) for k, v in data['boards'].items()}
    # Independently rebuild unchanged Wing boundaries from the authoritative CSVs.
    for side in ('left', 'right'):
        t = data['wing_transforms'][side]
        path = source.parent.parent / f'inputs/rev3-final/outline-17mm-{side}.csv'
        with path.open() as f:
            points = [[float(r['x_mm']), float(r['y_mm'])] for r in csv.DictReader(f)]
        transformed = Polygon([[sum(t['matrix'][i][j]*p[j] for j in range(2)) + t['translation'][i] for i in range(2)] for p in points])
        assert transformed.equals_exact(boards['wing_'+side], 1e-9)
    # Same extraction arithmetic and tolerance as base.generate, no pocket edits.
    cavity = unary_union([g.buffer(.502, join_style=2) for g in boards.values()] + [box(-11,-24,11,12)]).simplify(.002, preserve_topology=True)

    old = cavity.buffer(2., join_style=2)
    new = proposed_outline(cavity, boards)
    r1 = round1_outline(cavity, boards)
    r2 = round2_outline(cavity, boards)
    r3 = round3_outline(cavity, boards)
    r3_final = unary_union([r3,*[box(-10.5,y-8,17.5,y+8) for y in (-8.,55.)]])
    r2_final = unary_union([r2,*[box(-10.5,y-8,17.5,y+8) for y in (-8.,55.)]])
    assert curve_design(boards)["north_controls_xy_mm"] == round2_design(boards)["north_controls_xy_mm"]
    assert curve_design(boards)["north_controls_xy_mm"] == round3_design(boards)["north_controls_xy_mm"]
    design = curve_design(boards)
    plates = [box(-10.5,y-8,17.5,y+8) for y in (-8.,55.)]
    old_final, r1_final, new_final = [unary_union([g,*plates]) for g in (old,r1,new)]
    assert new_final.covers(cavity)
    assert new_final.difference(old_final).area<=3500.
    # North boundary and USB geometry are identical to rounds 2 and 3.
    north_clip=box(-300,-200,300,-45)
    north=new.boundary.intersection(north_clip)
    north_equality={}
    for name,prior in [('round2',r2),('round3',r3)]:
        previous=prior.boundary.intersection(north_clip)
        # GEOS clipping of coincident analytic supports differs by ~1e-14 mm.
        # Assert set equality on a 1e-10 mm grid, plus raw Hausdorff bound.
        assert set_precision(north,1e-10).equals(set_precision(previous,1e-10))
        deviation=north.hausdorff_distance(previous)
        assert deviation<1e-12
        north_equality[name]=dict(equal_on_grid_mm=1e-10,raw_hausdorff_mm=deviation)
    wall = distance_record(cavity.boundary,new.boundary)
    assert wall['mm'] >= 2.-1e-8
    # Seat/connector datum: same J1/J2 positions and transformation as base.py.
    import re
    pcb_source = ROOT/'hardware/kicad/qualification/issue-196-main-rev4-phasea2/inputs/udb/c3.kicad_pcb'
    text = pcb_source.read_text()
    def position(ref):
        for block in text.split('(module ')[1:]:
            if re.search(r'\(fp_text reference '+ref+r'\s',block):
                m=re.search(r'\(at ([0-9.-]+) ([0-9.-]+)',block)
                return tuple(map(float,m.groups()))
        raise ValueError(ref)
    j1,j2=position('J1'),position('J2')
    usb_front=[j1[0]-j2[0],j1[1]-6.8-j2[1]-20]
    slot=usb_access(new,usb_front[0])
    assert slot.equals(usb_access(r2,usb_front[0]))
    assert slot.equals(usb_access(r3,usb_front[0]))
    crossing=new.boundary.intersection(slot)
    assert not crossing.is_empty
    # The north passage goes all the way from outside to the unchanged seat.
    assert slot.bounds[1]<new.bounds[1] and slot.bounds[3]>usb_front[1]
    def angles(points,closed=False):
        out=[]
        indices=range(len(points)) if closed else range(1,len(points)-1)
        for i in indices:
            a,b,c=points[i-1],points[i],points[(i+1)%len(points)]
            u=[a[k]-b[k] for k in (0,1)];v=[c[k]-b[k] for k in (0,1)]
            cosine=sum(u[k]*v[k] for k in (0,1))/math.hypot(*u)/math.hypot(*v)
            out.append(dict(degrees=math.degrees(math.acos(max(-1.,min(1.,cosine)))),xy=list(b)))
        return out
    south=design['south_left']
    front=[design['left_north_xy_mm'],*south['path_xy_mm'],design['left_bridge_xy_mm']]
    front_angles=angles(front)
    assert min(a['degrees'] for a in front_angles)>=120
    bridge=design['left_bridge_xy_mm']
    bridge_angle=angles([front[-2],bridge,(-bridge[0],bridge[1])])[0]
    assert bridge_angle['degrees']>=120.-1e-8
    spans=south['spans_controls_xy_mm']
    assert len(spans)==1 and len(spans[0])==3
    # Exact quadratic/fillet tangency and positive travel direction.
    for span,fillet,index in [(spans[0],south['fillets'][0],0),(spans[-1],south['fillets'][1],-1)]:
        u=[span[1][k]-span[0][k] if index==0 else span[-1][k]-span[-2][k] for k in (0,1)]
        radius=[span[index][k]-fillet['center_xy_mm'][k] for k in (0,1)]
        assert abs(sum(u[k]*radius[k] for k in (0,1)))<1e-8
        assert u[0]*radius[1]-u[1]*radius[0]>0
    for fillet,anchor,end in [(south['fillets'][0],design['left_north_xy_mm'],'start'),
                             (south['fillets'][1],bridge,'end')]:
        point=fillet[end+'_xy_mm']
        direction=[point[k]-anchor[k] for k in (0,1)]
        radius=[point[k]-fillet['center_xy_mm'][k] for k in (0,1)]
        assert abs(sum(direction[k]*radius[k] for k in (0,1)))<1e-8
    # Shelf definition: nearest Euclidean distance FROM the south curve TO
    # the bare PCB south chain (never distance to pocket or #198 outline).
    # A dense arclength profile has a rigorous distance upper bound because
    # distance-to-set is 1-Lipschitz; half the sample spacing bounds the gap.
    curve=LineString(south['path_xy_mm'])
    pcb_south=LineString(list(boards['wing_left'].exterior.coords)[:14])
    count=20000
    profile=[]
    for i in range(count+1):
        q=curve.interpolate(curve.length*i/count)
        rec=distance_record(q,pcb_south)
        rec['arclength_mm']=curve.length*i/count
        profile.append(rec)
    maximum=max(profile,key=lambda r:r['mm'])
    shelf=dict(definition='nearest Euclidean distance from south perimeter to bare PCB south chain',
        maximum_sample=maximum,maximum_upper_bound_mm=maximum['mm']+curve.length/(2*count),
        sample_count=count+1,sample_spacing_mm=curve.length/count,profile=profile[::100],
        profile_stride=100,profile_includes_endpoints=True)
    # Retain the full dense profile as a reviewable, compact numeric artifact.
    with (HERE/'17mm-shelf-profile.csv').open('w',newline='') as f:
        writer=csv.writer(f,lineterminator="\n");writer.writerow(['arclength_mm','shelf_mm','curve_x_mm','curve_y_mm','pcb_x_mm','pcb_y_mm'])
        writer.writerows([r['arclength_mm'],r['mm'],*r['first_xy'],*r['second_xy']] for r in profile)
    shelf['full_profile_file']='17mm-shelf-profile.csv'
    shelf['above_limits']={}
    for limit in (10.,13.):
        runs=[];active=[]
        for r in profile:
            if r['mm']>limit:active.append(r)
            elif active:runs.append(active);active=[]
        if active:runs.append(active)
        shelf['above_limits'][str(limit)]=[dict(start=r[0],end=r[-1],maximum=max(r,key=lambda x:x['mm'])) for r in runs]
    # Stations: midpoint in chord projection of neighboring protruding tips.
    # This defines valley centers independently of curve parameterization.
    tips=south['stepped_tip_xy_mm']
    axis=[tips[-1][k]-tips[0][k] for k in (0,1)]
    length=math.hypot(*axis);axis=[v/length for v in axis]
    def station(p):
        normal=(-axis[1],axis[0])
        ray=LineString([tuple(p[k]+sign*400*normal[k] for k in (0,1)) for sign in (-1,1)])
        q=curve.intersection(ray)
        if q.is_empty:q=nearest_points(curve, Point(p))[0]
        if q.geom_type=='MultiPoint':q=max(q.geoms,key=lambda p:p.y)
        return distance_record(q,pcb_south)
    shelf['valley_centers']=[dict(between_tips=[i,i+1],**station(tuple((tips[i][k]+tips[i+1][k])/2 for k in (0,1)))) for i in range(len(tips)-1)]
    shelf['tips']=[dict(tip_index=i,stepped_outline_to_curve=distance_record(Point(p),curve),**station(p)) for i,p in enumerate(tips)]
    # T3 explicitly permits conflict reporting; never claim a numerical pass.
    shelf['target_mm']=10.
    shelf['deep_notch_allowance_mm']=13.
    shelf['target_met']=shelf['maximum_upper_bound_mm']<=10.
    shelf['allowance_met']=shelf['maximum_upper_bound_mm']<=13.
    # A supporting chord of the unchanged pocket convex hull, offset by the
    # required 2 mm wall, is a necessary lower envelope for any convex south
    # boundary. Along its outward normal all pocket/PCB points are north, so
    # nearest PCB distance cannot decrease farther south along that ray.
    hull=list(cavity.convex_hull.exterior.coords)
    a,b=next((a,b) for a,b in zip(hull,hull[1:])
             if max(a[0],b[0])<-50 and math.dist(a,b)>50 and max(a[1],b[1])>50)
    tangent=[(b[k]-a[k])/math.dist(a,b) for k in (0,1)]
    normal=(-tangent[1],tangent[0])
    if normal[1]<0:normal=tuple(-v for v in normal)
    chord=LineString([tuple(p[k]+2*normal[k] for k in (0,1)) for p in (a,b)])
    lower_point=max((chord.interpolate(chord.length*i/20000) for i in range(20001)),key=lambda q:q.distance(pcb_south))
    support=sum(normal[k]*a[k] for k in (0,1))
    assert max(sum(normal[k]*p[k] for k in (0,1))-support for p in cavity.exterior.coords)<1e-10
    for endpoint in chord.coords:
        assert abs(Point(endpoint).distance(cavity)-2.)<1e-10
    assert new.covers(chord)
    outward_ray=LineString([lower_point.coords[0],tuple(lower_point.coords[0][k]+200*normal[k] for k in (0,1))])
    assert not outward_ray.intersection(curve).is_empty
    lower_bound=dict(pocket_hull_edge_xy_mm=[a,b],required_wall_mm=2.,
        outward_normal_xy=normal,required_convex_chord_xy_mm=list(chord.coords),
        shelf_lower_bound=distance_record(lower_point,pcb_south),
        excess_over_13_mm=lower_point.distance(pcb_south)-13.)
    assert lower_bound['excess_over_13_mm']>0
    # Curvature of every sampled interior triple, plus the exact quadratic
    # minimum radius. Quadratic B' x B'' is constant and strictly negative.
    sweep=bezier(spans[0])
    def cross(u,v):return u[0]*v[1]-u[1]*v[0]
    turns=[];radii=[]
    for a,b,c in zip(sweep,sweep[1:],sweep[2:]):
        u=[b[k]-a[k] for k in (0,1)];v=[c[k]-b[k] for k in (0,1)]
        turn=cross(u,v);assert turn<0
        turns.append(-1 if turn<0 else 1)
        radii.append(math.dist(a,b)*math.dist(b,c)*math.dist(a,c)/(2*abs(turn)))
    controls=spans[0]
    velocity=[2*(controls[1][k]-controls[0][k]) for k in (0,1)]
    acceleration=[2*(controls[2][k]-2*controls[1][k]+controls[0][k]) for k in (0,1)]
    t=max(0.,min(1.,-sum(velocity[k]*acceleration[k] for k in (0,1))/sum(v*v for v in acceleration)))
    speed=math.hypot(*(velocity[k]+t*acceleration[k] for k in (0,1)))
    curvature=dict(family=south['family'],left_signed_turn=-1,right_signed_turn=1,
        sampled_sign_change_count=sum(a!=b for a,b in zip(turns,turns[1:])),
        right_sampled_sign_change_count=0,
        right_basis='exact reflection of left sampled path',
        sampled_interior_triples=len(turns),sampled_minimum_radius_mm=min(radii),
        analytic_minimum_radius_mm=speed**3/abs(cross(velocity,acceleration)),
        analytic_minimum_radius_parameter=t,
        analytic_cross_derivative=cross(velocity,acceleration),
        entire_path_including_fillets_minimum_radius_mm=5.)
    assert curvature['sampled_sign_change_count']==0
    # Fillets and joins turn in the same direction as the sweep.
    assert all(f['sweep_radians']<0 for f in south['fillets'])
    for a,b,c in zip(south['path_xy_mm'],south['path_xy_mm'][1:],south['path_xy_mm'][2:]):
        assert cross([b[k]-a[k] for k in (0,1)],[c[k]-b[k] for k in (0,1)])<0

    junctions=[dict(name='pinky side / fillet',xy=south['fillets'][0]['start_xy_mm'],interior_angle_degrees=180.,fillet_radius_mm=5.),
        dict(name='pinky fillet / sweep',xy=spans[0][0],interior_angle_degrees=180.,fillet_radius_mm=5.)]
    junctions.extend([dict(name='sweep / thumb fillet',xy=spans[-1][-1],interior_angle_degrees=180.,fillet_radius_mm=5.),
        dict(name='thumb fillet / inner side',xy=south['fillets'][1]['end_xy_mm'],interior_angle_degrees=180.,fillet_radius_mm=5.),
        dict(name='inner side / south bridge',xy=bridge,interior_angle_degrees=bridge_angle['degrees'])])
    sweep_points=bezier(spans[0])
    sweep_min=min(angles(sweep_points),key=lambda r:r['degrees'])
    removed=old_final.difference(new_final)
    def parts(g):
        if g.is_empty:return []
        return [g] if g.geom_type=='Polygon' else list(g.geoms)
    removed_records=[]
    for g in parts(removed):
        if g.area<1e-10:continue
        # Strip only zero-area floating-point tails along shared supports.
        raw_polygon=list(g.exterior.coords)
        raw_area=g.area
        cleaned=g.buffer(-1e-7).buffer(1e-7).simplify(1e-8,preserve_topology=False)
        assert abs(cleaned.area-g.area)<1e-7
        g=cleaned
        witness=g.representative_point()
        assert g.contains(witness), (g.wkt, g.area)
        assert cavity.distance(g)>0
        local_wall=distance_record(cavity.boundary,new.boundary.intersection(g.buffer(.01)))
        assert local_wall['mm']>=2.-1e-8
        removed_records.append(dict(area_mm2=raw_area,exact_polygon_xy=raw_polygon,
            numerical_tail_cleanup_mm=1e-7,bounds_xy_mm=list(g.bounds),
            interior_witness_xy=list(witness.coords[0]),polygon_xy=list(g.exterior.coords),
            adjacent_wall=local_wall))
    measures=dict(gate_status='2D candidate; T3 shelf conflict requires PMO/PO resolution',round=4,pitch_mm=17,coordinates='assembly XY mm; +Y south',
        source_dimensions_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        pocket_outside_proposal_mm2=cavity.difference(new).area,
        wall_minimum=wall,curves=design,shelf_depth=shelf,
        curvature=curvature,convex_shelf_conflict_lower_bound=lower_bound,
        unchanged_north_and_usb_vs_round2_and_round3=True,north_equality=north_equality,
        left_front_junctions=junctions,right_front_junctions=[dict(r,xy=[-r["xy"][0],r["xy"][1]]) for r in junctions],
        sweep_only_sampled_minimum=sweep_min,
        front_curve_and_endpoint_minimum=min(front_angles,key=lambda a:a['degrees']),
        front_endpoint_angles=[front_angles[0],front_angles[-1]],
        retained_bridge_interior_angle=bridge_angle,
        analytic_endpoint_join='R5 circular fillets; all line/arc/sweep joins tangent',
        design_primitive_counts_per_tray=dict(south_quadratic_sweeps=1,endpoint_circular_fillets=2,north_quadratic_portion=1,straight_segments_including_seam=4,total=8),
        analytic_front_minimum_interior_angle_degrees=120.,
        usb=dict(center_x_mm=usb_front[0],existing_connector_front_xy_mm=usb_front,
            width_mm=12.,z_open_from_mm=11.2,z_wall_top_mm=15.2,
            minimum_height_mm=4.,open_top=True,plan_cut_bounds_xy_mm=list(slot.bounds),
            wall_crossing_xy=list(crossing.coords) if crossing.geom_type=='LineString' else str(crossing),
            alignment='Provisional current seat datum; final alignment in pending Fly seat rework'),
        removed_material_vs_198=dict(area_mm2=removed.area,regions=removed_records),
        area_vs_198=dict(added_mm2=new_final.difference(old_final).area,
            removed_mm2=removed.area,net_mm2=new_final.area-old_final.area),
        area_vs_round3=dict(added_mm2=new_final.difference(r3_final).area,
            removed_mm2=r3_final.difference(new_final).area,net_mm2=new_final.area-r3_final.area),
        area_vs_round2=dict(added_mm2=new_final.difference(r2_final).area,
            removed_mm2=r2_final.difference(new_final).area,net_mm2=new_final.area-r2_final.area),
        area_vs_round1=dict(added_mm2=new_final.difference(r1_final).area,
            removed_mm2=r1_final.difference(new_final).area,net_mm2=new_final.area-r1_final.area),
        trays={},boards={})
    for name,pcb in boards.items():
        clear=pcb.buffer(.502,join_style=2)
        assert new.covers(clear)
        measures['boards'][name]=dict(pcb_margin=distance_record(pcb.boundary,new.boundary),
            clearance_margin=distance_record(clear.boundary,new.boundary),
            clearance_outside_mm2=clear.difference(new).area,clearance_covered=True)
    for side,clip in [('left',box(-300,-200,3.5,200)),('right',box(3.5,-200,300,200))]:
        geometries=[g.intersection(clip) for g in (old_final,r1_final,r2_final,r3_final,new_final)]
        before,previous,r2_tray,r3_tray,after=geometries
        b=after.bounds
        counts={name:dict(raw=len(g.exterior.coords)-1,normalized=vertices(g))
                for name,g in zip(('issue198','round1','round2','round3','round4'),geometries)}
        measures['trays'][side]=dict(counts=counts,bounds_xy_mm=list(b),
            footprint_xy_mm=[b[2]-b[0],b[3]-b[1]],
            with_5mm_brim_xy_mm=[b[2]-b[0]+10,b[3]-b[1]+10],
            footprint_change_vs_198_xy_mm=[(b[2]-b[0])-(before.bounds[2]-before.bounds[0]),(b[3]-b[1])-(before.bounds[3]-before.bounds[1])],
            footprint_change_vs_round1_xy_mm=[(b[2]-b[0])-(previous.bounds[2]-previous.bounds[0]),(b[3]-b[1])-(previous.bounds[3]-previous.bounds[1])])
        assert max(measures['trays'][side]['with_5mm_brim_xy_mm'])<=220
        curve=LineString(south['path_xy_mm'] if side=='left' else [(-x,y) for x,y in south['path_xy_mm']])
        assert curve.difference(new.boundary.buffer(1e-8)).length<1e-8
    # Bound Bezier-vs-chord deviation by max |B''| / (8*N^2).
    error={}
    for name,p in [('south_span_'+str(i),p) for i,p in enumerate(spans)]+[('north',design['north_controls_xy_mm'])]:
        degree=len(p)-1
        second=[tuple(degree*(degree-1)*(p[j+2][k]-2*p[j+1][k]+p[j][k]) for k in (0,1)) for j in range(degree-1)]
        error[name]=max(math.hypot(*v) for v in second)/(8*design['steps_per_span']**2)
    error['circular_fillets']=max(f['radius_mm']*(1-math.cos(f['sweep_radians']/256)) for f in south['fillets'])
    measures['chord_deviation_upper_bound_mm']=error
    (HERE/'17mm-outline.json').write_text(json.dumps(dict(measurements=measures,
        cavity_xy=list(cavity.exterior.coords),current_xy=list(old_final.exterior.coords),
        round1_xy=list(r1_final.exterior.coords),round2_xy=list(r2_final.exterior.coords),round3_xy=list(r3_final.exterior.coords),proposed_xy=list(new_final.exterior.coords)),indent=2)+'\n')
    (RUNTIME/'measurements.json').write_text(json.dumps(measures,indent=2)+'\n')
    def draw(ax,g,**kw):
        x,y=g.exterior.xy;ax.plot(x,y,**kw)
    def plot(ax):
        for g in boards.values():ax.fill(*g.exterior.xy,color='#d9e5ee',alpha=.85)
        draw(ax,cavity,color='#748596',lw=.7,label='Unchanged pocket (+0.502 mm)')
        draw(ax,old_final,color='#d65343',lw=1.4,ls='--',label='Current #198')
        draw(ax,r3_final,color='#947399',lw=1.4,alpha=.4,ls='-',label='Round 3 (rejected ripple)')
        draw(ax,new_final,color='#007c83',lw=2,label='Round 4 convex quadratic + R5 fillets')
        ax.axvline(3.5,color='#5e4b95',ls=':',lw=.7,label='Split X=3.5 mm')
        # Plan projection of wall opening above intact low rim/floor.
        x,y=slot.exterior.xy
        ax.fill(x,y,facecolor='#f1b438',edgecolor='#996600',alpha=.25,hatch='///',label='USB open-top port, W12 × H4 mm')
        ax.set_aspect('equal');ax.grid(alpha=.15)
        ax.set_xlabel('Assembly X (mm)');ax.set_ylabel('Assembly Y (mm; south downward)')
        ax.legend(loc='upper right',fontsize=8,framealpha=.95)
    fig,ax=plt.subplots(figsize=(14,8));plot(ax)
    ax.set_xlim(-160,160);ax.set_ylim(102,-78)
    ax.set_title('Issue #228 • Phase A round 4 • assembled 17 mm trays • 2D gate')
    fig.tight_layout();fig.savefig(HERE/'17mm-outline-overlay.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,9));plot(ax)
    ax.set_xlim(-166,-24);ax.set_ylim(103,-20)
    for label,point,offset in [('Pinky R5 fillet',south['fillets'][0]['points_xy_mm'][64],(12,-8)),('Thumb R5 fillet',south['fillets'][1]['points_xy_mm'][64],(-58,15))]:
        ax.scatter(*point,color='#005e63',s=24,zorder=5)
        ax.annotate(label,xy=point,xytext=offset,textcoords='offset points',arrowprops=dict(arrowstyle='->'),fontsize=10)
    for row in shelf['valley_centers']:
        p,q=row['first_xy'],row['second_xy']
        ax.plot([p[0],q[0]],[p[1],q[1]],color='#e09612',lw=1.2)
        ax.annotate(f"{row['mm']:.2f} mm",p,xytext=(5,5),textcoords='offset points',fontsize=8)
    p=maximum['first_xy']
    ax.annotate(f"Shelf maximum {maximum['mm']:.2f} mm\n13 mm limit conflict",xy=p,xytext=(-149,44),arrowprops=dict(arrowstyle='->'),fontsize=9)
    ax.annotate('120° retained bridge join',xy=bridge,xytext=(-100,98),arrowprops=dict(arrowstyle='->'),fontsize=10)
    ax.set_title('One convex left south sweep + R5 endpoint fillets • right mirrored')
    fig.tight_layout();fig.savefig(HERE/'17mm-south-edge-zoom.png',dpi=180);plt.close(fig)
    print(json.dumps({k:v for k,v in measures.items() if k not in ('curves','shelf_depth')},indent=2))


if __name__ == '__main__':
    main()
