"""Bounded repair/refill/native DRC/independent acceptance for a saved candidate.
Never accepts router status; routing dimensions and project floors stay fixed.
"""
from pathlib import Path
import subprocess,sys,json,os
E=Path(__file__).resolve().parent
for name in sys.argv[1:]:
 w=E/name
 def run(script):subprocess.run([sys.executable,str(E/script),name],check=True)
 for iteration in range(6):
  subprocess.run(['kicad-cli','pcb','drc','--format','json','--severity-all','-o',str(w/'drc.json'),str(w/'main.kicad_pcb')],check=True)
  d=json.loads((w/'drc.json').read_text())
  if d['unconnected_items'] or any(v['type'] not in ('track_dangling','via_dangling') for v in d['violations']):
   os.environ.setdefault('WING_ROUTE_STEP','.1');run('plane-repair.py');continue
  run('cleanup.py');run('via-margin.py');run('cleanup.py')
  result=subprocess.run([sys.executable,str(E/'verify.py'),name])
  if result.returncode==0:break
 else:raise RuntimeError(name+' did not qualify within six repair laps')
 print(name,'accepted',flush=True)
