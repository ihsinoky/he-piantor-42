"""Resolve full settings without running the router; freeze Main gate before any routing."""
import pathlib,subprocess,json,hashlib,datetime,re,difflib
E=pathlib.Path(__file__).resolve().parent;R=E.parents[4];T=pathlib.Path('/tmp/issue-105-fab-router');B=R/'hardware/kicad/qualification/issue-103-fab-router-falsification/evidence'
P=E/'main-preflight';P.mkdir(exist_ok=False)
source=R/'hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-restore/corrected.dsn'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2'
argv=[T/'bun/bun-linux-x64/bun','run',E/'driver.ts',T/'fab_router',source,P,'readback-only']
r=subprocess.run(list(map(str,argv)),capture_output=True,text=True);(P/'stdout').write_text(r.stdout);(P/'stderr').write_text(r.stderr);assert r.returncode==0,r.stderr
new=json.loads((P/'effective-settings-before.json').read_text())['effectiveSettings'];old=json.loads((B/'processes/main/result.json').read_text())['report']['effectiveSettings']
keys=sorted(set(old)|set(new));diff={k:dict(before=old.get(k),after=new.get(k)) for k in keys if old.get(k)!=new.get(k)}
assert diff=={'detailedRouter':{'before':'off','after':'tiles'}},diff
# Include unset optional fields as explicit state, not substituted runtime defaults.
spec=(T/'fab_router/spec/types/settings.ts').read_text().split('export interface RouteSettings {')[1].split('\n}')[0]
fields=re.findall(r'\b(\w+)\??:',re.sub(r'/\*.*?\*/|//[^\n]*','',spec,flags=re.S));fields=list(dict.fromkeys(fields))
allfields={k:dict(before=old[k] if k in old else '<unset>',after=new[k] if k in new else '<unset>',changed=old.get(k)!=new.get(k)) for k in sorted(set(fields)|set(keys))}
(E/'settings-comparison-before-main.json').write_text(json.dumps(dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),routing_calls=0,baseline_effective_settings=old,new_effective_settings=new,changed_fields=diff,all_declared_fields=allfields,argv=list(map(str,argv)),main_allowed_configuration=True),indent=2)+'\n')
(E/'driver-diff.patch').write_text(''.join(difflib.unified_diff((B/'driver.ts').read_text().splitlines(True),(E/'driver.ts').read_text().splitlines(True),fromfile='issue103/driver.ts',tofile='issue105/driver.ts')))
print(json.dumps(diff))
