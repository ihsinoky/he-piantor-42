"""Deterministic 4nm outward quantization guard; no copper or routing edits."""
from common import *
import math,shutil,sexpdata as sx,collections
assert json.loads((E/'inspection/global/assessment.json').read_text())['pass_acceptance']
def children(n,k):return [x for x in n if isinstance(x,list) and x and str(x[0])==k]
changes=[]
for family,stem in [('inputs','main'),('runs','out')]:
 source=E/family/'global';dest=E/family/'final';dest.mkdir(exist_ok=False)
 tree=sx.loads((source/(stem+'.kicad_pcb')).read_text());rows=[]
 for z in children(tree,'zone'):
  if not children(z,'keepout'):continue
  name=children(z,'name')[0][1];i=int(name.rsplit(' ',1)[1])-1
  cx,cy=[(79,92),(121,81),(79,119),(102,111.5)][i]
  pts=children(children(z,'polygon')[0],'pts')[0]
  before=sx.dumps(z)
  for pt in children(pts,'xy'):
   dx,dy=float(pt[1])-cx,float(pt[2])-cy;r=math.hypot(dx,dy)
   pt[1]=round(cx+dx*(r+.000004)/r,6);pt[2]=round(cy+dy*(r+.000004)/r,6)
  rows.append(dict(name=name,before=before,after=sx.dumps(z)))
 assert len(rows)==4
 (dest/(stem+'.kicad_pcb')).write_text(sx.dumps(tree)+'\n')
 shutil.copyfile(E/'inputs/global/main.kicad_pro',dest/(stem+'.kicad_pro'))
 if family=='inputs':shutil.copyfile(source/'fp-lib-table',dest/'fp-lib-table')
 changes.append(dict(family=family,source_sha256=digest(source/(stem+'.kicad_pcb')),final_sha256=digest(dest/(stem+'.kicad_pcb')),zones=rows))
save(E/'reservation-quantization-guard.json',dict(utc=now(),reason='Strict ideal 5.0mm disk vs integer-coordinate original 256-sided reservation and filled plane showed ~1.45e-7 mm2 overlap. Fixed outward, not accepted by a relaxed tolerance.',radial_guard_mm=.000004,routing_reexecuted=False,copper_edits=False,changed_nodes='Only the four existing keepout polygons in input and corresponding raw output; all other AST nodes preserved.',changes=changes))
print('Four reservations expanded by 4nm radial quantization guard; no routing edits')
