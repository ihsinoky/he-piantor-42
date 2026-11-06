"""Read-only all-via/pad audit. Run with KiCad 9 pcbnew; never saves a board."""
from pathlib import Path
import argparse, collections, csv, gzip, hashlib, json, math, sys
import pcbnew as p
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union

E=Path(__file__).resolve().parent
MM=1_000_000
CLEARANCE=0.1
EPS=0.000002  # 2 nm numeric boundary band, separately exposed

def dump(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def xy(v): return [v.x/MM,v.y/MM]
def point(v): return p.VECTOR2I(round(v[0]*MM),round(v[1]*MM))
def polygons(ps):
    def ring(line):return [xy(line.CPoint(i)) for i in range(line.PointCount())]
    return unary_union([Polygon(ring(ps.Outline(i)),[ring(ps.Hole(i,j)) for j in range(ps.HoleCount(i))]) for i in range(ps.OutlineCount())])
def pad_polygon(a,layer):
    ps=p.SHAPE_POLY_SET();a.TransformShapeToPolygon(ps,layer,0,10,p.ERROR_OUTSIDE)
    g=polygons(ps);assert g.is_valid and not g.is_empty
    return g

def write_csv(path,rows):
    with path.open('w',newline='') as f:
        fields=list(dict.fromkeys(k for row in rows for k in row))
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})

def load_geometry(source,runtime):
    name=source['board'];raw=gzip.decompress((E/source['snapshot']).read_bytes())
    assert hashlib.sha256(raw).hexdigest()==source['sha256']
    local=runtime/(name+'.kicad_pcb')
    if local.exists():assert local.read_bytes()==raw
    else:local.write_bytes(raw);local.chmod(0o444)
    b=p.LoadBoard(str(local));layers=list(b.GetEnabledLayers().CuStack())
    tracks=list(b.GetTracks());vias=sorted((t for t in tracks if isinstance(t,p.PCB_VIA)),key=lambda t:t.m_Uuid.AsString())
    pads=[];npth=[];keepouts=[]
    for f in b.GetFootprints():
        for a in f.Pads():
            if a.GetAttribute()==p.PAD_ATTRIB_NPTH:
                npth.append((f.GetReference(),xy(a.GetPosition()),xy(a.GetDrillSize())));continue
            shapes={l:a.GetEffectiveShape(l) for l in layers if a.IsOnLayer(l)}
            if not shapes:continue
            geoms={l:pad_polygon(a,l) for l in shapes}
            pads.append(dict(ref=f.GetReference(),pad=a.GetNumber(),uuid=a.m_Uuid.AsString(),net=a.GetNetname(),kind='testpad' if f.GetReference().startswith('TP') else 'mounted',position_mm=xy(a.GetPosition()),size_mm=xy(a.GetSize()),orientation_deg=a.GetOrientationDegrees(),layers=[b.GetLayerName(l) for l in shapes],shapes=shapes,geoms=geoms))
    for z in list(b.Zones())+[z for f in b.GetFootprints() for z in f.Zones()]:
        if z.GetIsRuleArea():
            keepouts.append(dict(uuid=z.m_Uuid.AsString(),geometry=polygons(z.Outline()),layers=[l for l in layers if z.IsOnLayer(l)],via_forbidden=z.GetDoNotAllowVias(),track_forbidden=z.GetDoNotAllowTracks()))
    return b,pads,tracks,vias,keepouts,npth

