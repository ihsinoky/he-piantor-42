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
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union, nearest_points
from outline import proposed_outline, round1_outline, curve_design, bezier, usb_access


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
    design = curve_design(boards)
    plates = [box(-10.5,y-8,17.5,y+8) for y in (-8.,55.)]
    old_final, r1_final, new_final = [unary_union([g,*plates]) for g in (old,r1,new)]
    assert new_final.covers(cavity)
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
    front=[design['left_north_xy_mm'],*bezier(design['south_left_controls_xy_mm']),
           design['left_bridge_xy_mm']]
    front_angles=angles(front)
    assert min(a['degrees'] for a in front_angles)>=120
    # Prove no cusp: at each real X-derivative root, Y derivative is nonzero.
    p=design['south_left_controls_xy_mm']
    dx=[3*(p[i+1][0]-p[i][0]) for i in range(3)]
    dy=[3*(p[i+1][1]-p[i][1]) for i in range(3)]
    assert dx[0]<0<dx[1] and dx[2]>0
    assert dy[0]>0 and dy[1]>0>dy[2]
    qa,qb,qc=dx[0]-2*dx[1]+dx[2],2*(dx[1]-dx[0]),dx[0]
    disc=qb*qb-4*qa*qc
    roots=[(-qb+sign*math.sqrt(disc))/(2*qa) for sign in (-1,1)]
    for t in roots:
        if 0<=t<=1:
            assert abs((1-t)**2*dy[0]+2*t*(1-t)*dy[1]+t*t*dy[2])>1e-8
    # The tangent vectors at both curve ends are parallel to the side lines.
    for a,b,c in [(front[0],p[0],p[1]),(p[-2],p[-1],front[-1])]:
        u=[b[k]-a[k] for k in (0,1)];v=[c[k]-b[k] for k in (0,1)]
        assert abs(u[0]*v[1]-u[1]*v[0])<1e-7
        assert sum(u[k]*v[k] for k in (0,1))>0
    # Include the retained junction from inner thumb side into central bridge.
    bridge=design['left_bridge_xy_mm']
    bridge_angle=angles([front[-2],bridge,(-bridge[0],bridge[1])])[0]
    assert bridge_angle['degrees']>=120.-1e-8
    removed=old_final.difference(new_final)
    def parts(g):
        if g.is_empty:return []
        return [g] if g.geom_type=='Polygon' else list(g.geoms)
    removed_records=[]
    for g in parts(removed):
        if g.area<1e-10:continue
        witness=g.representative_point()
        assert cavity.distance(g)>0
        local_wall=distance_record(cavity.boundary,new.boundary.intersection(g.buffer(.01)))
        assert local_wall['mm']>=2.-1e-8
        removed_records.append(dict(area_mm2=g.area,bounds_xy_mm=list(g.bounds),
            interior_witness_xy=list(witness.coords[0]),polygon_xy=list(g.exterior.coords),
            adjacent_wall=local_wall))
    measures=dict(round=2,pitch_mm=17,coordinates='assembly XY mm; +Y south',
        source_dimensions_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        pocket_outside_proposal_mm2=cavity.difference(new).area,
        wall_minimum=wall,curves=design,
        front_curve_and_endpoint_minimum=min(front_angles,key=lambda a:a['degrees']),
        front_endpoint_angles=[front_angles[0],front_angles[-1]],
        retained_bridge_interior_angle=bridge_angle,
        analytic_endpoint_join='tangent at both ends of each south cubic',
        analytic_front_minimum_interior_angle_degrees=120.,
        usb=dict(center_x_mm=usb_front[0],existing_connector_front_xy_mm=usb_front,
            width_mm=12.,z_open_from_mm=11.2,z_wall_top_mm=15.2,
            minimum_height_mm=4.,open_top=True,plan_cut_bounds_xy_mm=list(slot.bounds),
            wall_crossing_xy=list(crossing.coords) if crossing.geom_type=='LineString' else str(crossing),
            alignment='Provisional current seat datum; final alignment in pending Fly seat rework'),
        removed_material_vs_198=dict(area_mm2=removed.area,regions=removed_records),
        area_vs_198=dict(added_mm2=new_final.difference(old_final).area,
            removed_mm2=removed.area,net_mm2=new_final.area-old_final.area),
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
        geometries=[g.intersection(clip) for g in (old_final,r1_final,new_final)]
        before,previous,after=geometries
        b=after.bounds
        counts={name:dict(raw=len(g.exterior.coords)-1,normalized=vertices(g))
                for name,g in zip(('issue198','round1','round2'),geometries)}
        measures['trays'][side]=dict(counts=counts,bounds_xy_mm=list(b),
            footprint_xy_mm=[b[2]-b[0],b[3]-b[1]],
            with_5mm_brim_xy_mm=[b[2]-b[0]+10,b[3]-b[1]+10],
            footprint_change_vs_198_xy_mm=[(b[2]-b[0])-(before.bounds[2]-before.bounds[0]),(b[3]-b[1])-(before.bounds[3]-before.bounds[1])],
            footprint_change_vs_round1_xy_mm=[(b[2]-b[0])-(previous.bounds[2]-previous.bounds[0]),(b[3]-b[1])-(previous.bounds[3]-previous.bounds[1])])
        assert max(measures['trays'][side]['with_5mm_brim_xy_mm'])<=220
        curve=LineString(bezier(design['south_'+side+'_controls_xy_mm']))
        assert curve.difference(new.boundary.buffer(1e-8)).length<1e-8
    # Bound Bezier-vs-chord deviation by max |B''| / (8*N^2).
    error={}
    for name in ('south_left','north'):
        p=design[name+'_controls_xy_mm'];degree=len(p)-1
        second=[tuple(degree*(degree-1)*(p[j+2][k]-2*p[j+1][k]+p[j][k]) for k in (0,1)) for j in range(degree-1)]
        error[name]=max(math.hypot(*v) for v in second)/(8*design['steps_per_span']**2)
    measures['chord_deviation_upper_bound_mm']=error
    (HERE/'17mm-outline.json').write_text(json.dumps(dict(measurements=measures,
        cavity_xy=list(cavity.exterior.coords),current_xy=list(old_final.exterior.coords),
        round1_xy=list(r1_final.exterior.coords),proposed_xy=list(new_final.exterior.coords)),indent=2)+'\n')
    (RUNTIME/'measurements.json').write_text(json.dumps(measures,indent=2)+'\n')
    def draw(ax,g,**kw):
        x,y=g.exterior.xy;ax.plot(x,y,**kw)
    def plot(ax):
        for g in boards.values():ax.fill(*g.exterior.xy,color='#d9e5ee',alpha=.85)
        draw(ax,cavity,color='#748596',lw=.7,label='Unchanged pocket (+0.502 mm)')
        draw(ax,old_final,color='#d65343',lw=1.4,ls='--',label='Current #198')
        draw(ax,r1_final,color='#947399',lw=1.2,alpha=.45,ls=':',label='Round 1 straight (rejected)')
        draw(ax,new_final,color='#007c83',lw=2,label='Round 2 Bezier curves')
        ax.axvline(3.5,color='#5e4b95',ls=':',lw=.7,label='Split X=3.5 mm')
        # Plan projection of wall opening above intact low rim/floor.
        x,y=slot.exterior.xy
        ax.fill(x,y,facecolor='#f1b438',edgecolor='#996600',alpha=.25,hatch='///',label='USB open-top port, W12 × H4 mm')
        ax.set_aspect('equal');ax.grid(alpha=.15)
        ax.set_xlabel('Assembly X (mm)');ax.set_ylabel('Assembly Y (mm; south downward)')
        ax.legend(loc='upper right',fontsize=8,framealpha=.95)
    fig,ax=plt.subplots(figsize=(14,8));plot(ax)
    ax.set_xlim(-160,160);ax.set_ylim(102,-78)
    ax.set_title('Issue #228 • Phase A round 2 • assembled 17 mm trays • 2D gate')
    fig.tight_layout();fig.savefig(HERE/'17mm-outline-overlay.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,9));plot(ax)
    ax.set_xlim(-166,-24);ax.set_ylim(103,-20)
    controls=design['south_left_controls_xy_mm']
    for label,point,offset in [('Pinky tangent',controls[0],(12,-8)),('Thumb tangent',controls[-1],(-58,15))]:
        ax.scatter(*point,color='#005e63',s=24,zorder=5)
        ax.annotate(label,xy=point,xytext=offset,textcoords='offset points',arrowprops=dict(arrowstyle='->'),fontsize=10)
    ax.annotate('120° retained bridge join',xy=bridge,xytext=(-100,98),arrowprops=dict(arrowstyle='->'),fontsize=10)
    ax.set_title('Complete left south cubic + both tangent endpoints • right mirrored')
    fig.tight_layout();fig.savefig(HERE/'17mm-south-edge-zoom.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,8));plot(ax)
    ax.set_xlim(-43,43);ax.set_ylim(-17,-68)
    ax.annotate('Continuous north curve; notch and neck facets removed',xy=(20,-55.1),xytext=(-39,-63),arrowprops=dict(arrowstyle='->'),fontsize=9)
    ax.annotate('USB: 12 mm wide, 4 mm high, open top\nZ=11.2..15.2; current seat datum\nFinal alignment: pending Fly seat rework',xy=(0,-54.8),xytext=(-39,-44),arrowprops=dict(arrowstyle='->'),fontsize=9)
    ax.plot(*usb_front,marker='+',color='#996600',ms=10)
    ax.set_title('North-center detail • USB aperture above intact plan footprint')
    fig.tight_layout();fig.savefig(HERE/'17mm-north-center-zoom.png',dpi=180);plt.close(fig)
    print(json.dumps(measures,indent=2))


if __name__ == '__main__':
    main()
