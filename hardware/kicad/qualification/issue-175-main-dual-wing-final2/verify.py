"""Verify qualification, provenance, budgets, CAM and unchanged fallback before commit."""
from common import *
import csv,re,collections
read=lambda n:json.loads((E/n).read_text())
G=['git','--git-dir='+str(T/'git'),'--work-tree='+str(R)];base=read('start.json')['base'];s=read('status.json')
assert s['PCB_qualification_pass'] and not s['issue_complete'] and not s['manufacturing_GO']
assert s['route_attempts']==dict(global_count=1,local_count=0,remaining=0)
assert len(list((E/'runs').glob('*/execution.json')))==1
assert len(list((E/'processes').glob('*krt-route/record.json')))==1
assert read('runs/final/execution.json')['exit_code']==0 and read('runs/final/execution.json')['input_unchanged']
assert read('attempt-reserved.json')['whole_board_attempt']==1
sel=read('candidate-selection.json');assert len(sel['attempts'])==2 and sel['selected']=='candidate-2'
assert not sel['attempts'][0]['pass_preflight'] and sel['attempts'][1]['pass_preflight']
for row in sel['attempts']:
 w=E/'inputs'/row['candidate'];assert row['board_sha256']==digest(w/'main.kicad_pcb');assert row['project_sha256']==digest(w/'main.kicad_pro');assert row['drc_sha256']==digest(w/'preflight.json')
assert read('preflight-receipt.json')['board_sha256']==digest(E/'inputs/final/main.kicad_pcb')
assert read('placement-check.json')['pass_selected_geometry']
a=read('inspection/final/assessment.json');g=read('inspection/final/connectivity.json');d=read('inspection/final/drc.json')
assert a['pass_acceptance'] and list(a['metrics'].values())==[0,0,0,0]
assert not d['unconnected_items'] and g['nets_checked']==44 and g['wrong_net_contacts']==g['required_unconnected']==0
assert read('circuit-check-final.json')['pass_check'] and read('circuit-check-final.json')['logical_pins_checked']==245
physical=a['physical'];assert physical['thickness_mm']==1.2 and physical['copper_layers']==['F.Cu','In1.Cu','In2.Cu','B.Cu']
assert physical['tracks_per_layer'].get('In1.Cu',0)==0 and physical['via_diameter_drill_mm_counts']=={'0.6/0.3':113}
assert all(float(x)>=.1 for x in physical['track_width_mm_counts'])
eff=read('runs/final/effective.json');c=eff['grid_route_config'];assert c['track_width']==c['clearance']==.1 and c['via_size']==.6 and c['via_drill']==.3 and c['layer_costs']==[1.,-1.,1.,1.] and eff['escalation_policy'][0]=='off'
h=digest(E/'inspection/final/main.kicad_pcb');assert h==s['final_board_sha256']
assert digest(E/'inputs/final/main.kicad_pro')==digest(E/'inspection/final/main.kicad_pro')
for n,key in [('circuit-check-final.json','PCB_sha256'),('power-extraction-final.json','PCB_sha256'),('ground-extraction-final.json','board_sha256'),('cam-check.json','source_sha256'),('pofv-reclassification-final.json','source_sha256'),('export-provenance.json','board_sha256')]:assert read(n)[key]==h,n
assert read('ground-model-verification.json')['pass_numerics']
r=read('resistance-summary.json')['rows'][0];assert r['qualified'] and r['board_sha256']==h and r['all_loop_targets_met_in_model']
assert read('cam-check.json')['pass_check'] and read('cam-check.json')['pth_round_vias']==113
assert read('pofv-reclassification-final.json')['total_vias']==113 and read('pofv-reclassification-final.json')['candidate_count']==32
assert len(list(csv.DictReader((E/'all-vias.csv').open())))==113
bom=list(csv.DictReader((E/'main-bom.csv').open()));source=list(csv.DictReader((E.parent/'issue-169-main-dual-wing-followup/main-bom.csv').open()));old={r['ref']:r for r in source}
assert len(bom)==62
for row in bom:assert row['part_number']==old[row['ref']]['part_number'],row['ref']
for ref in ['C26','C27','C28']:assert next(x for x in bom if x['ref']==ref)['part_number']=='C3225X7R1C226K250AC'
assert len(list(csv.DictReader((E/'manufacturing/BOM.csv').open())))==len(list(csv.DictReader((E/'manufacturing/CPL.csv').open())))==58
fb=read('fallback-preservation.json');root=R/fb['path']
for path,expected in fb['files'].items():
 f=root/path;assert digest(f)==expected
 blob=subprocess.check_output(G+['show',base+':'+str(f.relative_to(R))]);assert hashlib.sha256(blob).hexdigest()==expected
assert read('runtime-check.json')['source_files']==2055 and not read('runtime-check.json')['mismatches']
q=read('pcba-update-status.json');assert not q['final_quote_confirmed'] and q['final_quote_total'] is None and not q['old_quote_transferred']
assert s['orders']==s['charges']==s['merges']==0 and not s['D019_relaxed']
allowed=[str(E.relative_to(R))+'/', 'docs/issue-175-main-dual-wing-final2.md']
changed=subprocess.check_output(G+['diff','--name-only',base,'--'],text=True).splitlines();assert all(x==allowed[1] or x.startswith(allowed[0]) for x in changed),changed
links=0
for f in [R/allowed[1],E/'README.md']:
 for target in re.findall(r'\]\(([^)]+)\)',f.read_text()):
  if target.startswith(('http://','https://','#')):continue
  assert (f.parent/target.split('#')[0]).exists(),(f,target);links+=1
for f in list(E.glob('*.py'))+[R/allowed[1],E/'README.md',E/'manufacturing/quote-handoff.md']:
 for n,line in enumerate(f.read_text().splitlines(),1):assert line==line.rstrip(),(f,n)
save(E/'verification.json',dict(utc=now(),evidence_integrity_pass=True,PCB_qualification_pass=True,issue_complete=False,manufacturing_GO=False,route_attempts=s['route_attempts'],candidates=2,four_metrics=a['metrics'],nets_checked=44,logical_pins_checked=245,CAM_pass=True,resistance_model_pass=True,fallback_files_compared_to_base=len(fb['files']),runtime_source_files=2055,prior_tracked_files_unchanged=True,quote_confirmed=False,local_links_checked=links,visual_review='Exported CAM contact sheet viewed: four copper layers, north output C paste, four mounting reservations and J1 rear shell paste observed; numeric CAM comparison passed.',no_order_charge_merge=True))
print('PASS: PCB/CAM/resistance/POFV provenance and finite budgets; quotation still incomplete')
