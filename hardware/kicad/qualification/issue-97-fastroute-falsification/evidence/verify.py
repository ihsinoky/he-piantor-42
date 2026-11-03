"""Validate saved evidence and add-only scope; never launches a router."""
import hashlib,json,pathlib,subprocess,sys
E=pathlib.Path(__file__).resolve().parent; ROOT=E.parents[4]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checked=[]
for stage in ['smoke','main']:
    work=E/'processes'/stage; r=json.loads((work/'record.json').read_text())
    assert r['exit_code']==0 and r['input_unchanged'] and not r.get('outer_timeout',False)
    assert r['argv'][1:]==['-de','corrected.dsn','-do','out.ses','--report=report.json','--max-time=1800']
    for name,info in r['artifacts'].items(): assert sha(work/name)==info['sha256'],(stage,name)
    assert sha(work/'corrected.dsn')==r['input_sha256']
    original=ROOT/'hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes'/(stage+'-restore')/'corrected.dsn'
    assert sha(original)==r['input_sha256']
    checked.append(stage+' saved artifact hashes, exact command, input identity, natural exit')
assert json.loads((E/'smoke-gate.json').read_text())['main_allowed']
smoke=json.loads((E/'smoke-independent.json').read_text())
assert all(smoke[x]==0 for x in ['required_unconnected','wrong_net_actual_copper_contacts','targeted_material_violations','unexplained_transfer_changes'])
assessment=json.loads((E/'assessment.json').read_text()); report=json.loads((E/'processes/main/report.json').read_text())
assert assessment['router_unrouted']==report['stats']['unrouted']
if report['stats']['unrouted']>0:
    assert all(x is None for x in assessment['independent_metrics'].values())
    assert not assessment['main_independent_checks_performed']
assert assessment['classification']!='SUCCESS' or all(x==0 for x in assessment['independent_metrics'].values())
changes=subprocess.check_output(['git','--git-dir=/tmp/issue-97-fastroute/git','--work-tree='+str(ROOT),'diff','HEAD','--no-renames','--name-status'],text=True)
for line in changes.splitlines():
    status,path=line.split('\t'); assert status=='A',line
    assert path=='docs/issue-97-fastroute-falsification.md' or path.startswith('hardware/kicad/qualification/issue-97-fastroute-falsification/'),path
checked.append('smoke import and independent gate; Main null-metric policy; no tracked worktree modifications')
# No executable or binary distribution inside the deliverable tree.
for p in E.parent.rglob('*'):
    if p.is_file(): assert p.read_bytes()[:4]!=b'\x7fELF',p
manifest={str(p.relative_to(E.parent)):sha(p) for p in E.parent.rglob('*') if p.is_file() and p.name not in ['manifest.json','verification.json']}
manifest['../../../../docs/issue-97-fastroute-falsification.md']=sha(ROOT/'docs/issue-97-fastroute-falsification.md')
(E/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
(E/'verification.json').write_text(json.dumps(dict(passed=True,checks=checked,manifest_entries=len(manifest)),indent=2)+'\n')
print('PASS:',len(manifest),'hashed files;',len(checked),'check groups')
