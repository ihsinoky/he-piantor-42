"""Independent native readback and explicit STOP record. Does not run a router."""
from common import *
old=R/'hardware/kicad/qualification/eda-004g/resume-02/read-pcb.py'
checks={}
for stage in ['main','smoke']:
 w=E/'inputs'/stage
 assert run(stage+'-native-readback',['/usr/bin/python3',old,w/'main.kicad_pcb',w/'snapshot.json'])==0
 a=json.loads((R/'hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/evidence/inputs'/stage/'snapshot.json').read_text())
 b=json.loads((w/'snapshot.json').read_text());changes=delta(a,b)
 assert {x['path'] for x in changes}==({'/layers','/zones'} if stage=='main' else {'/layers'})
 assert b['thickness']==1.2 and b['default']==dict(clearance=.2,width=.2,via=.6,drill=.3)
 f=json.loads((w/'fab-readback.json').read_text());assert [x['role'] for x in f['stack']]==['signal','plane','signal','signal']
 assert all(g['usable']==[0,2,3] for g in f['netGroups'])
 assert all(all(v/f['frame']['luPerUm']==200 for v in g['widthBySheet']) for g in f['netGroups'])
 if stage=='main':
  plane=f['stack'][1]['planeNet'];assert next(x['name'] for x in f['nets'] if x['id']==plane)=='GND'
  assert len(f['pours'])==1 and f['pours'][0]['net']==plane
 k=json.loads((E/'configuration'/f'{stage}-explicit.json').read_text());config=k['grid_route_config']
 assert config['track_width']==config['clearance']==.2 and config['via_size']==.6 and config['via_drill']==.3
 assert config['layer_costs']==[1,-1,1,1] and k['escalation_policy'][0]=='off'
 checks[stage]=dict(native_snapshot_changes=changes,all_footprint_pad_network_edge_original_track_snapshot_fields_equal=True,fab_parser_roles_pass=True,fab_no_In1_in_signal_usable_sheets=True,krt_explicit_dimensions_and_forbidden_In1_config_pass=True,routing_performed=False)
save(E/'preparation-readback.json',dict(utc=utc(),checks=checks,not_a_smoke_acceptance=True))
metrics=dict(required_unconnected=None,wrong_net_contacts=None,material_violations=None,unexplained_transfer_changes=None)
save(E/'equivalence-gate.json',dict(utc=utc(),pass_equivalence=False,status='STOP_FIXED_SMOKE_HAS_NO_GND',routing_started=False,main_native_and_DSN_equivalence=True,smoke_inventory_preserved=True,smoke_GND_zone_requirement=False,reason='The SHA256-fixed smoke board defines only nonempty net N. Adding GND or renaming N changes its net inventory. A net-GND zone and unchanged nets cannot both be satisfied.',router_smoke_gate=dict(fab_router='NOT_RUN',kicad_routing_tools='NOT_RUN'),independent_metrics=metrics))
save(E/'assessment.json',dict(utc=utc(),status='STAGE_0_STOP',stage0='Fixed smoke net/GND zone conflict; no route allowed',stage1={x:dict(status='NOT_RUN_STAGE0_GATE_CLOSED',runs=0,independent_metrics=metrics,unconnected_count=None,unconnected_net_endpoint_list=None,width_distribution=None,via_distribution=None,tracks_per_layer=None,plane_connections=None,execution_seconds=None,output_project_changes=None,stop_reason='Stage 0 gate closed before routing') for x in ['fab_router','kicad_routing_tools']},wing=dict(status='ANALYSIS_ONLY',runs=0,consumed_layout_paths=[]),D012_modified=False))
