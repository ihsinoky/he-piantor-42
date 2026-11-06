"""Read-only, bounded single-via relocation probes using the saved all-via audit.

Candidates are independent, not a simultaneous routing solution or DRC approval.
No board is modified or saved. Run again to resume completed boards/checkpoints.
"""
from audit import *
import shapely
import numpy as np

METHOD='independent-probe-v2-mm-anchors'
GUARD=0.00002

def probe(source,runtime):
    b,pads,tracks,vias,keepouts,npth=load_geometry(source,runtime)
    layers=list(b.GetEnabledLayers().CuStack());w=E/source['board']
    rows=json.loads((w/'all-vias.json').read_text())
    assert json.loads((w/'summary.json').read_text())['source_sha256']==source['sha256']
    assert {r['uuid'] for r in rows}=={v.m_Uuid.AsString() for v in vias}
    outline=p.SHAPE_POLY_SET();assert b.GetBoardPolygonOutlines(outline)
    board=polygons(outline)
    all_pad_geom=unary_union([g for a in pads for g in a['geoms'].values()])
    track_geom=[]
    for t in tracks:
        if isinstance(t,p.PCB_VIA):continue
        assert t.GetClass()=='PCB_TRACK',t.GetClass()
        line=LineString([xy(t.GetStart()),xy(t.GetEnd())])
        track_geom.append((t,line,line.buffer(t.GetWidth()/2/MM+GUARD,quad_segs=32)))
    fixed_forbidden=[]
    for ref,pos,size in npth:
        assert abs(size[0]-size[1])<1e-9
        fixed_forbidden.append(Point(pos).buffer(size[0]/2+0.25+GUARD,quad_segs=128))
    for k in keepouts:
        if k['via_forbidden']:fixed_forbidden.append(k['geometry'])
    fixed=unary_union(fixed_forbidden)
    checkpoint=w/'move-checkpoint.json'
    if checkpoint.exists():
        saved=json.loads(checkpoint.read_text());assert saved['method']==METHOD
        results=saved['results']
    else:results=[]
    done={r['via_uuid'] for r in results}
    offsets=sorted([(round(rad*math.cos(math.radians(ang)),9),round(rad*math.sin(math.radians(ang)),9)) for rad in np.arange(0.05,3.0001,0.05) for ang in range(0,360,5)],key=lambda q:q[0]*q[0]+q[1]*q[1])
    for r in rows:
        if r['passes_0p10'] or r['uuid'] in done:continue
        v=next(v for v in vias if v.m_Uuid.AsString()==r['uuid']);origin=[r['x_mm'],r['y_mm']];radius=r['diameter_mm']/2
        other_vias=[o for o in vias if o.m_Uuid.AsString()!=r['uuid']]
        # All via positions are fixed except the one being probed. Same-net vias
        # also retain 0.10mm copper spacing (a deliberately conservative filter).
        other_disks=unary_union([Point(xy(o.GetPosition())).buffer(o.GetWidth(p.F_Cu)/2/MM+radius+0.1+GUARD,quad_segs=128) for o in other_vias])
        foreign_tracks=[(t,line,g) for t,line,g in track_geom if t.GetNetname()!=r['net']]
        foreign_copper=unary_union([g for t,line,g in foreign_tracks])
        assert all(v.IsOnLayer(l) for l in layers)
        disk=p.SHAPE_CIRCLE(v.GetPosition(),round(radius*MM))
        incident=[(t,line) for t,line,g in track_geom if t.GetNetname()==r['net'] and t.GetEffectiveShape(t.GetLayer()).Collide(disk)]
        anchors=[]
        pad_stub_floor=0.3 if source['board'].startswith('wing-') and r['net'] in ['HALL_5V','GND'] else 0.1
        for t,line in incident:
            q=line.interpolate(line.project(Point(origin)))
            anchors.append(dict(kind='track',uuid=t.m_Uuid.AsString(),layer=b.GetLayerName(t.GetLayer()),position_mm=[q.x,q.y],width_mm=t.GetWidth()/MM))
        # A stub from the old via center can miss an edge-overlapping pad.
        # Anchor to each same-net touched pad's center instead.
        for a in pads:
            if a['net']!=r['net']:continue
            for l,shape in a['shapes'].items():
                if shape.Collide(disk):
                    anchors.append(dict(kind='pad',uuid=a['uuid'],ref=a['ref'],pad=a['pad'],layer=b.GetLayerName(l),position_mm=a['position_mm'],width_mm=max([t.GetWidth()/MM for t,line in incident if t.GetLayer()==l]+[pad_stub_floor])))
        positions=np.array([[round(origin[0]+dx,6),round(origin[1]+dy,6)] for dx,dy in offsets]);points=shapely.points(positions)
        pad_ok=shapely.distance(points,all_pad_geom)>=radius+0.1+GUARD
        body_ok=pad_ok & shapely.contains(board.buffer(-radius-0.3-GUARD),points)
        if not fixed.is_empty:body_ok &= shapely.distance(points,fixed)>=radius+GUARD
        body_ok &= ~shapely.intersects(points,other_disks)
        if not foreign_copper.is_empty:body_ok &= shapely.distance(points,foreign_copper)>=radius+0.1+GUARD
        indices=np.flatnonzero(body_ok);nearest_pad_idx=np.flatnonzero(pad_ok)
        out=dict(via_uuid=r['uuid'],origin_mm=origin,net=r['net'],classification=r['classification'],hit_pads=r['hit_pads'],nearest_pad=r['nearest_pad'],min_gap_mm=r['min_annulus_gap_mm'],tested_positions=len(positions),pad_only_candidate_count=int(pad_ok.sum()),fixed_copper_candidate_count=len(indices),anchors=anchors,pad_only_nearest_mm=positions[nearest_pad_idx[0]].tolist() if len(nearest_pad_idx) else None,fixed_copper_nearest_mm=None,straight_stub_candidate_mm=None,status='no-fixed-copper-candidate-in-grid')
        # Precompute foreign obstacles per layer. Same-net pads/tracks may merge;
        # all pads still require the full 0.10mm via-body separation above.
        obstacles={}
        for l in layers:
            shapes=[a['geoms'][l] for a in pads if a['net']!=r['net'] and l in a['geoms']]
            shapes += [g for t,line,g in foreign_tracks if t.GetLayer()==l]
            shapes += [Point(xy(o.GetPosition())).buffer(o.GetWidth(l)/2/MM+GUARD,quad_segs=128) for o in other_vias if o.GetNetname()!=r['net'] and o.IsOnLayer(l)]
            obstacles[b.GetLayerName(l)]=unary_union(shapes)
        def native_body(pos):
            center=point(pos);new_disk=p.SHAPE_CIRCLE(center,round(radius*MM))
            gap=min(shape.Distance(center)/MM-radius for a in pads for shape in a['shapes'].values())
            if gap<0.1-1e-12:return False
            if any(t.GetEffectiveShape(t.GetLayer()).Collide(new_disk,p.FromMM(0.1)) for t,line,g in foreign_tracks):return False
            return True
        for index in indices:
            pos=positions[index].tolist()
            if not native_body(pos):continue
            if out['fixed_copper_nearest_mm'] is None:
                out['fixed_copper_nearest_mm']=pos;out['fixed_copper_displacement_mm']=math.dist(origin,pos);out['status']='candidate-requires-local-reroute'
            valid=bool(anchors)
            for anchor in anchors:
                layer=anchor['layer'];l=b.GetLayerID(layer);width=anchor['width_mm']
                stub=LineString([anchor['position_mm'],pos]).buffer(width/2+GUARD,quad_segs=32)
                if not obstacles[layer].is_empty and stub.distance(obstacles[layer])<0.1:valid=False;break
                if not board.buffer(-0.3-GUARD).covers(stub):valid=False;break
                if any(l in k['layers'] and k['track_forbidden'] and stub.intersects(k['geometry']) for k in keepouts):valid=False;break
                if any(stub.distance(Point(pos_h))<size[0]/2+0.25+GUARD for ref,pos_h,size in npth):valid=False;break
            if valid:
                out['straight_stub_candidate_mm']=pos;out['straight_stub_displacement_mm']=math.dist(origin,pos);out['status']='candidate-with-straight-local-stubs';break
        results.append(out)
        dump(checkpoint,dict(method=METHOD,results=results))
        print(source['board'],r['uuid'],out['status'],out['fixed_copper_nearest_mm'],flush=True)
    dump(w/'move-probes.json',results);write_csv(w/'move-probes.csv',results)
    summary=dict(board=source['board'],source_sha256=source['sha256'],method=METHOD,violating_vias=len(results),status_counts=dict(collections.Counter(r['status'] for r in results)),radial_step_mm=0.05,angle_step_deg=5,max_radius_mm=3.0,guard_mm=GUARD,all_other_vias_fixed=True,simultaneous_routing_solution=False,zone_refill_performed=False,placement_changes_proven_necessary=False,connectivity_drc_proven=False)
    assert len(results)==sum(not r['passes_0p10'] for r in rows)
    dump(w/'move-summary.json',summary);checkpoint.unlink(missing_ok=True)
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--runtime',type=Path,default=Path('.issue183-runtime'));parser.add_argument('--board',action='append');args=parser.parse_args();args.runtime.mkdir(exist_ok=True)
    summaries=[]
    for source in json.loads((E/'sources.json').read_text()):
        if args.board and source['board'] not in args.board:continue
        saved=E/source['board']/'move-summary.json'
        if saved.exists():
            summary=json.loads(saved.read_text());assert summary['method']==METHOD and summary['source_sha256']==source['sha256']
        else:summary=probe(source,args.runtime)
        summaries.append(summary)
    dump(E/'move-summary.json',summaries)
