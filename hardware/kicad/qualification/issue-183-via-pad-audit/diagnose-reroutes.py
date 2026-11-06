"""Explain obstacles on the nearest saved move candidate's direct connections.

A blocked nearest path is evidence of a local routing problem, not proof that
all curved paths, coordinated moves, or the fixed placement are impossible.
"""
from audit import *

def diagnose(source,runtime):
    b,pads,tracks,vias,keepouts,npth=load_geometry(source,runtime)
    w=E/source['board'];results=[]
    for q in json.loads((w/'move-probes.json').read_text()):
        if q['straight_stub_candidate_mm'] is not None:continue
        pos=q['fixed_copper_nearest_mm'];failures=[]
        if pos is not None:
            for a in q['anchors']:
                l=b.GetLayerID(a['layer']);stub=p.SHAPE_SEGMENT(point(a['position_mm']),point(pos),p.FromMM(a['width_mm']))
                for pad in pads:
                    if pad['net']!=q['net'] and l in pad['shapes'] and pad['shapes'][l].Collide(stub,p.FromMM(0.1)):
                        failures.append(dict(anchor_uuid=a['uuid'],layer=a['layer'],kind='pad',ref=pad['ref'],pad=pad['pad'],net=pad['net'],uuid=pad['uuid']))
                for t in tracks:
                    if t.GetNetname()==q['net'] or not t.IsOnLayer(l):continue
                    if t.GetEffectiveShape(l).Collide(stub,p.FromMM(0.1)):
                        failures.append(dict(anchor_uuid=a['uuid'],layer=a['layer'],kind=t.GetClass(),net=t.GetNetname(),uuid=t.m_Uuid.AsString()))
                geom=LineString([a['position_mm'],pos]).buffer(a['width_mm']/2+0.00002,quad_segs=128)
                for k in keepouts:
                    if l in k['layers'] and k['track_forbidden'] and geom.intersects(k['geometry']):
                        failures.append(dict(anchor_uuid=a['uuid'],layer=a['layer'],kind='track-keepout',uuid=k['uuid']))
                for ref,pos_h,size in npth:
                    if geom.distance(Point(pos_h))<size[0]/2+0.25+0.00002:
                        failures.append(dict(anchor_uuid=a['uuid'],layer=a['layer'],kind='NPTH-clearance',ref=ref))
        results.append(dict(via_uuid=q['via_uuid'],net=q['net'],origin_mm=q['origin_mm'],hit_pads=q['hit_pads'],nearest_pad=q['nearest_pad'],status=q['status'],nearest_fixed_candidate_mm=pos,nearest_direct_connection_obstacles=failures,necessity_of_placement_change_proven=False))
    dump(w/'reroute-obstacles.json',results)
    return results

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--runtime',type=Path,default=Path('.issue183-runtime'));parser.add_argument('--board',action='append');args=parser.parse_args()
    for source in json.loads((E/'sources.json').read_text()):
        if not args.board or source['board'] in args.board:
            results=diagnose(source,args.runtime);print(source['board'],len(results),'reroute cases explained')
