from common import *
import concurrent.futures
(E/'configuration').mkdir(exist_ok=True)
for stage in ['smoke4','main4']:
 for policy in ['default','explicit']:
  assert run(stage+'-config-'+policy,[R/'.issue113-runtime/venv/bin/python3',E/'read-effective.py',E/'configuration'/(stage+'-'+policy+'.json'),stage,policy])==0
 cfg=json.loads((E/'configuration'/(stage+'-explicit.json')).read_text())
 assert cfg['grid_route_config']['track_width']==cfg['grid_route_config']['clearance']==.127
 assert cfg['grid_route_config']['via_size']==.6 and cfg['grid_route_config']['via_drill']==.3
 assert cfg['grid_route_config']['layer_costs']==[1,-1,1,1] and cfg['escalation_policy'][0]=='off'
 save(E/'configuration'/(stage+'-diff.json'),delta(json.loads((E/'configuration'/(stage+'-default.json')).read_text()),cfg))
# Separate processes execute independent predeclared smoke fixtures. No Main execution here.
def smoke(pair):
 label,router=pair
 assert run(label+'-'+router+'-launcher',['/usr/bin/python3',E/'run-cell.py',label,router],timeout=1950)==0
 assert run(label+'-'+router+'-inspection',['/usr/bin/python3',E/'independent-check.py',label,router],timeout=180)==0
 return pair
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for pair in pool.map(smoke,[('smoke4','fab'),('smoke4','krt'),('smoke4','free'),('smoke2','fab')]):print(pair,flush=True)
checks={}
for label,router in [('smoke4','fab'),('smoke4','krt'),('smoke4','free'),('smoke2','fab')]:
 d=json.loads((E/'inspection'/label/router/'independent.json').read_text());checks[label+'-'+router]=d
save(E/'smoke-gate.json',dict(utc=utc(),**{'pass':all(d['pass_acceptance'] for d in checks.values())},checks=checks))
assert all(d['pass_acceptance'] for d in checks.values())
print('STAGE0 PASS',utc())