def audit(source,runtime):
    name=source['board']
    b,pads,tracks,vias,keepouts,npth=load_geometry(source,runtime)
    layers=list(b.GetEnabledLayers().CuStack())
    rows=[];pairs=[];boundary=[]
    for v in vias:
        center=v.GetPosition();radius=v.GetWidth(p.F_Cu)/2/MM;drill=v.GetDrillValue()/2/MM
        shared=[l for l in layers if v.IsOnLayer(l)]
        hits=[];distances=[]
        for a in pads:
            common=[l for l in shared if l in a['shapes']]
            if not common:continue
            d=min(a['shapes'][l].Distance(center)/MM for l in common)
            gap=d-radius
            in_pad=any(a['shapes'][l].Collide(center) for l in common)
            native_drill=any(a['shapes'][l].Collide(p.SHAPE_CIRCLE(center,round(drill*MM))) for l in common)
            native_copper=any(a['shapes'][l].Collide(p.SHAPE_CIRCLE(center,round(radius*MM))) for l in common)
            assert native_drill or d>=drill-EPS
            assert native_copper or d>=radius-EPS
            kind='center' if in_pad else 'drill-edge' if native_drill else 'annulus-only' if native_copper else 'none'
            q=dict(via_uuid=v.m_Uuid.AsString(),ref=a['ref'],pad=a['pad'],pad_uuid=a['uuid'],pad_kind=a['kind'],pad_net=a['net'],same_net=a['net']==v.GetNetname(),common_layers=[b.GetLayerName(l) for l in common],center_to_pad_mm=round(d,9),annulus_gap_mm=round(gap,9),physical_copper_gap_mm=round(max(0,gap),9),classification=kind)
            distances.append(q)
            if kind!='none':hits.append(q);pairs.append(q)
            if min(abs(d-drill),abs(d-radius),abs(gap-CLEARANCE))<=EPS:boundary.append(q)
        nearest=min(distances,key=lambda a:a['annulus_gap_mm'])
        classification=next((k for k in ['center','drill-edge','annulus-only'] if any(h['classification']==k for h in hits)),'none')
        rows.append(dict(uuid=v.m_Uuid.AsString(),x_mm=center.x/MM,y_mm=center.y/MM,net=v.GetNetname(),diameter_mm=radius*2,drill_mm=drill*2,layers=[b.GetLayerName(l) for l in shared],classification=classification,min_annulus_gap_mm=nearest['annulus_gap_mm'],min_physical_gap_mm=nearest['physical_copper_gap_mm'],passes_0p10=nearest['annulus_gap_mm']>=CLEARANCE-1e-12,nearest_pad=nearest['ref']+'.'+nearest['pad'],nearest_pad_uuid=nearest['pad_uuid'],nearest_pad_kind=nearest['pad_kind'],nearest_pad_layers=nearest['common_layers'],hit_pads=[h['ref']+'.'+h['pad'] for h in hits],hit_kinds=sorted(set(h['pad_kind'] for h in hits)),hits=hits))
    summary=dict(board=name,source_sha256=source['sha256'],kicad_version=p.Version(),total_vias=len(rows),copper_pads=len(pads),npth_excluded=len(npth),copper_layers=[b.GetLayerName(l) for l in layers],classification_counts=dict(collections.Counter(r['classification'] for r in rows)),overlapping_vias=sum(r['classification']!='none' for r in rows),violates_0p10=sum(not r['passes_0p10'] for r in rows),min_nonoverlap_gap_mm=min(r['min_annulus_gap_mm'] for r in rows if r['classification']=='none'),nonoverlap_below_0p10=sum(r['classification']=='none' and not r['passes_0p10'] for r in rows),min_annulus_gap_mm=min(r['min_annulus_gap_mm'] for r in rows),min_physical_gap_mm=min(r['min_physical_gap_mm'] for r in rows),pad_hit_pairs=len(pairs),unique_hit_pads=len(set(h['pad_uuid'] for h in pairs)),overlapping_vias_by_pad_kind={kind:sum(kind in r['hit_kinds'] for r in rows) for kind in ['mounted','testpad']},classification_by_pad_kind={kind:dict(collections.Counter(next((c for c in ['center','drill-edge','annulus-only'] if any(h['pad_kind']==kind and h['classification']==c for h in r['hits'])),'none') for r in rows if kind in r['hit_kinds'])) for kind in ['mounted','testpad']},boundary_band_pairs=boundary)
    w=E/name;w.mkdir(exist_ok=True)
    dump(w/'summary.json',summary);dump(w/'all-vias.json',rows)
    write_csv(w/'all-vias.csv',[{k:v for k,v in r.items() if k!='hits'} for r in rows]);write_csv(w/'pad-hits.csv',pairs)
    pad_rows=[{k:v for k,v in a.items() if k not in ['shapes','geoms']} for a in pads];dump(w/'pads.json',pad_rows)
    print(name,json.dumps(summary,ensure_ascii=False),flush=True)
    return b,pads,tracks,vias,keepouts,npth,rows

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--runtime',type=Path,default=Path('.issue183-runtime'));args=parser.parse_args();args.runtime.mkdir(exist_ok=True)
    summaries=[]
    for source in json.loads((E/'sources.json').read_text()):
        audit(source,args.runtime)
