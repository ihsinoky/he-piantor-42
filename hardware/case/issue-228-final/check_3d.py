"""Read exported STEP: silhouette, USB passage, BRep, and assembled top view."""
import os,math,json,sys,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(HERE.parents[2]/'.issue228-runtime/mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from build123d import import_step,Plane,Vector
from shapely.geometry import Polygon,LineString,box
from shapely import set_precision
from shapely.ops import unary_union,polygonize

def section(shapes,z,ignore_holes=False):
    def wire_polygon(wire):
        lines=[]
        for edge in wire.edges():
            n=max(2,math.ceil(edge.length/.02))
            pts=edge.positions([i/n for i in range(n+1)])
            lines.append(LineString([(p.X,p.Y) for p in pts]))
        return unary_union(list(polygonize(set_precision(unary_union(lines),1e-6))))
    polys=[]
    for shape in shapes:
        for face in shape.intersect(Plane.XY.offset(z)):
            outer=wire_polygon(face.outer_wire())
            holes=unary_union([wire_polygon(w) for w in face.inner_wires()]) if not ignore_holes else Polygon()
            polys.append(outer.difference(holes))
    return unary_union(polys)

def leaves(shape):
    cs=list(shape.children) if hasattr(shape,'children') else []
    return [x for c in cs for x in leaves(c)] if cs else [shape]

def check(pitch):
    out=HERE/f'{pitch}mm';gate=json.loads((out/'outline-check.json').read_text())
    trays=[import_step(out/f'tray-{side}.step') for side in ('left','right')]
    actual=section(trays,1.,ignore_holes=True)
    assert not actual.is_empty
    expected=unary_union([Polygon(gate['outer_xy_mm']),*[box(-10.5,y-8,17.5,y+8) for y in (-8.,55.)]])
    deviation=actual.boundary.hausdorff_distance(expected.boundary)
    # Sections use only the outer wires: the floor's internal screw bores are excluded.
    assert deviation<.05, deviation
    # Passage is measured from sectioned exported solids, throughout its width.
    low=section(trays,10.5);high=section(trays,13.2)
    slot=Polygon(gate['usb_slot_xy_mm'])
    center=gate['usb_center_x_mm']
    corridor=slot
    high_block=high.intersection(corridor).area
    assert high_block<1e-8,high_block
    wall=[]
    for x in (center-5.99,center-3,center,center+3,center+5.99):
        line=LineString([(x,slot.bounds[1]),(x,-34)])
        cut=low.intersection(line)
        segments=list(cut.geoms) if hasattr(cut,'geoms') else [cut]
        wall.append(dict(x_mm=x,thickness_mm=cut.length,bands=[dict(y_min_mm=s.bounds[1],y_max_mm=s.bounds[3],thickness_mm=s.length) for s in segments if s.length>0]))
    shoulders=[]
    for x in (center-6.01,center+6.01):
        cut=high.intersection(LineString([(x,slot.bounds[1]),(x,-34)]))
        segments=list(cut.geoms) if hasattr(cut,'geoms') else [cut]
        shoulders.append(dict(x_mm=x,total_material_mm=cut.length,bands=[dict(y_min_mm=s.bounds[1],y_max_mm=s.bounds[3],thickness_mm=s.length) for s in segments if s.length>0]))
    floor=actual.intersection(corridor).area
    low_area=low.intersection(corridor).area
    assert floor>0 and low_area>0
    # Independent inside tests at the actual north-wall midline and height bands.
    checks=[]
    for x in (center-5.9,center,center+5.9):
        line=LineString([(x,slot.bounds[1]),(x,-34)])
        segment=low.intersection(line)
        q=segment.interpolate(.5,normalized=True)
        values={str(z):any(s.is_inside(Vector(x,q.y,z)) for t in trays for s in t.solids()) for z in (1,2.1,10,11.19,11.21,13.2,15.19)}
        assert all(values[str(z)] for z in (1,2.1,10,11.19))
        assert not any(values[str(z)] for z in (11.21,13.2,15.19))
        checks.append(dict(x_mm=x,y_mm=q.y,material_present=values))
    result=dict(pitch_mm=pitch,silhouette_max_deviation_mm=deviation,
                section_max_edge_sample_spacing_mm=.02,
                conservative_hausdorff_upper_bound_mm=deviation+.01,
                usb=dict(width_mm=12,height_band_mm=[11.2,15.2],blocked_area_at_z13_2_mm2=high_block,
                         intact_floor_area_in_corridor_mm2=floor,intact_low_rim_area_in_corridor_mm2=low_area,
                         wall_thickness_samples=wall,slot_shoulder_wall_thickness_samples=shoulders,material_probes=checks),
                brep={p.stem:dict(faces=len((s:=import_step(p)).faces()),edges=len(s.edges()),solids=len(s.solids()),valid=s.is_valid) for p in sorted(out.glob('*.step'))})
    (out/'3d-check.json').write_text(json.dumps(result,indent=2)+'\n')
    assembly=import_step(out/'assembly.step');polys=[]
    for s in leaves(assembly):
        label=s.label.lower()
        color='#7f989d' if 'tray' in label else '#629b78' if label in ('main','udb','wing_left','wing_right') else '#e89940' if 'gh-' in label else '#46505c'
        vertices,triangles=s.tessellate(.03,.1)
        for tri in triangles:
            v=[vertices[i] for i in tri]
            xy=[(p.X,p.Y) for p in v]
            if Polygon(xy).area>1e-9:polys.append((sum(p.Z for p in v)/3,xy,color))
    polys.sort(key=lambda v:v[0])
    fig,ax=plt.subplots(figsize=(14,8));ax.add_collection(PolyCollection([p[1] for p in polys],facecolors=[p[2] for p in polys],edgecolors='none'))
    x,y=expected.exterior.xy;ax.plot(x,y,color='#be4262',lw=.6,ls='--',label='approved 2D perimeter')
    ax.autoscale();ax.set_aspect('equal');ax.invert_yaxis();ax.legend(loc='upper right')
    ax.set_title(f'Issue #228 · {pitch} mm · assembled exported STEP, top view\nmaximum perimeter deviation {deviation:.6f} mm')
    ax.set_xlabel('assembly X (mm)');ax.set_ylabel('assembly Y (mm, south)')
    fig.tight_layout();fig.savefig(out/'assembled-top.png',dpi=180);plt.close(fig)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.suffix in ('.step','.stl','.svg','.json','.csv','.png') and p.name not in ('exports-sha256.json','verification.json')}
    (out/'exports-sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':check(int(sys.argv[1]) if len(sys.argv)>1 else 17)
