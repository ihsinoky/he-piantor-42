"""Static physical width and saved-session statistics; no router execution."""
import collections,hashlib,json,math,pathlib,sys
import sexpdata as sx
E=pathlib.Path(__file__).resolve().parent
stage=sys.argv[1]; work=E/'processes'/stage
ses=sx.loads((work/'out.ses').read_text())
def children(node,key): return [x for x in node if isinstance(x,list) and x and str(x[0])==key]
def one(node,key):
    rows=children(node,key); assert len(rows)==1,(key,len(rows)); return rows[0]
routes=one(ses,'routes'); resolution=one(routes,'resolution'); assert str(resolution[1])=='um'
per_mm=1000*float(resolution[2]); network=one(routes,'network_out')
widths=[]; lengths=[]; vias=[]; layers=collections.Counter(); nets=[]; paths=0;segments=0; narrow=[]
for net in children(network,'net'):
    nets.append(str(net[1]))
    for wire in children(net,'wire'):
        path=one(wire,'path'); paths+=1; layer=str(path[1]); layers[layer]+=1
        width=float(path[2])/per_mm; widths.append(width)
        if width<.2-1e-9: narrow.append(dict(net=str(net[1]),global_path_index=paths,width_mm=width,path_tokens=[str(x) for x in path]))
        coords=list(map(float,path[3:])); assert len(coords)%2==0
        xy=list(zip(coords[::2],coords[1::2])); segments+=len(xy)-1
        lengths.append(sum(math.dist(a,b)/per_mm for a,b in zip(xy,xy[1:])))
    vias.extend(children(net,'via'))
report=json.loads((work/'result.json').read_text())
stats={'unrouted':report['report']['incompleteAfter']}
result=dict(stage=stage,ses_sha256=hashlib.sha256((work/'out.ses').read_bytes()).hexdigest(),resolution=str(resolution),units_per_mm=per_mm,width_histogram_mm=dict(collections.Counter(map(str,widths))),minimum_width_mm=min(widths) if widths else None,paths_below_020mm=sum(w<.2-1e-9 for w in widths),layers=dict(layers),paths=paths,segments=segments,vias=len(vias),routed_nets=len(nets),centerline_length_mm=sum(lengths),report_stats=stats,narrow_paths=narrow,scope='Static SES serialization checks only; does not prove actual connectivity or clearance. Four independent Main metrics remain null if unrouted remains.')
(E/(stage+'-ses-inspection.json')).write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
