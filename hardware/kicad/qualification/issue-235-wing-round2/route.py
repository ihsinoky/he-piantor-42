"""Run proven KRT pipeline at D-021 floors, retain unsuccessful evidence."""
from pathlib import Path
import subprocess,concurrent.futures,time,json,os,sys
E=Path(__file__).resolve().parent;ROOT=E.parents[3];T=ROOT/'.issue235-runtime'
KRT=Path(os.environ.get('KRT_HOME','/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools'))
opts=['--track-width','0.1','--power-nets','HALL_5V','GND','--power-nets-widths','0.3','0.3','--escalation','off','--clearance','0.1','--via-size','0.6','--via-drill','0.3','--same-net-pad-clearance','0.15']
def run(w):
 start=time.time();cmd=[str(T/'run'),os.environ.get('ROUTER_PYTHON','/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3'),str(KRT/'py_router/route.py'),str(w/'input.kicad_pcb'),str(w/'routed.kicad_pcb'),*opts]
 with (w/'route.log').open('w') as f:
  try:result=subprocess.run(cmd,cwd=KRT,stdout=f,stderr=subprocess.STDOUT,timeout=1200);code=result.returncode
  except subprocess.TimeoutExpired:code=124
 (w/'route-execution.json').write_text(json.dumps(dict(argv=cmd,exit_code=code,elapsed_seconds=time.time()-start),indent=2)+'\n');print(w.name,code,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,[w for w in sorted(E.glob('wing-rev4-*')) if len(sys.argv)==1 or w.name in sys.argv[1:]]))
