"""Keep the source Fly length/endpoints; dress it clear of Rev.4 GH rises.
Standalone repair of generated assemblies is equivalent to build.py's final step.
"""
from geometry import *

def dressed(d):
 source=d['fly']['cable']['waypoints_mm'];start=source[0];end=source[-1]
 cy=d['fly']['transform']['translation_mm'][1]
 def pts(north):return [start,[0,cy+10,8.6],[-6,cy+17,8.6],[-6,-29.5,32.5],[-6,-18,32.5],[6,-18,32.5],[6,north,32.5],[-6,north,32.5],[-6,-29,32.5],[-3,-29,18.2],[-3,-5,18.2],[0,5,18.2],[0,14,12.6],end]
 north=-44-(170-rounded(pts(-44)).length)/2
 s,path=tube(pts(north),1)
 assert abs(path.length-170)<1e-8 and s.is_valid and len(s.solids())==1
 s.label='EZmate-170mm-route'
 return s,dict(connected_length_mm=path.length,diameter_mm=2,bend_radius_mm=5,waypoints_mm=pts(north),stored_z_mm=32.5,endpoints_unchanged=True,source_length_unchanged=True,reason='Avoid both Rev.4 GH rises at X±7,Y−16 and the retained rack column at X1,Y−14. Central loop elevated above GH service plane; Main approach X−3 clears the rack and both rises.')

def patch(pitch):
 out=HERE/f'{pitch}mm';baseline=json.loads((BASE/f'{pitch}mm/dimensions.json').read_text());s,data=dressed(baseline)
 source=import_step(out/'assembly.step')
 def replace(n):
  if n.label=='EZmate-170mm-route':return s
  if list(n.children):
   v=Compound(children=[replace(c) for c in list(n.children)]);v.label=n.label;return v
  n.parent=None;return n
 result=replace(source);export_step(result,out/'assembly.step');s.parent=None;export_step(s,out/'fly-harness-170mm.step')
 d=json.loads((out/'dimensions.json').read_text());d['fly_dressing']=data;save(out/'dimensions.json',d)
 print(pitch,'Fly re-dressed',data['connected_length_mm'],flush=True)
if __name__=='__main__':
 import sys
 patch(int(sys.argv[1]))
