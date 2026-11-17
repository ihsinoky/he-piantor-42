"""Main Rev.8 follow-up (PO option (a), Issue #263 REPORT 3.3):
Rev.7 outline extended with tabs under both ZIFs so all pads +
courtyard sit on-board with >=0.20 mm copper-to-edge clearance
(design target: rule 0.20 + 0.20 margin for pads; courtyard +0.10).
Poses, assignment (pad n <- signal 15-n) and copper-strip logic are
identical to build-main.py. Tab parameters are computed from the
built pad bounding boxes + footprint courtyard against the slanted
edge lines and recorded in outline-extension.json.
"""
from pathlib import Path
import pcbnew as p, json, math, shutil
import numpy as np
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
E=Path(__file__).resolve().parent; BASE=E.parent/'issue-240-main-rev7'
FP='Hirose_FH12-14S-0.5SH_1x14-1MP_P0.50mm_Horizontal'
W=E/'main-rev8'; W.mkdir(exist_ok=True)
b=p.LoadBoard(str(BASE/'inspection/final/main.kicad_pcb'))

def mm(v): return p.ToMM(v)
# --- original outline polygon from Edge.Cuts segments
segs=[]
for d in b.GetDrawings():
 if d.GetLayer()==p.Edge_Cuts:
  segs.append(((mm(d.GetStart().x),mm(d.GetStart().y)),(mm(d.GetEnd().x),mm(d.GetEnd().y))))
pts=[segs[0][0],segs[0][1]]; used={0}
while len(used)<len(segs):
 for i,s in enumerate(segs):
  if i in used: continue
  if s[0]==pts[-1]: pts.append(s[1]); used.add(i)
  elif s[1]==pts[-1]: pts.append(s[0]); used.add(i)
outline=Polygon(pts)
# two slanted edges = the two longest segments; west = smaller mid-x
slanted=[s for s in segs if abs(s[1][1]-s[0][1])>10]
edges={}
for s in slanted:
 mid=((s[0][0]+s[1][0])/2,(s[0][1]+s[1][1])/2)
 edges['west' if mid[0]<100 else 'east']=s
cent=np.array([outline.centroid.x,outline.centroid.y])
edgeinfo={}
for name,s in edges.items():
 A=np.array(s[0]); Bv=np.array(s[1]); u=(Bv-A)/np.linalg.norm(Bv-A)
 n=np.array([u[1],-u[0]])
 if np.dot(n,cent-A)>0: n=-n  # outward = away from centroid
 edgeinfo[name]=dict(A=A,u=u,n=n)

spec={'J2':dict(centre=(76.91,110.97),yaw=38.0,edge='west'),'J3':dict(centre=(123.30,110.80),yaw=-43.0,edge='east')}
olds={}; oldfps={}
for f in b.GetFootprints():
 if f.GetReference() in spec:
  oldfps[f.GetReference()]=f
  olds[f.GetReference()]={a.GetNumber():a.GetNetCode() for a in f.Pads() if a.GetNumber() not in ('MP','15')}
  olds[f.GetReference()+'_names']={a.GetNetCode():a.GetNetname() for a in f.Pads() if a.GetNumber() not in ('MP','15')}
newfps={}
for ref in spec:
 f=p.FootprintLoad(str(E/'connector'),FP); assert f
 b.Add(f); newfps[ref]=f
info={}
for ref,s in spec.items():
 f=newfps[ref]; th=math.radians(s['yaw'])
 ox=s['centre'][0]-1.40*math.sin(th); oy=s['centre'][1]+1.40*math.cos(th)
 f.SetReference(ref); f.SetValue('FH12-14S-0.5SH(55)')
 f.SetPosition(p.VECTOR2I(round(ox*1e6),round(oy*1e6))); f.SetOrientationDegrees(s['yaw'])
 assign={}
 for a in f.Pads():
  if a.GetNumber()=='MP': a.SetNetCode(0)
  else:
   sig=str(15-int(a.GetNumber())); a.SetNetCode(olds[ref][sig]); assign[a.GetNumber()]=olds[ref+'_names'][olds[ref][sig]]
 info[ref]=dict(origin_mm=[ox,oy],yaw_deg=s['yaw'],envelope_centre_board_mm=list(s['centre']),assignment_pad_to_net=assign)

