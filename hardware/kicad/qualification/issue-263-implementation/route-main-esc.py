"""KRT route of Main Rev.8 (same opts as #240 Rev.7 rebuild)."""
from pathlib import Path
import subprocess,time,json,os
E=Path(__file__).resolve().parent;ROOT=E.parents[3];T=ROOT/'.issue263-runtime'
KRT=Path(os.environ.get('KRT_HOME','/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools'))
w=E/'main-rev8'
cmd=[str(T/'run'),os.environ.get('ROUTER_PYTHON','/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3'),str(KRT/'py_router/route.py'),str(w/'input.kicad_pcb'),str(w/'routed.kicad_pcb'),
 '--track-width','.1','--escalation','board','--clearance','.1','--via-size','.6','--via-drill','.3','--same-net-pad-clearance','.15','--keep-thermal','--keep-input-copper','--no-stub-layer-swap','--max-iterations','100000',
 '--power-nets','HALL_5V','GND','VBUS','V5V2','--power-nets-widths','.5','.3','.5','.5']
start=time.time()
with (w/'route.log').open('w') as f:
 try: r=subprocess.run(cmd,cwd=KRT,stdout=f,stderr=subprocess.STDOUT,timeout=2400); code=r.returncode
 except subprocess.TimeoutExpired: code=124
(w/'route-execution.json').write_text(json.dumps(dict(exit_code=code,elapsed_seconds=time.time()-start),indent=2)+'\n')
print('main-rev8 route exit',code)
