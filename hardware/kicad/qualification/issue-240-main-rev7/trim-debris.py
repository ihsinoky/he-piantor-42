from common import *
w=E/'inspection/final';cli=B/'kicad/usr/bin/kicad-cli'
if '--once' in sys.argv:
 import pcbnew as p
 d=json.loads((w/'drc.json').read_text());bad={a['uuid'] for v in d['violations'] if v['type'] in ['track_dangling','via_dangling'] for a in v['items']}
 b=p.LoadBoard(str(w/'main.kicad_pcb'));held=[]
 for t in b.GetTracks():
  if t.m_Uuid.AsString() in bad:held.append(t);b.Remove(t)
 p.SaveBoard(str(w/'main.kicad_pcb'),b)
else:
 removed=[]
 for i in range(40):
  d=json.loads((w/'drc.json').read_text());bad={a['uuid'] for v in d['violations'] if v['type'] in ['track_dangling','via_dangling'] for a in v['items']}
  if not bad:break
  subprocess.run([sys.executable,__file__,'--once'],env=env,check=True);removed.extend(sorted(bad))
  subprocess.run([str(cli),'pcb','drc','--format','json','--severity-all','-o',str(w/'drc.json'),str(w/'main.kicad_pcb')],env=env,check=True,stdout=subprocess.DEVNULL)
 else:raise RuntimeError('debris trimming failed to converge')
 save(E/'trimmed-debris.json',removed)
