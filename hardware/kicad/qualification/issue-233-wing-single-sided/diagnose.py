"""Native saved-candidate diagnostics, including unsuccessful routes; never certify them."""
from pathlib import Path
import pcbnew as p
import json,subprocess,shutil,sys,importlib.util,collections,hashlib,math
E=Path(__file__).resolve().parent;BASE=E.parent/'issue-200-wing-rev3'
spec=importlib.util.spec_from_file_location('rev3verify',BASE/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
if len(sys.argv)!=2:
 for name in (sys.argv[1:] or [w.name for w in sorted(E.glob('wing-rev4-*'))]):subprocess.run([sys.executable,__file__,name],check=True)
 sys.exit(0)
for w in sorted(E.glob('wing-rev4-*')):
 if len(sys.argv)>1 and w.name not in sys.argv[1:]:continue
 if not (w/'routed.kicad_pcb').exists():continue
 b=p.LoadBoard(str(w/'routed.kicad_pcb'));mgr=p.GetSettingsManager();mgr.LoadProject(str(w/'input.kicad_pro'));b.SetProject(mgr.Prj())
 changes=[]
 for t in b.GetTracks():
  if not isinstance(t,p.PCB_VIA) and t.GetNetname() in ('HALL_5V','GND') and t.GetWidth()<300000:
   changes.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'old_width_mm':p.ToMM(t.GetWidth()),'new_width_mm':.3,'start_mm':v.xy(t.GetStart()),'end_mm':v.xy(t.GetEnd())});t.SetWidth(300000)
 v.save(w/'power-width-normalization.json',changes)
 # Same complementary pours as Rev.3; exact nominal clearance floor. No
 # optimistic graph connections by net name: native refill and copper graph follow.
 points=json.loads((w/'definition.json').read_text())['outline_mm']
 for net,layer in [('HALL_5V',p.F_Cu),('GND',p.B_Cu)]:
  z=p.ZONE(b);z.SetLayer(layer);z.SetNetCode(b.FindNet(net).GetNetCode());z.SetZoneName('Study '+net);z.SetLocalClearance(p.FromMM(.15));z.SetMinThickness(p.FromMM(.3));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
  poly=z.Outline();poly.NewOutline()
  for x,y in points:poly.Append(round((100+x)*1e6),round((100-y)*1e6))
  b.Add(z)
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();p.SaveBoard(str(w/'main.kicad_pcb'),b)
 # KRT may alter its output project: restore the immutable input rules, and
 # diagnose under those rules, rather than accepting router-specific changes.
 shutil.copyfile(w/'input.kicad_pro',w/'main.kicad_pro')
 subprocess.run(['kicad-cli','pcb','drc','--format','json','--severity-all','-o',str(w/'drc.json'),str(w/'main.kicad_pcb')],check=True)
 result=v.qualify(w)
 byid={t.m_Uuid.AsString():t for t in b.GetTracks()}
 byid.update({a.m_Uuid.AsString():a for f in b.GetFootprints() for a in f.Pads()})
 drc=json.loads((w/'drc.json').read_text());opens=[]
 for item in drc['unconnected_items']:
  q={'description':item['description'],'ends':[]}
  for a in item['items']:
   t=byid.get(a['uuid']);q['ends'].append({**a,'net':t.GetNetname() if t else None})
  opens.append(q)
 log=(w/'route.log').read_text();summaries={}
 for line in log.splitlines():
  for prefix in ('JSON_REGRADE: ','JSON_SUMMARY_MIN: ','JSON_SUMMARY: '):
   if line.startswith(prefix):
    try:summaries[prefix.strip(': ')]=json.loads(line[len(prefix):])
    except json.JSONDecodeError:pass
 v.save(w/'congestion.json',{'qualified':result['pass'],'open_connections':opens,'router':summaries,'power_voltage_extraction':'NOT performed on a failing/disconnected board','erc':'NOT RUN: no native Wing schematic in Rev.3 package; routing gate not passed'})
