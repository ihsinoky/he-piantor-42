"""Author Rev.3 from each independently generated Rev.2 placement and Stage 1 geometry.
Run with .issue200-runtime/run /usr/bin/python3. No inherited routed copper.
"""
from pathlib import Path
import json,math,shutil
import pcbnew as p
from shapely.geometry import Polygon,LineString
E=Path(__file__).resolve().parent;R=E.parents[3]
V=lambda x,y:p.VECTOR2I(round(x*1e6),round(y*1e6))
def save(path,o):path.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
native_boards=[]  # Keep SWIG board parents alive across project loads.
for g in json.loads((R/'hardware/case/issue-200-stage1/geometry.json').read_text())['variants']:
 name='wing-rev3-'+g['variant'];w=E/name;w.mkdir(exist_ok=True);old=E.parent/'issue-194-wing-rev2'/name.replace('rev3','rev2')
 s=json.loads((old/'definition.json').read_text());s.update(name=name,outline_mm=g['outline_local'],status='Issue 200 Stage 2 candidate',service_reservations=[],service_notes=['Rev.3 north tab service layout; real pad rotations, no mirrored pads'])
 s['width_mm']=max(x for x,y in s['outline_mm'])-min(x for x,y in s['outline_mm']);s['height_mm']=max(y for x,y in s['outline_mm'])-min(y for x,y in s['outline_mm'])
 s.pop('south_cut',None);s['layout_source']='hardware/case/issue-200-stage1/geometry.json';s['outline_policy']='Stage 1 north tab and stepped south trim';s['harness']['length_decision']='pending: evaluate 124 and 200mm'
 b=p.LoadBoard(str(old/'input.kicad_pcb'));native_boards.append(b);fs={f.GetReference():f for f in b.GetFootprints()}
 for z in list(b.Zones()):b.Delete(z)
 for d in list(b.GetDrawings()):b.Delete(d)
 m=g['transform']['matrix'];t=g['transform']['translation'];sgn=1 if g['side']=='left' else -1
 def local(ax,ay):
  dx=ax-t[0];dy=ay-t[1];return [m[0][0]*dx+m[1][0]*dy,m[0][1]*dx+m[1][1]*dy]
 tps=[c for c in s['components'] if c['kind']=='testpoint']
 poses={'J_WING':g['connector']['local']}
 for i,group in enumerate('ABC'):
  poses['U_MUX_'+group]=local(sgn*(-38+10*i),-26)
  poses['C_MUX_'+group]=local(sgn*(-38+10*i),-21)
 for i,c in enumerate(tps):poses[c['reference']]=local(sgn*(-40+1.7*i),-33)
 for c in s['components']:
  if c['reference'] not in poses:continue
  x,y=poses[c['reference']];c.update(x_mm=x,y_mm=y,rotation_ccw_deg=g['connector']['local_ccw_deg'])
  f=fs[c['reference']];f.SetPosition(V(100+x,100-y));f.SetOrientationDegrees(c['rotation_ccw_deg'])
 for h in g['mounting_candidates']:
  ref=h['ref'];x,y=h['candidate_local'];fs[ref].SetPosition(V(100+x,100-y));s['mounting_holes'][int(ref[1:])-1].update(x_mm=x,y_mm=y)
 # Full phi5 mounting reservations, never relaxed around moved hole.
 for i,h in enumerate(s['mounting_holes'],1):
  x,y=h['x_mm'],h['y_mm'];z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask());z.SetZoneName(f'Mounting H{i} phi5');z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(False);z.SetDoNotAllowCopperPour(True);poly=z.Outline();poly.NewOutline()
  for j in range(128):a=2*math.pi*j/128;v=V(100+x+2.5/math.cos(math.pi/128)*math.cos(a),100-y+2.5/math.cos(math.pi/128)*math.sin(a));poly.Append(v.x,v.y)
  b.Add(z)
 for i,(x,y) in enumerate(s['outline_mm']):
  xx,yy=s['outline_mm'][(i+1)%len(s['outline_mm'])];d=p.PCB_SHAPE();d.SetShape(p.SHAPE_T_SEGMENT);d.SetStart(V(100+x,100-y));d.SetEnd(V(100+xx,100-yy));d.SetWidth(p.FromMM(.05));d.SetLayer(p.Edge_Cuts);b.Add(d)
 # Keep signal routing/vias away from the south 2mm band. Pours are allowed;
 # power spine is generated after full KRT routing, in the reserved band.
 band=LineString([(100+x,100-y) for x,y in ([g['south_trim_line_local'][0][0]]+[ab[1] for ab in g['south_trim_line_local']])]).buffer(2,join_style=2).intersection(Polygon([(100+x,100-y) for x,y in s['outline_mm']]))
 for part in getattr(band,'geoms',[band]):
  z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask());z.SetZoneName('South reserved band: no signal tracks or vias');z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(False);z.SetDoNotAllowCopperPour(False);poly=z.Outline();poly.NewOutline()
  for x,y in list(part.exterior.coords)[:-1]:v=V(x,y);poly.Append(v.x,v.y)
  b.Add(z)
 pro=json.loads((old/'input.kicad_pro').read_text());save(w/'input.kicad_pro',pro);manager=p.GetSettingsManager();manager.LoadProject(str(w/'input.kicad_pro'));b.SetProject(manager.Prj());p.SaveBoard(str(w/'input.kicad_pcb'),b)
 (w/'fp-lib-table').write_text((old/'fp-lib-table').read_text().replace('WingRev2','WingRev3'))
 save(w/'definition.json',s);save(w/'placement-changes.json',dict(components=poses,mounting=g['mounting_candidates'],right_independent=True));print(name,flush=True)

# Derived metadata must not retain Rev.2 connector access or 100mm length.
import subprocess,sys
subprocess.run([sys.executable,str(E/"update-definitions.py")],check=True)
