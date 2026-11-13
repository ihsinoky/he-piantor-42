from common import *
import pcbnew as p
old=p.LoadBoard(str(E.parent/'issue-226-main-rev6/inspection/final/main.kicad_pcb'));new=p.LoadBoard(str(E/'inspection/final/main.kicad_pcb'))
def totals(b):
 d={}
 for t in b.GetTracks():
  r=d.setdefault(t.GetNetname(),dict(length_mm=0,vias=0))
  if isinstance(t,p.PCB_VIA):r['vias']+=1
  else:r['length_mm']+=p.ToMM(t.GetLength())
 return d
a=totals(old);b=totals(new);changes=[]
for n in sorted(set(a)|set(b)):
 if abs(a.get(n,{}).get('length_mm',0)-b.get(n,{}).get('length_mm',0))>1e-4 or a.get(n,{}).get('vias',0)!=b.get(n,{}).get('vias',0):changes.append(dict(net=n,before=a.get(n),after=b.get(n)))
x=json.loads((E/'routing-geometry-diff.json').read_text());bounds=[v for r in x for k,v in r.items() if k.endswith('bounds_mm') and v]
save(E/'scope-summary.json',dict(board_sha256=digest(E/'inspection/final/main.kicad_pcb'),changed_net_layer_pairs=len(x),changed_nets=sorted({r['net'] for r in x}),copper_change_bounds_mm=[min(v[0] for v in bounds),min(v[1] for v in bounds),max(v[2] for v in bounds),max(v[3] for v in bounds)],length_and_via_changes=changes,strictly_connector_local=False,exceptions=['V5V2 converter-to-switch route replaced to recover the common-loop resistance target.','Positive copper widened in place, including segments beyond the two connector windows.','USB_DM_ESD and other collateral signal repairs extend outside the connector windows; see per-net bounds.'],no_placement_or_board_shape_exception=True))
