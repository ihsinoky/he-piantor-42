import pathlib,json,hashlib,datetime,shutil,subprocess
R=pathlib.Path.cwd();E=R/'hardware/kicad/qualification/issue-105-fab-router-detailed/evidence';T=pathlib.Path('/tmp/issue-105-fab-router');h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads((E/p).read_text())
assert (E/'instructions.md').read_bytes()==pathlib.Path('/home/hatch/workspace/goals/he-piantor-42-keyboard-pmo/instructions/issue-105-fab-router-detailed.md').read_bytes()
manifest={str(p.relative_to(E)):h(p) for p in E.rglob('*') if p.is_file()}
assert load('smoke-gate.json')['main_allowed']
for k in ['required_unconnected','wrong_net_actual_copper_contacts','targeted_material_violations','unexplained_transfer_changes']:assert load('smoke-independent.json')[k]==0
assert load('processes/smoke/check-drc-after.json')['counts']==dict(violations=0,incompletes=0)
for n,d in load('processes/smoke/record.json')['files'].items():assert h(E/'processes/smoke'/n)==d['sha256']
assert load('settings-comparison-before-main.json')['changed_fields']=={'detailedRouter':{'before':'off','after':'tiles'}}
for n,sha in load('source-manifest.json').items():assert h(T/'fab_router'/n)==sha,n
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=T/'fab_router').decode().strip()=='69cf598db98c136bff16bbe02bccdded95674b18'
assert not subprocess.check_output(['git','diff','HEAD','--','src','spec'],cwd=T/'fab_router').strip()
assert h(R/'.issue105-runtime/bun.zip')==load('installation.json')['bun_sha256']
assert subprocess.check_output([T/'bun/bun-linux-x64/bun','--version']).decode().strip()=='1.4.4'
assert not (E/'processes/main/result.json').exists() and not (E/'processes/main/out.ses').exists() and not (E/'processes/main/record.json').exists()
assert load('processes/main/effective-settings-before.json')['effectiveSettings']==load('settings-comparison-before-main.json')['new_effective_settings']
G=['git','--git-dir='+str(T/'git'),'--work-tree='+str(R)];base=subprocess.check_output(G+['rev-parse','origin/main']).decode().strip();rows=subprocess.check_output(G+['ls-tree','-r',base]).decode().splitlines()
for row in rows:
 meta,name=row.split('\t');data=(R/name).read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==meta.split()[2],name
subprocess.run(G+['read-tree',base],check=True);subprocess.run(G+['symbolic-ref','HEAD','refs/heads/issue-105-fab-router-detailed'],check=True);subprocess.run(G+['update-ref','refs/heads/issue-105-fab-router-detailed',base],check=True)
(E/'processes/main').rename(E/'processes/main-attempt-1-interrupted')
shutil.copyfile(E/'main-launch.json',E/'processes/main-attempt-1-interrupted/launch-original.json')
now=datetime.datetime.now(datetime.timezone.utc)
record=dict(resume_start_utc='2026-11-03T23:48:06+00:00',deadline_utc='2026-11-04T01:48:06+00:00',limit_seconds=7200,verified_utc=now.isoformat(),cause='Runtime restart: external infrastructure interruption, as reported by user; not a router outcome. No result.json, out.ses, or completion record existed.',authorization='User expressly authorized one recovery Main execution, with unchanged conditions; not settings exploration. Smoke and condition identification must not be repeated.',prior_attempt='processes/main-attempt-1-interrupted',main_complete_runs_before_resume=0,allowed_recovery_invocations=1,base_commit=base,baseline_files_unchanged=len(rows),src_spec_files_verified=len(load('source-manifest.json')),runtime='Restored /tmp symlinks to surviving Bun 1.4.4 and unchanged clone; no routing performed during setup.',original_evidence_sha256=manifest)
(E/'recovery-preflight.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='original_evidence_sha256'},indent=2))
# Preserve the existing harness byte for byte; only redirect its launch record to a new path.
script=(E/'run-router.py').read_text();assert script.count("(stage+'-launch.json')")==1
(E/'run-router-recovery.py').write_text(script.replace("(stage+'-launch.json')","(stage+'-recovery-launch.json')"))
