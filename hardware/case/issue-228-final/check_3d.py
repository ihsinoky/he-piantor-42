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

def leaves(shape,owner=None):
    # STEP often calls a Compound's contained solid 'SOLID'. Retain the owning
    # part name so the two tray halves cannot collapse into one dictionary entry.
    label=shape.label
    if not label or label.lower() in ('solid','compound','assembly','part'):label=owner
    cs=list(shape.children) if hasattr(shape,'children') else []
    if cs:return [x for c in cs for x in leaves(c,label)]
    if label:shape.label=label
    return [shape]

def check(pitch):
    out=HERE/f'{pitch}mm';gate=json.loads((out/'outline-check.json').read_text())
    trays=[import_step(out/f'tray-{side}.step') for side in ('left','right')]
    actual=section(trays,1.,ignore_holes=True)
    assert not actual.is_empty
    expected=unary_union([Polygon(gate['outer_xy_mm']),*[box(-10.5,y-8,17.5,y+8) for y in (-8.,55.)]])
    deviation=actual.boundary.hausdorff_distance(expected.boundary)
    # Sections use only the outer wires: the floor's internal screw bores are excluded.
    assert deviation<.05, deviation
    d=json.loads((out/'dimensions.json').read_text());f=d['fly']
    assembly=import_step(out/'assembly.step');items={}
    # Repeated source STEP instances can share a product label. Check every instance.
    for shape in leaves(assembly):
        label=shape.label;key=label;index=1
        while key in items:key=f'{label}@{index}';index+=1
        items[key]=shape
    assert len(items)==d['assembly_solid_count'],(len(items),d['assembly_solid_count'])
    assert 'tray-left' in items and 'tray-right' in items, list(items)
    from build123d import Face,Wire,extrude
    def block(x0,y0,x1,y1,z,h):
        return extrude(Face(Wire.make_polygon([(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)],close=True)),amount=h)
    def volume(a,b):
        q=a.intersect(b);return sum(s.volume for s in q) if q else 0.
    measured_wall=actual.boundary.intersection(LineString([(0,-100),(0,-40)])).y
    measured_mouth=items['Fly-official-42'].bounding_box().min.Y
    assert abs(measured_mouth-measured_wall-.3)<1e-5
    board_bottom=f['board_bottom_z_mm']
    pcb_bb=items['Fly-official-00'].bounding_box()
    assert abs(pcb_bb.min.Z-board_bottom)<1e-6 and abs(pcb_bb.max.Z-board_bottom-1.59)<1e-6
    pcb_sections=items['Fly-official-00'].intersect(Plane.XY.offset(board_bottom+.795))
    pcb_side_gap=min(face.distance_to(t) for face in pcb_sections for t in trays)
    assert pcb_side_gap>.2,('Fly lateral PCB clearance',pcb_side_gap)
    # Independently bracket both 16 mm face edges and the opening's bottom.
    probes=[]
    for x,z,want in [(0,board_bottom-.31,True),(0,board_bottom-.29,False),(-7.99,board_bottom+3.32,False),(7.99,board_bottom+3.32,False),(-8.01,board_bottom+3.32,True),(8.01,board_bottom+3.32,True)]:
        present=any(s.is_inside(Vector(x,measured_wall+.005,z)) for t in trays for s in t.solids())
        assert present==want,(x,z,present,want)
        probes.append(dict(x_mm=x,y_mm=measured_wall+.005,z_mm=z,material=present))
    mouth=f['mouth_y_mm'];shell=items['USB-reference-shell'];sb=shell.bounding_box()
    engagement=sb.max.Y-mouth
    assert abs(engagement-6.2)<1e-5
    # Continuous translational sweep bounded by Cartesian products. Checking these
    # larger solids proves the entire insertion, including every intermediate pose.
    travel=30.
    swept={
      'shell':block(-4.45,sb.min.Y-travel,4.45,sb.max.Y,board_bottom+1.72,3.2),
      'overmold':block(-6,sb.min.Y-15-travel,6,sb.min.Y,board_bottom+.32,6),
      'cable-exit':block(-2,sb.min.Y-40-travel,2,sb.min.Y-15,board_bottom+1.32,4)}
    collisions=[];gaps={}
    for name,probe in swept.items():
        for label,shape in items.items():
            if label.startswith('USB-reference-') or label.split('@')[0] in {f'Fly-official-{i:02d}' for i in [*range(1,25),41,42]}:continue
            bb=shape.bounding_box();pb=probe.bounding_box()
            # Distance only to case; other candidates use strict bbox broad phase.
            if label.startswith('tray-'):gaps[name+' / '+label]=probe.distance_to(shape)
            if any(min(a,c)-max(b,e)<=1e-6 for a,b,c,e in [(pb.max.X,pb.min.X,bb.max.X,bb.min.X),(pb.max.Y,pb.min.Y,bb.max.Y,bb.min.Y),(pb.max.Z,pb.min.Z,bb.max.Z,bb.min.Z)]):continue
            v=volume(probe,shape)
            if v>1e-4:collisions.append(dict(probe=name,obstacle=label,volume_mm3=v))
    assert not collisions,collisions
    route=items['EZmate-170mm-route']
    route_gaps={label:route.distance_to(shape) for label,shape in items.items() if label not in ('EZmate-170mm-route','EZmate-Fly-plug','EZmate-Main-plug','Main-envelope-J4') and not label.startswith('USB-reference-') and label!='Fly-official-67'}
    route_gaps['Fly-PCB']=route.distance_to(items['Fly-official-00'])
    assert min(route_gaps.values())>.2,sorted(route_gaps.items(),key=lambda q:q[1])[:5]
    # Under-board mating envelopes and all official components, including shell legs.
    under={label: min(shape.distance_to(t) for t in trays) for label,shape in items.items() if label.startswith('EZmate-') or (label.startswith('Fly-official-') and shape.bounding_box().min.Z<9.99)}
    assert all(v>.2 for v in under.values()),under
    result=dict(pitch_mm=pitch,silhouette_max_deviation_mm=deviation,
                section_max_edge_sample_spacing_mm=.02,
                conservative_hausdorff_upper_bound_mm=deviation+.01,
                usb=dict(opening=f['opening'],material_probes=probes,measured_mouth_recess_mm=measured_mouth-measured_wall,measured_board_bottom_z_mm=pcb_bb.min.Z,engagement_mm=engagement,travel_mm=travel,
                         continuous_swept_envelopes_xyz_mm=dict(shell=[8.9,travel+6.65,3.2],overmold=[12,travel+15,6],cable_exit=[4,travel+25,4]),
                         unexpected_sweep_collisions=collisions,case_clearances_mm=gaps,
                         connector_internal_overlaps=f['usb']['connector_internal_overlaps'],
                         strict_connector_internal_zero_overlap=not bool(f['usb']['connector_internal_overlaps'])),
                fly_pcb_midplane_to_case_mm=pcb_side_gap,under_board_case_clearances_mm=under,route_clearances_mm=route_gaps,
                brep={p.stem:dict(faces=len((s:=import_step(p)).faces()),edges=len(s.edges()),solids=len(s.solids()),valid=s.is_valid) for p in sorted(out.glob('*.step'))})
    result['blockers']=[]
    source=import_step(HERE/'inputs/TheFly_DaughterBoard_V4.2.stp')
    result['source_invalid_solid_indices']=[i for i,s in enumerate(source.solids()) if not s.is_valid]
    if result['source_invalid_solid_indices']:result['blockers'].append('Supplied official Fly has invalid BRep solids on direct import; preserved without healing.')
    if f['usb']['connector_internal_overlaps']:result['blockers'].append('Strict USB connector-internal zero overlap at nominal full mate is not demonstrated.')
    result['case_insertion_passed']=not collisions
    result['passed']=not result['blockers'] and all(q['valid'] for q in result['brep'].values())
    (out/'3d-check.json').write_text(json.dumps(result,indent=2)+'\n')
    assembly=import_step(out/'assembly.step');polys=[]
    wire_only=[s for s in leaves(assembly) if not s.is_valid]
    result['render_wire_only_labels']=[s.label for s in wire_only]
    for s in leaves(assembly):
        label=s.label.lower()
        color='#7f989d' if 'tray' in label else '#629b78' if label in ('main','wing_left','wing_right') or label.startswith('fly-official-') else '#e89940' if 'gh-' in label else '#46505c'
        if not s.is_valid:continue
        vertices,triangles=s.tessellate(.03,.1)
        for tri in triangles:
            v=[vertices[i] for i in tri]
            xy=[(p.X,p.Y) for p in v]
            if Polygon(xy).area>1e-9:polys.append((sum(p.Z for p in v)/3,xy,color))
    polys.sort(key=lambda v:v[0])
    fig,ax=plt.subplots(figsize=(14,8));ax.add_collection(PolyCollection([p[1] for p in polys],facecolors=[p[2] for p in polys],edgecolors='none'))
    for shape in wire_only:
        for edge in shape.edges():
            n=max(2,math.ceil(edge.length/.1));pts=edge.positions([i/n for i in range(n+1)])
            ax.plot([p.X for p in pts],[p.Y for p in pts],color='#185578',lw=.25)
    x,y=expected.exterior.xy;ax.plot(x,y,color='#be4262',lw=.6,ls='--',label='approved 2D perimeter')
    ax.autoscale();ax.set_aspect('equal');ax.invert_yaxis();ax.legend(loc='upper right')
    ax.set_title(f'Issue #228 · {pitch} mm · assembled exported STEP, top view\nmaximum perimeter deviation {deviation:.6f} mm · invalid source shell shown as BRep edges')
    ax.set_xlabel('assembly X (mm)');ax.set_ylabel('assembly Y (mm, south)')
    fig.tight_layout();fig.savefig(out/'assembled-top.png',dpi=180);plt.close(fig)
    # Orthographic side view of actual exported triangles, clipped to north bay.
    close=[]
    for tray in trays:
        for face in tray.intersect(Plane(origin=(0,0,0),z_dir=(1,0,0))) or []:
            vs,ts=face.tessellate(.03,.1)
            for tri in ts:close.append((-100,[(vs[i].Y,vs[i].Z) for i in tri],'#a7b5bd'))
    for shape in leaves(assembly):
        label=shape.label
        if not (label.startswith(('Fly-official-','USB-reference-','EZmate-Fly')) or label=='EZmate-170mm-route'):continue
        if not shape.is_valid:continue
        vs,ts=shape.tessellate(.03,.1)
        color='#a7b5bd' if label.startswith('tray-') else '#3b9a72' if label=='Fly-official-00' else '#db923e' if label.startswith(('USB-reference-','EZmate-')) else '#526375'
        for tri in ts:
            v=[vs[i] for i in tri]
            if min(p.X for p in v)>12.4 or max(p.X for p in v)<-12.4:continue
            yz=[(p.Y,p.Z) for p in v]
            if Polygon(yz).area>1e-9:close.append((sum(p.X for p in v)/3,yz,color))
    close.sort(key=lambda q:q[0])
    fig,ax=plt.subplots(figsize=(12,6));ax.add_collection(PolyCollection([q[1] for q in close],facecolors=[q[2] for q in close],edgecolors='none'))
    for shape in wire_only:
        for edge in shape.edges():
            n=max(2,math.ceil(edge.length/.1));pts=edge.positions([i/n for i in range(n+1)])
            ax.plot([p.Y for p in pts],[p.Z for p in pts],color='#185578',lw=.4)
    ax.axvline(f['wall_outer_y_at_x0_mm'],color='#c43e60',ls='--',lw=1,label='outer wall at X0')
    ax.axvline(mouth,color='#1661aa',ls=':',lw=1,label='receptacle mouth, 0.30 mm recessed')
    ax.set_xlim(mouth-24,f['transform']['translation_mm'][1]+9);ax.set_ylim(0,board_bottom+9);ax.set_aspect('equal')
    ax.set_xlabel('Assembly Y (mm; outside north at left)');ax.set_ylabel('Z (mm)')
    ax.set_title(f'{pitch} mm · exported STEP north wall X0 section / electronics side projection · nominal USB mate 6.2 mm\nInvalid official shell shown as BRep edges · strict mating proof blocked')
    ax.legend(loc='upper left');fig.tight_layout();fig.savefig(out/'north-wall-closeup.png',dpi=180);plt.close(fig)
    (out/'3d-check.json').write_text(json.dumps(result,indent=2)+'\n')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.suffix in ('.step','.stl','.svg','.json','.csv','.png') and p.name not in ('exports-sha256.json','verification.json')}
    (out/'exports-sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
    assert result['passed'],result['blockers']

if __name__=='__main__':check(int(sys.argv[1]) if len(sys.argv)>1 else 17)
