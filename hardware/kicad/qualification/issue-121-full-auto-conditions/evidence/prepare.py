from common import *
import re,copy,shutil
sys.path.insert(0,str(RT/'geometry/lib/python3.12/site-packages'))
import sexpdata as sx
ref=subprocess.check_output(['git','--git-dir='+GIT,'rev-parse','refs/heads/main'],text=True).strip()
assert subprocess.check_output(['git','--git-dir='+GIT,'merge-base','--is-ancestor','ce2e27fe6495dbd08db86bdd9b22a3c93b002347',ref])==b''
old='hardware/kicad/qualification/issue-119-promising-tools-relaxed/evidence/'
paths=subprocess.check_output(['git','--git-dir='+GIT,'ls-tree','-r','--name-only',ref,old],text=True).splitlines()
manifest=json.loads(subprocess.check_output(['git','--git-dir='+GIT,'show',ref+':'+old+'manifest.json']))
save(E/'source119-manifest.json',manifest)
provenance={}
for path in paths:
 rel=path[len(old):]
 if rel.startswith(('inputs/main4/','inputs/smoke4/','inspection/main4/krt/')) or rel in ['equivalence-gate.json','runtime-revalidation.json','smoke-gate.json','assessment.json']:
  if '/.pretty/' in rel:continue
  blob=subprocess.check_output(['git','--git-dir='+GIT,'show',ref+':'+path]);p=E/'source119'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob)
  h=sha(p);expected=manifest.get('files',manifest).get(rel)
  if isinstance(expected,dict):expected=expected.get('sha256')
  assert expected==h,(rel,expected,h)
  provenance[rel]=h
save(E/'source-provenance.json',dict(utc=utc(),source_commit=ref,merged_PR=120,merge_commit='ce2e27fe6495dbd08db86bdd9b22a3c93b002347',method='git show main commit:path, verified against committed #119 manifest',files=provenance))
conditions=json.loads((E/'conditions.json').read_text());rows={}
for cell,c in conditions.items():
 for stage in ['main','smoke']:
  label=stage+'-'+cell;source=E/'source119/inputs'/(stage+'4');w=E/'inputs'/label;w.mkdir(parents=True)
  pcb=(source/'main.kicad_pcb').read_text();dsn=(source/'corrected.dsn').read_text();pro=json.loads((source/'main.kicad_pro').read_text())
  edits=[]
  def edit(text,pattern,replacement):
   changed,count=re.subn(pattern,replacement,text);edits.append(dict(pattern=pattern,replacement=replacement,count=count));return changed
  # The only native changes are zone manufacturing-rule scalars.
  pcb2=edit(pcb,r'\((clearance|min_thickness|thermal_gap|thermal_bridge_width) 0\.127\)',rf'(\g<1> {c["width"]:g})') if c['width']!=.127 else pcb
  restored=re.sub(r'\((clearance|min_thickness|thermal_gap|thermal_bridge_width) 0\.1\)',r'(\1 0.127)',pcb2) if c['width']!=.127 else pcb2
  assert restored==pcb
  (w/'main.kicad_pcb').write_text(pcb2)
  p2=copy.deepcopy(pro);rules=p2['board']['design_settings']['rules'];rules['min_clearance']=rules['min_track_width']=c['width']
  rules['min_via_diameter']=c['via'];rules['min_through_hole_diameter']=c['drill']
  for nc in p2['net_settings']['classes']:
   for key in ['clearance','track_width','diff_pair_width','diff_pair_gap','diff_pair_via_gap']:nc[key]=c['width']
   nc['via_diameter']=c['via'];nc['via_drill']=c['drill']
  pd=delta(pro,p2);assert all(x['path'] in ['/board/design_settings/rules/'+k for k in ['min_clearance','min_track_width','min_via_diameter','min_through_hole_diameter']]+['/net_settings/classes'] for x in pd)
  save(w/'main.kicad_pro',p2)
  dsn2=re.sub(r'\((width|clearance) 127(?=[\s)])',lambda m:'('+m[1]+' '+str(round(c['width']*1000)),dsn)
  if c['via']!=.6:
   assert '(via ' not in pcb # no existing native via can be changed
   dsn2=dsn2.replace('Via[0-3]_600:300_um','Via[0-3]_450:200_um')
   start=dsn2.index('    (padstack "Via[0-3]_450:200_um"');end=dsn2.index('\n    )',start)
   dsn2=dsn2[:start]+dsn2[start:end].replace(' 600)',' 450)')+dsn2[end:]
  reverse=re.sub(r'\((width|clearance) 100(?=[\s)])',r'(\1 127',dsn2) if c['width']==.1 else dsn2
  if c['via']!=.6:
   reverse=reverse.replace('Via[0-3]_450:200_um','Via[0-3]_600:300_um');start=reverse.index('    (padstack "Via[0-3]_600:300_um"');end=reverse.index('\n    )',start);reverse=reverse[:start]+reverse[start:end].replace(' 450)',' 600)')+reverse[end:]
  assert reverse==dsn
  (w/'corrected.dsn').write_text(dsn2)
  rows[label]=dict(source='source119/inputs/'+stage+'4',native_rule_reversal_byte_identical=True,DSN_rule_reversal_byte_identical=True,project_diff=pd,native_edits=edits,hashes={p.name:sha(p) for p in w.iterdir()},rule_changes_only=True)
save(E/'equivalence-gate.json',dict(utc=utc(),pass_equivalence=True,inputs=rows,scope='Reversing only zone scalar rules, DSN width/clearance and unused via padstack definition restores entire original text byte-for-byte; full project recursive diff restricted to listed rule fields. No component, placement, net, layer, thickness or existing copper change.'))
# KRT-only runtime verification; no alternative router invocation.
checks={}
for name,root in [('source-manifest.json',KRT),('inspection-runtime-hashes.json',RT)]:
 prior=R/'hardware/kicad/qualification/issue-113-kicad-routing-tools-falsification/evidence'/name
 data=json.loads(prior.read_text());bad=[p for p,h in data.items() if sha(root/p)!=h];assert not bad
 checks[name]=dict(files=len(data),mismatches=bad,manifest_sha256=sha(prior))
assert (KRT/'VERSION').read_text().strip()=='0.23.8'
assert subprocess.check_output(['git','-C',str(KRT),'rev-parse','HEAD'],text=True).strip()=='c64c0db25e6cf23afa6769ee05665c7ea22b3ff2'
assert not subprocess.check_output(['git','-C',str(KRT),'diff','--name-only'])
binary=list(KRT.rglob('grid_router*.so'));assert len(binary)==1
assert sha(binary[0])=='4411ccf3f074f519d8d69be29ac58b46ca7c4c2fe4f4be889d253d40996c2c0f'
save(E/'runtime-revalidation.json',dict(utc=utc(),checks=checks,version='0.23.8',commit='c64c0db25e6cf23afa6769ee05665c7ea22b3ff2',binary_sha256=sha(binary[0])))
print('INPUT GATES PASS',utc())
