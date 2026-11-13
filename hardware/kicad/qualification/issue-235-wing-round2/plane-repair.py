"""Join required physical copper components using exact filled-plane sources.
Automatic A* only; every candidate is qualified independently afterwards.
"""
from pathlib import Path
import collections,json,sys,subprocess,os
import numpy as np
import shapely
from shapely.geometry import Point,LineString
from shapely.ops import unary_union
import pcbnew as p
from verify import xy,polys,padgeom
E=Path(__file__).resolve().parent;T=E.parents[3]/'.issue235-runtime';V=lambda a:p.VECTOR2I(round(a[0]*1e6),round(a[1]*1e6))

def components(b,net,prune=False,skip_uuid=None):
 es=[]
 for f in b.GetFootprints():
  for a in f.Pads():
   if a.GetAttribute()==p.PAD_ATTRIB_NPTH or a.GetNetname()!=net:continue
   es.append((unary_union([padgeom(a,l) for l in (p.F_Cu,p.B_Cu) if a.IsOnLayer(l)]),set(l for l in (p.F_Cu,p.B_Cu) if a.IsOnLayer(l)),True,None))
 for t in b.GetTracks():
  if t.GetNetname()!=net:continue
  if t.m_Uuid.AsString()==skip_uuid:continue
  if isinstance(t,p.PCB_VIA):g=Point(xy(t.GetPosition())).buffer(.3).difference(Point(xy(t.GetPosition())).buffer(.15));ls={p.F_Cu,p.B_Cu}
  else:g=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2);ls={t.GetLayer()}
  es.append((g,ls,False,t))
 for z in b.Zones():
  if z.GetIsRuleArea() or z.GetNetname()!=net:continue
  for l in (p.F_Cu,p.B_Cu):
   if not z.IsOnLayer(l):continue
   g=polys(z.GetFilledPolysList(l))
   for part in g.geoms if hasattr(g,'geoms') else [g]:
    if not part.is_empty:es.append((part,{l},False,None))
 tree=shapely.STRtree([e[0] for e in es]);parent=list(range(len(es)))
 def find(i):
  while i!=parent[i]:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for i,(g,ls,_,item) in enumerate(es):
  for jj in tree.query(g,predicate='intersects'):
   j=int(jj)
   if j<i and ls&es[j][1]:parent[find(i)]=find(j)
 groups=collections.defaultdict(list)
 for i,a in enumerate(es):groups[find(i)].append(a)
 # Retain largest region even if currently missing a direct pad anchor.
 gs=sorted(groups.values(),key=lambda g:-sum(a[0].area for a in g))
 if prune:
  for group in gs:
   if not any(a[2] for a in group):
    for a in group:
     if a[3] is not None:b.Delete(a[3])
 return [g for g in gs if any(a[2] for a in g)]

