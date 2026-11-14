"""Replay the accepted copper removals from the archived interrupted-run boards.
Writes only the two repaired Wing candidates; all other candidates stay frozen.
Run native/independent gates and extraction afterward with reproduce.sh --extract.
"""
from pathlib import Path
import json,gzip,shutil,importlib.util,sys
import pcbnew as p
E=Path(__file__).resolve().parent;R=E.parents[3];T=R/'.issue250-runtime'
sys.path.insert(0,str(E))
sp=importlib.util.spec_from_file_location('plane',E/'plane-components.py');plane=importlib.util.module_from_spec(sp);sp.loader.exec_module(plane)
for name in ['wing-rev4-16mm-left','wing-rev4-17mm-left']:
 src=E/name/'main.kicad_pcb';rules=src.with_suffix('.kicad_pro').read_bytes()
 assert rules==(E/name/'input.kicad_pro').read_bytes(),'Original project rules required'
 src.write_bytes(gzip.decompress((E/'continuation-start'/(name+'.kicad_pcb.gz')).read_bytes()))
 # Load in its original project context. SaveBoard to a different basename
 # can write default project settings, so only copy its PCB back afterward.
 b=p.LoadBoard(str(src));held=[]
 assert len(plane.components(b,'GND'))==1
 changes=json.loads((E/'continuation-repairs.json').read_text())[name];assert changes['adopted'];ids={x['uuid'] for x in changes['changes']};found=set()
 for t in list(b.GetTracks()):
  if t.m_Uuid.AsString() in ids:found.add(t.m_Uuid.AsString());assert not isinstance(t,p.PCB_VIA) and t.GetNetname()=='GND' and p.ToMM(t.GetWidth())<.3;held.append(t);b.Remove(t)
 assert found==ids
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());out=T/(name+'-continuation-final.kicad_pcb');p.SaveBoard(str(out),b)
 shutil.copyfile(out,src);assert src.with_suffix('.kicad_pro').read_bytes()==rules
 print(name,'removed',len(ids),'redundant GND stubs')
 # Keep SWIG boards and children alive across iterations.
 globals().setdefault('boards',[]).append((b,held))