# --- tab design per site
tabs={}; tabpolys=[]
for ref,s in spec.items():
 f=newfps[ref]; ei=edgeinfo[s['edge']]; A,u,n=ei['A'],ei['u'],ei['n']
 padpts=[]
 for a in f.Pads():
  bb=a.GetBoundingBox()
  for cx,cy in [(bb.GetLeft(),bb.GetTop()),(bb.GetRight(),bb.GetTop()),(bb.GetLeft(),bb.GetBottom()),(bb.GetRight(),bb.GetBottom())]:
   padpts.append(np.array([mm(cx),mm(cy)]))
 cy=f.GetCourtyard(p.F_Cu); cypts=[]
 for chain in range(cy.OutlineCount()):
  o=cy.Outline(chain)
  for i in range(o.PointCount()):
   pt=o.GetPoint(i); cypts.append(np.array([mm(pt.x),mm(pt.y)]))
 def tn(P):
  rel=P-A; return float(rel@u), float(rel@n)
 pad_tn=[tn(q) for q in padpts]; cy_tn=[tn(q) for q in cypts]
 d_pad=max(d for t,d in pad_tn)+0.20+0.20   # rule + margin
 d_cy=max(d for t,d in cy_tn)+0.10
 depth=max(d_pad,d_cy)
 tall=[t for t,d in pad_tn]+[t for t,d in cy_tn]
 t0,t1=min(tall)-2.0,max(tall)+2.0
 c=[A+u*t0+n*(-1.0),A+u*t1+n*(-1.0),A+u*t1+n*depth,A+u*t0+n*depth]
 tabpolys.append(Polygon([tuple(q) for q in c]))
 tabs[ref]=dict(edge=s['edge'],depth_mm=round(depth,3),d_pad_req_mm=round(d_pad,3),d_courtyard_req_mm=round(d_cy,3),t_range_mm=[round(t0,3),round(t1,3)],corners=[[round(float(q[0]),3),round(float(q[1]),3)] for q in c])
newoutline=unary_union([outline]+tabpolys)
assert newoutline.geom_type=='Polygon', newoutline.geom_type
coords=list(newoutline.exterior.coords)
# verify: every pad bbox corner >=0.20 from new outline exterior
worst=1e9; worstid=None
for ref,s in spec.items():
 for a in newfps[ref].Pads():
  bb=a.GetBoundingBox()
  for cx,cy in [(bb.GetLeft(),bb.GetTop()),(bb.GetRight(),bb.GetTop()),(bb.GetLeft(),bb.GetBottom()),(bb.GetRight(),bb.GetBottom())]:
   d=newoutline.exterior.distance(Point(mm(cx),mm(cy)))
   if d<worst: worst,worstid=d,f"{ref}.{a.GetNumber()}"
print('new outline vertices:',len(coords)-1,'worst pad-corner clearance:',round(worst,3),'at',worstid)
assert worst>=0.20-1e-9
# replace Edge.Cuts
for d in list(b.GetDrawings()):
 if d.GetLayer()==p.Edge_Cuts: b.Remove(d)
for i in range(len(coords)-1):
 sh=p.PCB_SHAPE(b); sh.SetShape(p.SHAPE_T_SEGMENT)
 sh.SetStart(p.VECTOR2I(round(coords[i][0]*1e6),round(coords[i][1]*1e6)))
 sh.SetEnd(p.VECTOR2I(round(coords[i+1][0]*1e6),round(coords[i+1][1]*1e6)))
 sh.SetLayer(p.Edge_Cuts); sh.SetWidth(0); b.Add(sh)
(W/'outline-extension.json').write_text(json.dumps(dict(tabs=tabs,worst_pad_corner_clearance_mm=round(worst,4),worst_at=worstid,new_outline_area_mm2=round(newoutline.area,2),old_outline_area_mm2=round(outline.area,2)),indent=2)+'\n')

# --- copper strip (identical to build-main.py)
from shapely.geometry import box as sbox, LineString as SLine, Point as SPoint
padpolys=[]
for ref in ('J2','J3'):
 f=[x for x in b.GetFootprints() if x.GetReference()==ref][0]
 for a in f.Pads():
  padpolys.append(sbox(mm(a.GetPosition().x)-mm(a.GetSize().x)/2-.10,mm(a.GetPosition().y)-mm(a.GetSize().y)/2-.10,mm(a.GetPosition().x)+mm(a.GetSize().x)/2+.10,mm(a.GetPosition().y)+mm(a.GetSize().y)/2+.10))
collided=[]
for t in list(b.GetTracks()):
 if isinstance(t,p.PCB_VIA): g=SPoint(mm(t.GetPosition().x),mm(t.GetPosition().y)).buffer(mm(t.GetWidth(p.F_Cu))/2)
 else: g=SLine([(mm(t.GetStart().x),mm(t.GetStart().y)),(mm(t.GetEnd().x),mm(t.GetEnd().y))]).buffer(mm(t.GetWidth())/2,cap_style=1)
 if any(g.intersects(pp) for pp in padpolys): collided.append(t)
for t in collided: b.Remove(t)
print('removed colliding kept copper:',len(collided))
removed=0; netcodes=set()
for ref in spec: netcodes|=set(olds[ref].values())
for t in list(b.GetTracks()):
 if t.GetNetCode() not in netcodes: continue
 s2,e2=t.GetStart(),t.GetEnd()
 near=False
 for ref,sp in spec.items():
  cx,cy=sp['centre']
  if max(abs(mm(s2.x)-cx),abs(mm(s2.y)-cy))<22 and max(abs(mm(e2.x)-cx),abs(mm(e2.y)-cy))<22: near=True
 if near: b.Remove(t); removed+=1
for f in oldfps.values(): b.Remove(f)
p.SaveBoard(str(W/'input.kicad_pcb'),b)
src=BASE/'schematic/main.kicad_sch'
if src.exists(): shutil.copyfile(src,W/'main.kicad_sch')
(W/'swap.json').write_text(json.dumps(dict(removed_local_tracks=removed,sites=info),indent=2)+'\n')
print('main-rev8 extended-outline input built; removed',removed)
