"""Evidence-integrity verification; expressly NOT PCB qualification."""
from common import *
import re,csv,collections,math
status=json.loads((E/'status.json').read_text());assert not status['issue_complete'] and not status['manufacturing_GO']
assert status['route_attempts']==dict(global_count=1,local_count=1,remaining=0)
for label,expected in [('global',[3,0,0,1]),('local',[3,0,2,24])]:
 a=next(x for x in status['attempts'] if x['label']==label)
 assert list(a['measured_four_metrics'].values())==expected and a['nets_checked']==44 and not a['qualified']
 assert a['width_pass'] and a['via_pass'] and a['plane_pass']
 assert json.loads((E/('circuit-check-'+label+'.json')).read_text())['pass_check']
 assert digest(E/'inspection'/label/'main.kicad_pro')==digest(E/'inputs/global/main.kicad_pro')
 assert not json.loads((E/'inspection'/label/'assessment.json').read_text())['pass_acceptance']
 assert json.loads((E/'runs'/label/'execution.json').read_text())['attempt']==1
# Explicitly preserve all unrelated work recorded at the previous authorized start.
protected=json.loads((T/'protected-start.json').read_text());exceptions={'docs/decisions.md','docs/issue-167-main-dual-wing-stage2.md'}
bad=[x for x,h in protected.items() if x not in exceptions and (not (R/x).is_file() or digest(R/x)!=h)];assert not bad,bad
G=['git','--git-dir='+str(T/'git'),'--work-tree='+str(R)]
old=subprocess.check_output(G+['show','0a1f355510e3f2fcadfdc68e7ae97ea90122eb6b:docs/decisions.md'])
new=(R/'docs/decisions.md').read_bytes();assert new.startswith(old) and new[len(old):].decode().count('## D-027')==1
assert digest(E/'previous-run-report.md')==hashlib.sha256(subprocess.check_output(G+['show','0a1f355510e3f2fcadfdc68e7ae97ea90122eb6b:docs/issue-167-main-dual-wing-stage2.md'])).hexdigest()
assert digest(R/'hardware/kicad/qualification/issue-155-main-mounting-stage2/inspection/final/main.kicad_pcb')=='fdc1a7748f94714e395eb50f3e08c43afa24192ee76eb3d1804a8cba28690222'
for x,h in json.loads((E/'frozen-inputs.json').read_text()).items():assert digest(E/x)==h,x
runtime=json.loads((E/'runtime-check.json').read_text());assert not runtime['mismatches'] and runtime['source_files']==2055
rows=list(csv.DictReader((E/'connector-current-sensitivity.csv').open()));assert len(rows)==405
for row in rows:
 a={k:float(row[k]) for k in ['connector_V','efficiency_assumption','input_positive_extracted_ohm','GND_loop_assumption_ohm','Wing_A','rail_V','converter_V','converter_A','Main_other_allocated_A','total_USB_A']}
 assert abs(a['converter_A']+a['Main_other_allocated_A']-a['total_USB_A'])<1e-12
 assert abs(a['converter_A']*a['converter_V']*a['efficiency_assumption']-2*a['Wing_A']*a['rail_V'])<1e-12
 assert abs(a['converter_V']+(a['input_positive_extracted_ohm']+a['GND_loop_assumption_ohm'])*a['total_USB_A']-a['connector_V'])<1e-12
p=json.loads((E/'power-budget.json').read_text());assert p['USB']['connector_min_V']==4.5 and not p['qualified'] and not p['current_guarantee_established'] and p['Main_common_target_not_met_in_model']
assert not (E/'manufacturing').exists()
links=[]
for file in [R/'docs/issue-167-main-dual-wing-stage2.md',E/'README.md']:
 for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
  if target.startswith(('https://','http://','#')):continue
  path=(file.parent/target.split('#')[0]).resolve();assert path.exists(),(file,target);links.append(str(path))
# Preparation failures and temporary SWIG leak diagnostics remain raw evidence,
# but author-authored code/report contain no trailing whitespace.
authored=[R/'docs/decisions.md',R/'docs/issue-167-main-dual-wing-stage2.md']+list(E.glob('*.py'))+[E/'README.md',E/'draft-pr-body.md']
for f in authored:
 for n,line in enumerate(f.read_text().splitlines(),1):assert line==line.rstrip(),(str(f),n)
save(E/'verification.json',dict(utc=now(),evidence_integrity_pass=True,PCB_qualification_pass=False,issue_complete=False,protected_unrelated_files_checked=len(protected)-len(exceptions),protected_changes=bad,decisions_D027_append_only=True,previous_report_byte_preserved=True,baseline_PCB_unchanged=True,bounded_attempts=dict(global_count=1,local_count=1,remaining=0),all_nets_checked=44,circuit_logical_pins_checked=245,current_arithmetic_cases_checked=405,runtime_source_hashes_checked=2055,local_links_checked=len(links),no_manufacturing_output_mislabelled=True,forbidden_actions_performed=[]))
print('Evidence integrity PASS; PCB qualification FAIL; issue incomplete; no remaining routing attempts')
