from common import *
import shutil
source=E/'inputs/local';w=E/'runs/local';w.mkdir(parents=True,exist_ok=False)
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(source/('main.'+ext),w/('in.'+ext))
args=ARGS+['--keep-input-copper','--nets','V1V1','V3V3','QSPI_SD0','XOUT','--ordering','original']
assert run('local-effective',[B/'venv/bin/python3',E/'read-effective.py',w/'effective.json',source/'main.kicad_pcb']+args)==0
c=json.loads((w/'effective.json').read_text());assert c['escalation_policy'][0]=='off' and c['grid_route_config']['layer_costs']==[1.,-1.,1.,1.]
rc=run('local-krt-route',[B/'venv/bin/python3','py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb']+args,cwd=K,timeout=900)
save(w/'execution.json',dict(utc=now(),attempt=1,final_permitted_routing_attempt=True,exit_code=rc,args=args,input_unchanged=digest(w/'in.kicad_pcb')==digest(source/'main.kicad_pcb')))
raise SystemExit(rc)
