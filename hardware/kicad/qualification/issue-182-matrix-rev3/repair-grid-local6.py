"""Bounded local copper repair. Candidate generator only; independent DRC,
physical graph, complete transfer comparison and all-via audit decide acceptance.
No pads, rules, zones or electrical configuration are modified.
"""
from common import *
import pcbnew as p
import numpy as np
import shapely as sh
from shapely.geometry import Point,LineString,box
from shapely.ops import unary_union
from shapely import affinity
import heapq,math,sys
src,out=map(Path,sys.argv[1:3]);b=p.LoadBoard(str(src));tick=time.monotonic();ledger=[]
mm=p.ToMM
xy=lambda v:(mm(v.x),mm(v.y))
V=lambda a:p.VECTOR2I(p.FromMM(float(a[0])),p.FromMM(float(a[1])))
def geom(q):
 if isinstance(q,p.PCB_VIA):return Point(xy(q.GetPosition())).buffer(mm(q.GetWidth(p.F_Cu))/2,quad_segs=32)
 if isinstance(q,p.PCB_TRACK):return LineString([xy(q.GetStart()),xy(q.GetEnd())]).buffer(mm(q.GetWidth())/2,quad_segs=32)
 x,y=xy(q.GetPosition());w,h=xy(q.GetSize());s=q.GetShape()
 if s==p.PAD_SHAPE_RECT:g=box(x-w/2,y-h/2,x+w/2,y+h/2)
 elif s==p.PAD_SHAPE_CIRCLE:g=Point(x,y).buffer(w/2,quad_segs=32)
 elif s==p.PAD_SHAPE_OVAL:g=LineString([(x-max(w-h,0)/2,y-max(h-w,0)/2),(x+max(w-h,0)/2,y+max(h-w,0)/2)]).buffer(min(w,h)/2,quad_segs=32)
 else:raise ValueError(s)
 return affinity.rotate(g,-q.GetOrientationDegrees(),origin=(x,y))
def items():
 return [dict(obj=q,g=geom(q),net=q.GetNetname(),layers=[i for i,l in enumerate([p.F_Cu,p.B_Cu]) if q.IsOnLayer(l)],pad=isinstance(q,p.PAD),via=isinstance(q,p.PCB_VIA)) for q in list(b.GetTracks())+[q for f in b.GetFootprints() for q in f.Pads() if q.GetAttribute()!=p.PAD_ATTRIB_NPTH]]
# First candidate uses GLOBAL-02. Remove just the single prohibited via and widen
# the one undersized power segment; all changed routes will be requalified.
for t in list(b.GetTracks()):
 if isinstance(t,p.PCB_VIA) and t.m_Uuid.AsString()=='64129d2f-40a4-4053-8481-dae9fd46ee28':ledger.append(dict(remove_via=t.m_Uuid.AsString()));b.RemoveNative(t)
 elif t.m_Uuid.AsString() in ['34c7da87-eb3a-4959-983d-0e5eba1f6530','aa8ef9e6-e6d3-429e-96e8-ca8d89333771','b41328b1-5fa1-4a2a-a126-ba93a120c995','f682e9a3-4b91-4fee-b8f1-84a6b2d141fb','fe631775-132d-4f9a-994d-795cc2da99f6','db588e12-1adb-4a8d-ab5d-c813e6116b72']:
  ledger.append(dict(remove_blocker=t.m_Uuid.AsString(),net=t.GetNetname()));b.RemoveNative(t)
 elif not isinstance(t,p.PCB_VIA) and t.GetNetname() in ['GND','HALL_5V'] and mm(t.GetWidth())<.3:t.SetWidth(p.FromMM(.3));ledger.append(dict(widen=t.m_Uuid.AsString(),width_mm=.3))
npth=[Point(xy(q.GetPosition())).buffer(2.5,quad_segs=48) for f in b.GetFootprints() for q in f.Pads() if q.GetAttribute()==p.PAD_ATTRIB_NPTH]
def components(rows,net):
 a=[r for r in rows if r['net']==net];par=list(range(len(a)))
 def find(i):
  while par[i]!=i:par[i]=par[par[i]];i=par[i]
  return i
 tree=sh.STRtree([r['g'] for r in a])
 for i,r in enumerate(a):
  for j in tree.query(r['g'],predicate='intersects'):
   if j<i and set(r['layers'])&set(a[j]['layers']):par[find(i)]=find(j)
 groups={}
 for i,r in enumerate(a):groups.setdefault(find(i),[]).append(r)
 return sorted(groups.values(),key=lambda g:(sum(r['pad'] for r in g),len(g)),reverse=True)
