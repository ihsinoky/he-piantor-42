"""Remove DRC-flagged redundant tails only if required-pad connectivity survives.
All removals are independently requalified by fresh DRC and verify.py.
"""
import importlib.util,json,subprocess,sys
from pathlib import Path
import pcbnew as p
E=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('plane_repair',E/'plane-repair.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
for name in sys.argv[1:]:
 w=E/name;history=[]
 for iteration in range(20):
  subprocess.run(['kicad-cli','pcb','drc','--format','json','--severity-all','-o',str(w/'drc.json'),str(w/'main.kicad_pcb')],check=True,stdout=subprocess.PIPE)
  drc=json.loads((w/'drc.json').read_text());assert not drc['unconnected_items']
  flagged={a['uuid'] for v in drc['violations'] if v['type']=='track_dangling' for a in v['items']}
  if not flagged:break
  b=p.LoadBoard(str(w/'main.kicad_pcb'));manager=p.GetSettingsManager();manager.LoadProject(str(w/'main.kicad_pro'));b.SetProject(manager.Prj());removed=[]
  for t in list(b.GetTracks()):
   uuid=t.m_Uuid.AsString()
   if uuid not in flagged:continue
   net=t.GetNetname();copy=t.Duplicate();b.Delete(t)
   if len(m.components(b,net))==1:removed.append(dict(uuid=uuid,net=net))
   else:b.Add(copy)
  if not removed:
   # Duplicate() assigns new UUIDs; reload before matching the saved DRC.
   b=p.LoadBoard(str(w/'main.kicad_pcb'));b.SetProject(manager.Prj())
   cleanup_sp=importlib.util.spec_from_file_location('cleanup',E/'cleanup.py');cleanup=importlib.util.module_from_spec(cleanup_sp);cleanup_sp.loader.exec_module(cleanup)
   removed=cleanup.prune(b,drc)
   assert removed,(name,'no redundant tails or safe trims')
  b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(w/'main.kicad_pcb'),b);history.append(removed)
 subprocess.run(['kicad-cli','pcb','drc','--format','json','--severity-all','-o',str(w/'drc.json'),str(w/'main.kicad_pcb')],check=True,stdout=subprocess.PIPE)
 (w/'redundant-tails.json').write_text(json.dumps(history,indent=2)+'\n');print(name,history,flush=True)