def repair(w):
 src=w/'main.kicad_pcb'
 if False:
  subprocess.run([sys.executable,str(E/'escape-service-power.py'),w.name],check=True)
 if w.name=='wing-rev3-17mm-right' and not (w/'ground-rescue-complete.json').exists():
  subprocess.run([sys.executable,str(E/'escape-ground-to-plane.py'),w.name],check=True)
 b=p.LoadBoard(str(src));manager=p.GetSettingsManager();manager.LoadProject(str(w/'input.kicad_pro'));b.SetProject(manager.Prj())
 # Keep dangling tracks: their middle may carry a required T-junction.
 # cleanup.py trims free tails after connectivity has been restored.
 drc=json.loads((w/'drc.json').read_text());dangling=set()
 tracks_by_id={t.m_Uuid.AsString():t for t in b.GetTracks()}
 for q in drc['violations']:
  if q['type']=='items_not_allowed':
   dangling.update(a['uuid'] for a in q['items'] if a['uuid'] in tracks_by_id)
  if q['type']!='clearance':continue
  candidates=[tracks_by_id[a['uuid']] for a in q['items'] if a['uuid'] in tracks_by_id and not isinstance(tracks_by_id[a['uuid']],p.PCB_VIA) and tracks_by_id[a['uuid']].GetNetname() in ('HALL_5V','GND')]
  if candidates:
   candidates.sort(key=lambda t:t.GetNetname()!='HALL_5V');dangling.add(candidates[0].m_Uuid.AsString())
 for t in list(b.GetTracks()):
  if t.m_Uuid.AsString() in dangling:b.Delete(t)
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity()
 pads=[a for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute()!=p.PAD_ATTRIB_NPTH];holes=[a for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute()==p.PAD_ATTRIB_NPTH]
 outline=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(outline);board=polys(outline);x0,y0,x1,y1=board.bounds;step=float(os.environ.get('WING_ROUTE_STEP','.05'))
 if w.name=='wing-rev3-17mm-right':
  # A 0.1mm grid aliases the rotated 0.65mm-pitch service escape channels.
  # Include a 2mm halo around rebuild-service-escapes.py's cut window.
  # Without it, clipped track endpoints just outside the cut can have no
  # usable source cell (or a boundary dead end), despite open interior space.
  # Refine only this north window; no fabrication dimension is relaxed.
  step=.025;x0=max(x0,48.);y0=max(y0,13.);x1=min(x1,112.);y1=min(y1,70.)
 if os.environ.get('WING_ROUTE_BOX'):
  ax,ay,bx,by=map(float,os.environ['WING_ROUTE_BOX'].split(','));x0=max(x0,ax);y0=max(y0,ay);x1=min(x1,bx);y1=min(y1,by)
 nx=round((x1-x0)/step)+1;ny=round((y1-y0)/step)+1;xx,yy=np.meshgrid(x0+np.arange(nx)*step,y0+np.arange(ny)*step);xx=xx.ravel();yy=yy.ravel();points=shapely.points(xx,yy);n=len(points);layers=[p.F_Cu,p.B_Cu]
 fixed=unary_union([Point(xy(a.GetPosition())).buffer(p.ToMM(a.GetDrillSize().x)/2+.25) for a in holes]+[polys(z.Outline()) for z in b.Zones() if z.GetIsRuleArea()]);allpads=unary_union([padgeom(a,l) for a in pads for l in layers if a.IsOnLayer(l)])
 nets=[str(n) for n in b.GetNetsByName() if str(n)];nets.sort(key=lambda net:(net in ('HALL_5V','GND'),net));records=[]
 for net in nets:components(b,net,prune=True)
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity()
 for net in nets:
  cached=None;consecutive_rips=0
  for attempt in range(40):
   gs=components(b,net)
   if len(gs)<=1:break
   source=gs[0];target=gs[1];width=.3 if net in ('HALL_5V','GND') else .1
   if cached is None:
    foreign={l:[] for l in layers};native={l:[] for l in layers}
    for a in pads:
     if a.GetNetname()==net:continue
     for l in layers:
      if a.IsOnLayer(l):foreign[l].append(padgeom(a,l));native[l].append(a.GetEffectiveShape(l))
    for t in b.GetTracks():
     if t.GetNetname()==net:continue
     if isinstance(t,p.PCB_VIA):geom=Point(xy(t.GetPosition())).buffer(.3);ls=layers
     else:geom=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2);ls=[t.GetLayer()]
     for l in ls:foreign[l].append(geom);native[l].append(t.GetEffectiveShape(l))
    unions={l:unary_union(foreign[l]) for l in layers};blocked=[]
    for l in layers:
     obs=unions[l].buffer(width/2+.110001).union(fixed.buffer(width/2+.002));inside=board.buffer(-.3-width/2-.002);shapely.prepare(obs);shapely.prepare(inside);blocked.append(shapely.intersects(obs,points)|~shapely.contains(inside,points))
    obs=unary_union([unions[l].buffer(.410001) for l in layers]+[allpads.buffer(.435001),fixed.buffer(.302)]);inside=board.buffer(-.602);shapely.prepare(obs);shapely.prepare(inside);via=shapely.intersects(obs,points)|~shapely.contains(inside,points)
    cached=(blocked,via,native)
   else:blocked,via,native=cached
   masks=[]
   for group in (source,target):
    ms=[]
    for l in layers:
     g=unary_union([a[0] for a in group if l in a[1]]);shapely.prepare(g);ms.append(shapely.intersects(g,points))
    masks.append(np.concatenate(ms).astype(np.uint8))
   binary=T/(w.name+'-plane-grid.bin');output=T/(w.name+'-plane-path.bin');binary.write_bytes(np.array([nx,ny],dtype=np.int32).tobytes()+np.concatenate(blocked).astype(np.uint8).tobytes()+via.astype(np.uint8).tobytes()+masks[0].tobytes()+masks[1].tobytes())
   rc=subprocess.run([str(T/'grid-search'),str(binary),str(output)]).returncode
   displaced=[]
   if rc and w.name=='wing-rev3-17mm-right':
    # A shortest hard-obstacle route can be fenced in by previously routed
    # signals. Find the least copper displacement instead of ripping a broad
    # radial corridor. Pads, vias, pad fanouts and every mechanical exclusion
    # remain hard obstacles; only other track interiors are soft obstacles.
    hard={l:[] for l in layers};soft={l:[] for l in layers};removable=[]
    for pad in pads:
     if pad.GetNetname()!=net:
      for l in layers:
       if pad.IsOnLayer(l):hard[l].append(padgeom(pad,l))
    for track in b.GetTracks():
     if track.GetNetname()==net:continue
     if isinstance(track,p.PCB_VIA):
      disk=Point(xy(track.GetPosition())).buffer(.3)
      for l in layers:hard[l].append(disk)
     else:
      l=track.GetLayer();g=LineString([xy(track.GetStart()),xy(track.GetEnd())]).buffer(p.ToMM(track.GetWidth())/2)
      fanout=any(pad.GetNetname()==track.GetNetname() and pad.IsOnLayer(l) and (pad.GetEffectiveShape(l).Collide(track.GetStart()) or pad.GetEffectiveShape(l).Collide(track.GetEnd())) for pad in pads)
      if fanout:hard[l].append(g)
      else:soft[l].append(g);removable.append(track)
    weighted=[]
    for l in layers:
     obstacle=unary_union(hard[l]).buffer(width/2+.110001).union(fixed.buffer(width/2+.002));inside=board.buffer(-.3-width/2-.002)
     mobile=unary_union(soft[l]).buffer(width/2+.110001)
     shapely.prepare(obstacle);shapely.prepare(inside);shapely.prepare(mobile)
     mask=np.where(shapely.intersects(mobile,points),2,0).astype(np.uint8)
     mask[shapely.intersects(obstacle,points)|~shapely.contains(inside,points)]=1;weighted.append(mask)
    binary.write_bytes(np.array([nx,ny],dtype=np.int32).tobytes()+np.concatenate(weighted).tobytes()+via.astype(np.uint8).tobytes()+masks[0].tobytes()+masks[1].tobytes())
    rc=subprocess.run([str(T/'grid-search'),str(binary),str(output)]).returncode
    if not rc:
     raw=np.frombuffer(output.read_bytes(),dtype=np.int32);corridors={l:[] for l in layers}
     for ai,zi in zip(raw,raw[1:]):
      a,z=int(ai),int(zi)
      if a//n==z//n:corridors[layers[a//n]].append(LineString([(xx[a%n],yy[a%n]),(xx[z%n],yy[z%n])]))
     corridors={l:unary_union(lines).buffer(width/2+.110002) for l,lines in corridors.items()}
     for track in removable:
      line=LineString([xy(track.GetStart()),xy(track.GetEnd())]);clip=corridors[track.GetLayer()].buffer(p.ToMM(track.GetWidth())/2+.000002)
      if not line.intersects(clip):continue
      outside=line.difference(clip)
      for piece in getattr(outside,'geoms',[outside]):
       if piece.is_empty or piece.length<.001:continue
       copy=p.PCB_TRACK(b);copy.SetStart(V(piece.coords[0]));copy.SetEnd(V(piece.coords[-1]));copy.SetLayer(track.GetLayer());copy.SetWidth(track.GetWidth());copy.SetNetCode(track.GetNetCode());b.Add(copy)
      displaced.append(dict(uuid=track.m_Uuid.AsString(),net=track.GetNetname()));b.Delete(track)
     records.append(dict(weighted_displacement_for=net,tracks=displaced));cached=None
     native={l:[pad.GetEffectiveShape(l) for pad in pads if pad.GetNetname()!=net and pad.IsOnLayer(l)]+[track.GetEffectiveShape(l) for track in b.GetTracks() if track.GetNetname()!=net and track.IsOnLayer(l)] for l in layers}
     print(w.name,net,'weighted displacement',len(displaced),'tracks',flush=True)
   if rc:
    # Unbox a fixed top-side service pad by cutting only the blocking copper.
    # Preserve the outside ends; the broken net is reconnected in a later pass.
    from shapely.geometry import box
    ripped=[]
    if consecutive_rips<int(os.environ.get('WING_ROUTE_MAX_RIPS','0')):
     for f in b.GetFootprints():
      for pad in f.Pads():
       if pad.GetNetname()!=net:continue
       padlayer=p.F_Cu if pad.IsOnLayer(p.F_Cu) else p.B_Cu
       pg=padgeom(pad,padlayer)
       if not any(pg.intersects(a[0]) and padlayer in a[1] for a in target):continue
       origin=xy(pad.GetPosition());center=xy(f.GetPosition());direction=1 if origin[0]>=center[0] else -1
       dx=origin[0]-center[0];dy=origin[1]-center[1]
       if f.GetReference().startswith('J_'):dx,dy=0,1
       length=(dx*dx+dy*dy)**.5
       if length<.0001:dx,dy,length=1,0,1
       reach=max(p.ToMM(pad.GetSize().x),p.ToMM(pad.GetSize().y))/2+1.0
       end=[origin[0]+dx/length*reach,origin[1]+dy/length*reach]
       corridor=LineString([origin,end]).buffer(width/2+.11)
       for track in list(b.GetTracks()):
        if track.GetNetname()==net:continue
        if isinstance(track,p.PCB_VIA):
         if Point(xy(track.GetPosition())).distance(corridor)<.7:
          ripped.append(dict(net=track.GetNetname(),uuid=track.m_Uuid.AsString(),kind='via',for_net=net,pad=f.GetReference()+'.'+pad.GetNumber()));b.Delete(track)
         continue
        g=LineString([xy(track.GetStart()),xy(track.GetEnd())])
        cutshape=corridor if track.GetLayer()==padlayer else Point(end).buffer(1.8)
        if g.distance(cutshape)>p.ToMM(track.GetWidth())/2:continue
        clip=cutshape.buffer(p.ToMM(track.GetWidth())/2+.05)
        outside=g.difference(clip)
        for line in outside.geoms if hasattr(outside,'geoms') else [outside]:
         if line.is_empty or line.length<.001:continue
         other=p.PCB_TRACK(b);other.SetStart(V(line.coords[0]));other.SetEnd(V(line.coords[-1]));other.SetWidth(track.GetWidth());other.SetLayer(track.GetLayer());other.SetNetCode(track.GetNetCode());b.Add(other)
        ripped.append(dict(net=track.GetNetname(),uuid=track.m_Uuid.AsString(),for_net=net,pad=f.GetReference()+'.'+pad.GetNumber()));b.Delete(track)
       if ripped:break
      if ripped:break
    if ripped:
     cached=None;consecutive_rips+=1;records.append(dict(local_rips=ripped));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();print(w.name,net,'ripped',len(ripped),'blocker pieces',flush=True);continue
    print(w.name,net,'NO PATH',len(gs),flush=True);break
   path=np.frombuffer(output.read_bytes(),dtype=np.int32);nodes=[int(path[0])]
   for i in range(1,len(path)-1):
    if path[i]-path[i-1]!=path[i+1]-path[i]:nodes.append(int(path[i]))
   nodes.append(int(path[-1]));new=[]
   def pos(i):return [float(xx[i%n]),float(yy[i%n])]
   for a,z in zip(nodes,nodes[1:]):
    if a//n!=z//n:
     item=p.PCB_VIA(b);item.SetPosition(V(pos(a)));item.SetWidth(600000);item.SetDrill(300000);item.SetViaType(p.VIATYPE_THROUGH);item.SetLayerPair(p.F_Cu,p.B_Cu)
    else:
     item=p.PCB_TRACK(b);item.SetStart(V(pos(a)));item.SetEnd(V(pos(z)));item.SetWidth(p.FromMM(width));item.SetLayer(layers[a//n]);shape=item.GetEffectiveShape(item.GetLayer());assert not any(s.Collide(shape,99999) for s in native[item.GetLayer()]),'native clearance rejected grid path'
    item.SetNetCode(b.FindNet(net).GetNetCode());new.append(item)
   for item in new:b.Add(item)
   b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity()
   p.SaveBoard(str(w/'main.kicad_pcb'),b)
   consecutive_rips=0;after=len(components(b,net));records.append(dict(net=net,width_mm=width,before=len(gs),after=after,segments=len(new),path=[dict(position_mm=pos(q),layer=b.GetLayerName(layers[q//n])) for q in nodes]));print(w.name,net,len(gs),'->',after,flush=True)
   if after>=len(gs):break
 assert p.SaveBoard(str(w/'main.kicad_pcb'),b)
 history=json.loads((w/'plane-repairs.json').read_text()) if (w/'plane-repairs.json').exists() else [];history.append(dict(grid_step_mm=step,search_bbox_mm=[x0,y0,x1,y1],removed_dangling=list(dangling),paths=records));(w/'plane-repairs.json').write_text(json.dumps(history,indent=2)+'\n')
if __name__=='__main__':
 for name in sys.argv[1:]:repair(E/name)
