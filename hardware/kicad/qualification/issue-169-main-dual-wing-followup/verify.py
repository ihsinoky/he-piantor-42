"""Evidence integrity only. Seed-b remains unqualified and issue incomplete."""
from common import *
import csv,math,collections,re,sexpdata as sx
read=lambda f:json.loads((E/f).read_text())
status=read('status.json');assert not status['issue_complete'] and not status['manufacturing_GO'];assert status['route_attempts']==dict(global_count=2,local_count=0,remaining=0)
assert len(list((E/'runs').glob('seed-*/execution.json')))==2
for label,expected in [('seed-a',[0,0,0,0]),('seed-b',[2,2,4,7])]:
 s=next(x for x in status['attempts'] if x['label']==label);assert list(s['measured_four_metrics'].values())==expected and s['nets_checked']==44
 a=read('inspection/'+label+'/assessment.json');g=read('inspection/'+label+'/connectivity.json');t=read('inspection/'+label+'/transfer-diff.json');d=read('inspection/'+label+'/drc.json')
 assert a['pass_acceptance']==(label=='seed-a') and g['nets_checked']==44
 assert len(d['unconnected_items'])==g['required_unconnected']==expected[0]
 assert g['wrong_net_contacts']==expected[1] and a['raw_material_count']==expected[2]
 assert len(t['missing_retained_tracks'])+len(t['missing_retained_vias'])+len(t['nonroute_removed'])+len(t['nonroute_added'])==expected[3]
 assert a['width_pass'] and a['via_pass'] and a['plane_pass']
 assert read('circuit-check-'+label+'.json')['pass_check'] and read('circuit-check-'+label+'.json')['logical_pins_checked']==245
 assert digest(E/'inspection'/label/'main.kicad_pro')==digest(E/'inputs'/label/'main.kicad_pro')
 eff=read('runs/'+label+'/effective.json');c=eff['grid_route_config'];assert c['track_width']==c['clearance']==.1 and c['via_size']==.6 and c['via_drill']==.3 and c['layer_costs']==[1.,-1.,1.,1.]
 assert eff['escalation_policy'][0]=='off' and len(eff['native_keepouts'])==4
 if label=='seed-b':assert set(a['metrics'].values())=={None}
 assert read('runs/'+label+'/execution.json')['input_unchanged']
assert read('inspection/final/assessment.json')['pass_acceptance'] and set(read('inspection/final/assessment.json')['metrics'].values())=={0}
def copper(file):
 x=sx.loads(Path(file).read_text());return collections.Counter(sx.dumps(v) for v in x if isinstance(v,list) and v and str(v[0]) in ['segment','via'])
for family,stem in [('inputs','main'),('runs','out')]:assert copper(E/family/'seed-a'/(stem+'.kicad_pcb'))==copper(E/family/'final'/(stem+'.kicad_pcb'))
for x in ['pads','tracks','components']:assert read('inspection/seed-a/snapshot.json')[x]==read('inspection/final/snapshot.json')[x]
assert read('paste-correction.json')['new_openings']==36 and read('paste-correction.json')['additional_routing_attempts']==0
pre=read('preflight-seed-b-revision2.json');bad=[x for x in pre['violations'] if x['type'] not in {'text_height','silk_overlap','silk_over_copper','via_dangling'}];assert any(x['type']=='shorting_items' for x in bad)
assert read('processes/guard-budget-test/record.json')['exit_code']==1
assert 'budget exhausted' in (E/'processes/guard-budget-test/stderr').read_text()
assert read('cam-check.json')['pass_check'] and read('cam-check.json')['pth_round_vias']==110
assert digest(E/'inspection/final/main.kicad_pcb')==read('export-provenance.json')['board_sha256']
assert not status['final_manufacturing_generated'] and not status['pcba_final_quote_confirmed']
assert not read('pcba-update-status.json')['final_quote_confirmed'] and read('pcba-update-status.json')['final_quote_total'] is None
assert read('pofv-reclassification-seed-a.json')['candidate_count']==28 and read('pofv-reclassification-seed-b.json')['candidate_count']==40
assert read('pofv-reclassification-seed-b.json')['total_vias']==127
assert read('ground-model-verification.json')['pass_numerics']
for label in ['seed-a','seed-b']:
 gr=read('ground-extraction-'+label+'.json');assert gr['assumptions']['port_current'].startswith('U6.10 PGND only')
 assert gr['board_sha256']==digest(E/'inspection'/label/'main.kicad_pcb')
 assert len(gr['rows'])==4 and {x['max_triangle_area_mm2'] for x in gr['rows']}=={.03,.0075}
 for row in gr['rows']:assert row['results_at_20C']['output_returns'][0]['reference_pads']==['U6.10']
