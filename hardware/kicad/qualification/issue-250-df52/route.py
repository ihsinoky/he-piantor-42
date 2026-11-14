"""Recorded bounded routing; independent subprocesses, no baseline mutations."""
from pathlib import Path
import subprocess,concurrent.futures,time,json,os,sys
E=Path(__file__).resolve().parent;R=E.parents[3];T=R/'.issue250-runtime';KRT=Path('/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools');RP=KRT.parent/'venv/bin/python3'
def run(w):
 name=w.name;out=T/(name+'-route.kicad_pcb')
 opts=['--track-width','.1','--clearance','.1','--via-size','.6','--via-drill','.3','--same-net-pad-clearance','.15','--keep-thermal','--keep-input-copper','--no-stub-layer-swap','--max-iterations','100000','--escalation','off','--power-nets','HALL_5V','GND']
 if name=='main':opts+=['VBUS','V5V2','--power-nets-widths','.5','.3','.5','.5']
 else:opts+=['--power-nets-widths','.3','.3']
 cmd=[str(T/'run'),str(RP),str(KRT/'py_router/route.py'),str(w/'input.kicad_pcb'),str(out),*opts]
 start=time.time();env=dict(os.environ,KICAD_RIP_PREEXISTING='0')
 with (T/(name+'-route.log')).open('w') as f:
  try:rc=subprocess.run(cmd,cwd=KRT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=1200).returncode
  except subprocess.TimeoutExpired:rc=124
 rec=dict(argv=cmd,exit_code=rc,elapsed_seconds=time.time()-start,output_exists=out.exists(),log=str((T/(name+'-route.log')).relative_to(R)))
 (w/'route-execution.json').write_text(json.dumps(rec,indent=2)+'\n');print(name,rc,flush=True)
boards=[w for w in [E/'main',*sorted(E.glob('wing-rev4-*'))] if len(sys.argv)==1 or w.name in sys.argv[1:]]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,boards))
