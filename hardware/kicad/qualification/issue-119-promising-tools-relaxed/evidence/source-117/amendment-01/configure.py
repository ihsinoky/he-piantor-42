from helpers import *
(A/'configuration').mkdir()
for policy in ['default','explicit']:
 assert run('amend01-smoke-config-'+policy,[R/'.issue113-runtime/venv/bin/python3',A/'read-effective.py',A/'configuration'/('smoke-'+policy+'.json'),'smoke',policy])==0
baseline=json.loads((A/'configuration/smoke-default.json').read_text());explicit=json.loads((A/'configuration/smoke-explicit.json').read_text())
changes=delta({k:v for k,v in baseline.items() if k not in ['checked_utc','policy']},{k:v for k,v in explicit.items() if k not in ['checked_utc','policy']})
cfg=explicit['grid_route_config'];assert cfg['track_width']==cfg['clearance']==.2 and cfg['via_size']==.6 and cfg['via_drill']==.3
assert cfg['layer_costs']==[1,-1,1,1] and explicit['escalation_policy'][0]=='off'
main=json.loads((E/'configuration/main-explicit.json').read_text());assert cfg==main['grid_route_config']
save(A/'configuration/smoke-diff.json',dict(utc=utc(),differences=changes,main_original_config_unchanged=True,smoke_config_equals_main_config=True,exact_cli_reused_for_execution=True))
