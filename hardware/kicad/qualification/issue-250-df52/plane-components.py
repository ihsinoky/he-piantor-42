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
def components(b,net,prune=False,skip_uuid=None):
 es=[]
 for f in b.GetFootprints():
  for a in f.Pads():
   if a.GetAttribute()==p.PAD_ATTRIB_NPTH or a.GetNetname()!=net:continue
   es.append((unary_union([padgeom(a,l) for l in list(b.GetEnabledLayers().CuStack()) if a.IsOnLayer(l)]),set(l for l in list(b.GetEnabledLayers().CuStack()) if a.IsOnLayer(l)),True,None))
 for t in b.GetTracks():
  if t.GetNetname()!=net:continue
  if t.m_Uuid.AsString()==skip_uuid:continue
  if isinstance(t,p.PCB_VIA):g=Point(xy(t.GetPosition())).buffer(.3).difference(Point(xy(t.GetPosition())).buffer(.15));ls=set(b.GetEnabledLayers().CuStack())
  else:g=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2);ls={t.GetLayer()}
  es.append((g,ls,False,t))
 for z in b.Zones():
  if z.GetIsRuleArea() or z.GetNetname()!=net:continue
  for l in list(b.GetEnabledLayers().CuStack()):
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