rowdata=list(csv.DictReader((E/'connector-current-sensitivity.csv').open()));assert len(rowdata)==270
for r in rowdata:
 a={k:float(r[k]) for k in ['connector_V','efficiency_assumption','Wing_A','rail_V','converter_V','converter_A','Main_other_allocation_A','total_USB_A','input_loop_ohm']}
 assert abs(a['total_USB_A']-a['converter_A']-a['Main_other_allocation_A'])<1e-12
 assert abs(a['converter_A']*a['converter_V']*a['efficiency_assumption']-2*a['Wing_A']*a['rail_V'])<1e-12
 assert abs(a['converter_V']+a['total_USB_A']*a['input_loop_ohm']-a['connector_V'])<1e-12
 assert (r['load_class']=='design')==(a['Wing_A']==.127)
selection=read('component-selection.json')['seed_b'];assert math.isclose(selection['output_screening_effective_uF'],3*22*.85*.9*.85*.9) and selection['output_screening_effective_uF']>33
assert selection['input_screening_effective_uF']>4.7
bom=list(csv.DictReader((E/'main-bom.csv').open()));assert len(bom)==62 and len({x['ref'] for x in bom})==62
for r in ['C26','C27','C28']:assert next(x for x in bom if x['ref']==r)['part_number']=='C3225X7R1C226K250AC'
for row in read('sources.json'):
 if 'sha256' in row:assert digest(E/'sources'/row['file'])==row['sha256']
assert read('runtime-check.json')['source_files']==2055 and not read('runtime-check.json')['mismatches']
G=['git','--git-dir='+str(T/'git'),'--work-tree='+str(R)];base=read('start.json')['base_sha']
changed=subprocess.check_output(G+['diff','--name-only',base,'--'],text=True).splitlines();allowed=['docs/issue-169-main-dual-wing-followup.md',str(E.relative_to(R))+'/']
assert all(x==allowed[0] or x.startswith(allowed[1]) for x in changed),changed
assert subprocess.check_output(G+['show',base+':docs/decisions.md'])==(R/'docs/decisions.md').read_bytes()
for path,h in read('frozen-inputs.json').items():assert digest(E/path)==h,path
links=[]
for file in [E/'README.md',R/'docs/issue-169-main-dual-wing-followup.md']:
 for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
  if target.startswith(('http://','https://','#')):continue
  assert (file.parent/target.split('#')[0]).exists(),(file,target);links.append(target)
for f in list(E.glob('*.py'))+[E/'README.md',E/'draft-pr-body.md',R/'docs/issue-169-main-dual-wing-followup.md']:
 for n,line in enumerate(f.read_text().splitlines(),1):assert line==line.rstrip(),(f,n)
save(E/'verification.json',dict(utc=now(),evidence_integrity_pass=True,final_selected_component_PCB_qualified=False,issue_complete=False,route_attempts=dict(global_count=2,local_count=0,remaining=0),actual_metrics=dict(seed_a=[0,0,0,0],seed_b=[2,2,4,7]),nets_checked_each=44,logical_pins_checked_each=245,paste_only_copper_identity=True,source_preflight_failure_preserved=True,exhausted_budget_guard_rejection_verified=True,prior_tracked_files_and_decisions_unchanged=True,source_files_checked=2055,ground_boundary='PGND only / USB contacts / six GH contacts',ground_numerics=True,current_cases_verified=len(rowdata),BOM_rows=62,seed_a_review_CAM_checked=True,seed_b_CAM_and_final_quote_not_claimed=True,local_links_checked=len(links),visual_review='Seed-a CAM contact sheet viewed: correct extended outline, four mounting voids, 4 copper layers, added north paste and USB shell rear paste. Numeric CAM check governs exact geometry.',forbidden_actions_performed=[]))
print('Evidence integrity PASS; seed-b PCB qualification FAIL; issue incomplete; two whole-board runs spent')