def route(rows,net,startgroup,goalgroup,margin,step=.05):
 width=.3 if net in ['GND','HALL_5V'] else .1
 a=unary_union([r['g'] for r in startgroup]);z=unary_union([r['g'] for r in goalgroup]);ax,ay,bx,by=a.union(z).bounds
 # Bounded spatial window, not a new global routing attempt.
 xmin=max(36.4,math.floor((ax-margin)/step)*step);ymin=max(60.4,math.floor((ay-margin)/step)*step)
 xmax=min(163.6,bx+margin);ymax=min(139.6,by+margin)
 xs=np.arange(xmin,xmax+step/2,step);ys=np.arange(ymin,ymax+step/2,step);X,Y=np.meshgrid(xs,ys);h,w=X.shape
 blocked=[];goals=[];starts=[]
 foreign=[r for r in rows if r['net']!=net]
 for l in [0,1]:
  obs=unary_union([r['g'] for r in foreign if l in r['layers']]+npth).buffer(.1+width/2+.003,quad_segs=24)
  blocked.append(sh.contains_xy(obs,X,Y))
  g=unary_union([r['g'] for r in goalgroup if l in r['layers']]).buffer(width/2-.008)
  goals.append(sh.contains_xy(g,X,Y)&~blocked[-1])
  g=unary_union([r['g'] for r in startgroup if l in r['layers']]).buffer(max(width/2-.008,.001))
  starts.append(sh.contains_xy(g,X,Y)&~blocked[-1])
 padobs=unary_union([r['g'].buffer(.403,quad_segs=24) for r in rows if r['pad']]+[g.buffer(.303) for g in npth])
 viaobs=unary_union([padobs]+[r['g'].buffer(.403,quad_segs=24) for r in foreign]+[r['g'].buffer(.203,quad_segs=24) for r in rows if r['via']])
 viabad=sh.contains_xy(viaobs,X,Y)|blocked[0]|blocked[1]
 # Reserve the middle fanout site for MUX_A2; A1 must exit above or left.
 if net=='MUX_A1':viabad|=(X>119)&(X<125)&(Y>119.2)&(Y<123)
 B=np.array(blocked).reshape(-1);G=np.array(goals).reshape(-1);S=np.flatnonzero(np.array(starts).reshape(-1));size=h*w
 print('search',net,'start cells',len(S),'goal cells',int(G.sum()),'grid',h,w,flush=True)
 if not len(S) or not G.any():return None
 goalcoords=np.argwhere(np.array(goals));gmin=goalcoords[:,1:].min(axis=0);gmax=goalcoords[:,1:].max(axis=0)
 def heuristic(n):
  j,i=divmod(n%size,w);return (max(int(gmin[0])-j,0,j-int(gmax[0]))+max(int(gmin[1])-i,0,i-int(gmax[1])))*.707
 distance={int(n):0. for n in S};parent={int(n):-1 for n in S};queue=[(heuristic(int(n)),0.,int(n)) for n in S];heapq.heapify(queue);end=None;count=0
 while queue:
  _,cost,n=heapq.heappop(queue)
  if cost!=distance[n]:continue
  if G[n]:end=n;break
  count+=1
  if count>1200000 or time.monotonic()-tick>1700:return None
  l=n//size;j,i=divmod(n%size,w)
  ns=[]
  for dj,di in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
   jj,ii=j+dj,i+di
   if 0<=jj<h and 0<=ii<w:
    nn=l*size+jj*w+ii
    if not B[nn] and (not dj or not di or not B[l*size+j*w+ii] and not B[l*size+jj*w+i]):ns.append((nn,1.41421356237 if dj and di else 1.))
  if not viabad[j,i]:ns.append(((1-l)*size+j*w+i,20.))
  for nn,d in ns:
   nc=cost+d
   if nc<distance.get(nn,math.inf):distance[nn]=nc;parent[nn]=n;heapq.heappush(queue,(nc+heuristic(nn),nc,nn))
 if end is None:
  print('no path',net,'expanded',count,flush=True);return None
 path=[]
 while end!=-1:
  l=end//size;j,i=divmod(end%size,w);path.append((l,(float(xs[i]),float(ys[j]))));end=parent[end]
 path.reverse();print('path',net,len(path),'expanded',count,'margin',margin,flush=True)
 return path
for net in ['GND','MUX_A1','MUX_A2','MUX_OUT_A','HALL_5V']:
 for attempt in range(8):
  rows=items();groups=components(rows,net);required=[g for g in groups if any(r['pad'] for r in g)]
  print(net,'groups',[(len(g),sum(r['pad'] for r in g)) for g in groups],flush=True)
  if len(groups)==1:break
  goal=groups[0];start=groups[-1];path=None
  for margin in [3,8,15]:
   path=route(rows,net,start,goal,margin)
   if path:break
  if path is None:ledger.append(dict(net=net,failed=True));break
  netcode=start[0]['obj'].GetNetCode();width=.3 if net in ['GND','HALL_5V'] else .1
  # Compress only collinear grid steps; never simplify across obstacles.
  piv=[path[0]]
  for i in range(1,len(path)-1):
   a,z,q=path[i-1:i+2]
   if a[0]!=z[0] or z[0]!=q[0] or abs((z[1][0]-a[1][0])*(q[1][1]-z[1][1])-(z[1][1]-a[1][1])*(q[1][0]-z[1][0]))>1e-8:piv.append(z)
  piv.append(path[-1]);new=[]
  for a,z in zip(piv,piv[1:]):
   if a[0]!=z[0]:
    t=p.PCB_VIA(b);t.SetPosition(V(a[1]));t.SetWidth(p.FromMM(.6));t.SetDrill(p.FromMM(.3));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu)
   else:
    if a[1]==z[1]:continue
    t=p.PCB_TRACK(b);t.SetStart(V(a[1]));t.SetEnd(V(z[1]));t.SetLayer([p.F_Cu,p.B_Cu][a[0]]);t.SetWidth(p.FromMM(width))
   t.SetNetCode(netcode);b.Add(t);new.append(t.m_Uuid.AsString())
  ledger.append(dict(net=net,window_margin_mm=margin,grid_step_mm=.05,added_items=new,path=piv))
  p.SaveBoard(str(out),b)
out.parent.mkdir(parents=True,exist_ok=True);p.SaveBoard(str(out),b)
save(out.with_suffix('.grid-repair.json'),dict(utc=now(),source_sha256=digest(src),output_sha256=digest(out),elapsed_seconds=time.monotonic()-tick,time_bound_seconds=1800,ledger=ledger))
