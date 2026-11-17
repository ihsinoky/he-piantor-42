"""Wing Rev.5: swap Rev.4's GH connector for the FH12 ZIF at the same site.

Base = qualified routed Rev.4 board (issue-235 tree). Local fanout of the
14 connector nets inside an 18 mm box is removed; KRT re-routes it.
Pin assignment: pad k keeps Rev.4's net for D-024 signal k (Wing side
keeps the arriving-order assignment per #261/#264).
"""
from pathlib import Path
import pcbnew as p, json, shutil, sys, math
E=Path(__file__).resolve().parent; BASE=E.parent/'issue-235-wing-round2'
FP='Hirose_FH12-14S-0.5SH_1x14-1MP_P0.50mm_Horizontal'
def V(x,y): return p.VECTOR2I(round(x*1e6),round(y*1e6))
if len(sys.argv)==1:
 import subprocess
 for src in sorted(BASE.glob('wing-rev4-*')): subprocess.run([sys.executable,__file__,src.name],check=True)
 sys.exit(0)
for src in sorted(BASE.glob("wing-rev4-*")):
 if src.name!=sys.argv[1]: continue
 name='wing-rev5-'+src.name[len('wing-rev4-'):]
 w=E/name; w.mkdir(exist_ok=True)
 b=p.LoadBoard(str(src/'routed.kicad_pcb'))
 old=[f for f in b.GetFootprints() if f.GetReference()=='J_WING'][0]
 pos=old.GetPosition(); ang=old.GetOrientationDegrees(); flipped=old.IsFlipped()
 nets={a.GetNumber():a.GetNetCode() for a in old.Pads() if a.GetNumber()!='MP'}
 netnames={a.GetNetCode():a.GetNetname() for a in old.Pads() if a.GetNumber()!='MP'}
 oldrow=[a.GetPosition() for a in old.Pads() if a.GetNumber()!='MP']
 oc=(sum(q.x for q in oldrow)/len(oldrow), sum(q.y for q in oldrow)/len(oldrow))
 cx,cy=p.ToMM(pos.x),p.ToMM(pos.y)
 f=p.FootprintLoad(str(E/'connector'),FP); assert f, 'footprint load failed'
 b.Add(f); f.SetReference('J_WING'); f.SetValue('FH12-14S-0.5SH(55)')
 if flipped: f.Flip(pos,False)
 f.SetPosition(pos); f.SetOrientationDegrees(ang)
 newrow=[a.GetPosition() for a in f.Pads() if a.GetNumber()!='MP']
 nc=(sum(q.x for q in newrow)/len(newrow), sum(q.y for q in newrow)/len(newrow))
 f.SetPosition(p.VECTOR2I(int(pos.x+(oc[0]-nc[0])), int(pos.y+(oc[1]-nc[1]))))
 # Shift along the mouth direction so the housing (envelope) centre
 # matches the #261 spec: pad row sits 2.40 mm behind the housing
 # centre; the GH pad row it was aligned to sits 2.95 mm further back.
 rowc=[sum(p.ToMM(a.GetPosition().x) for a in f.Pads() if a.GetNumber()!='MP')/14,sum(p.ToMM(a.GetPosition().y) for a in f.Pads() if a.GetNumber()!='MP')/14]
 mpc=[sum(p.ToMM(a.GetPosition().x) for a in f.Pads() if a.GetNumber()=='MP')/2,sum(p.ToMM(a.GetPosition().y) for a in f.Pads() if a.GetNumber()=='MP')/2]
 dx,dy=mpc[0]-rowc[0],mpc[1]-rowc[1]; L=math.hypot(dx,dy); ux,uy=dx/L,dy/L
 fp0=f.GetPosition(); f.SetPosition(p.VECTOR2I(int(fp0.x+ux*2.95*1e6),int(fp0.y+uy*2.95*1e6)))
 anchor=[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)]
 for a in f.Pads():
  if a.GetNumber()=='MP': a.SetNetCode(0)
  else: a.SetNetCode(nets[a.GetNumber()])
 removed=0
 for t in list(b.GetTracks()):
  if t.GetNetCode() not in nets.values(): continue
  s,e=t.GetStart(),t.GetEnd()
  if max(abs(p.ToMM(s.x)-cx),abs(p.ToMM(s.y)-cy),abs(p.ToMM(e.x)-cx),abs(p.ToMM(e.y)-cy))<18.0:
   b.Remove(t); removed+=1
 b.Remove(old)
 p.SaveBoard(str(w/'input.kicad_pcb'),b)
 for n in ('input.kicad_pro','main.kicad_pro'):
  src2=src/n
  if src2.exists(): shutil.copyfile(src2,w/n)
 d=json.loads((src/'definition.json').read_text()); d['status']='Issue 263 Wing Rev.5 implementation; no manufacturing release'
 for c in d['components']:
  if c['reference']=='J_WING':
   c['mpn']='FH12-14S-0.5SH(55)'; c['value']='FH12-14S-0.5SH(55)'; c['kind']='connector_zif'
 (w/'definition.json').write_text(json.dumps(d,indent=2)+'\n')
 (w/'swap.json').write_text(json.dumps(dict(variant=name,removed_local_tracks=removed,anchor_mm=anchor,angle_deg=ang,flipped=flipped,net_by_pad={k:netnames[v] for k,v in nets.items()}),indent=2)+'\n')
 print(name,'removed',removed,flush=True)
