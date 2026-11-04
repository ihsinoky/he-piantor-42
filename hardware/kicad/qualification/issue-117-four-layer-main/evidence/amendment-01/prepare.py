from helpers import *
import shutil
save(A/'start.json',dict(start_utc='2026-11-04T09:22:54+00:00',smoke_deadline_utc='2026-11-04T09:52:54+00:00',deadline_utc='2026-11-04T11:22:54+00:00',prior_commit='7917d82',amendment_precedence=True))
manifest=json.loads((E/'manifest.json').read_text());rows={}
for p in sorted((E/'inputs/main').iterdir()):
 if not p.is_file():continue
 relative=str(p.relative_to(E));h=sha(p)
 committed=subprocess.check_output(['git','--git-dir='+GIT,'show','HEAD:'+str(p.relative_to(R))])
 assert p.read_bytes()==committed
 assert h==manifest[relative]['sha256']
 rows[relative]=dict(sha256=h,bytes=p.stat().st_size,byte_identical_to_prior_commit=True,prior_manifest_match=True)
assert sha(E/'inputs/main/main.kicad_pcb')==json.loads((E/'native-equivalence.json').read_text())['inputs']['main']['four_layer_pcb_sha256']
checks={}
for issue,filename,root in [('113','source-manifest.json',KRT),('113','inspection-runtime-hashes.json',RT),('103','source-manifest.json',FAB)]:
 folder={'113':'issue-113-kicad-routing-tools-falsification','103':'issue-103-fab-router-falsification'}[issue]
 hashes=json.loads((R/'hardware/kicad/qualification'/folder/'evidence'/filename).read_text())
 bad=[p for p,h in hashes.items() if not (root/p).exists() or sha(root/p)!=h];assert not bad,bad
 checks[issue+'-'+filename]=dict(files=len(hashes),mismatches=bad)
assert sha(next(KRT.rglob('grid_router*.so')))=='4411ccf3f074f519d8d69be29ac58b46ca7c4c2fe4f4be889d253d40996c2c0f'
save(A/'main-reuse-and-runtime-revalidation.json',dict(utc=utc(),main_rebuilt=False,files=rows,runtime=checks))
assert run('amend01-prepare-smoke',['/usr/bin/python3',A/'prepare-smoke.py'])==0
assert run('amend01-smoke-dsn-equivalence',['/usr/bin/python3',A/'check-smoke-dsn.py'])==0
assert run('amend01-smoke-native-readback',['/usr/bin/python3',R/'hardware/kicad/qualification/eda-004g/resume-02/read-pcb.py',A/'inputs/smoke/main.kicad_pcb',A/'inputs/smoke/snapshot.json'])==0
before=json.loads((R/'hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/evidence/inputs/smoke/snapshot.json').read_text())
after=json.loads((A/'inputs/smoke/snapshot.json').read_text());changes=delta(before,after)
assert {x['path'] for x in changes}=={'/layers','/zones'}
assert run('amend01-smoke-fab-parse',[RT/'bun/bun-linux-x64/bun',E/'read-fab.ts',FAB,A/'inputs/smoke/corrected.dsn',A/'inputs/smoke/fab-readback.json'])==0
f=json.loads((A/'inputs/smoke/fab-readback.json').read_text());assert [s['role'] for s in f['stack']]==['signal','plane','signal','signal']
assert next(n['name'] for n in f['nets'] if n['id']==f['stack'][1]['planeNet'])=='N'
assert all(g['usable']==[0,2,3] for g in f['netGroups'])
assert all(all(v/f['frame']['luPerUm']==200 for v in g['widthBySheet']) for g in f['netGroups'])
save(A/'equivalence-gate.json',dict(utc=utc(),pass_equivalence=True,smoke_deviation='In1 plane assigned to existing sole net N under amendment 01; no net addition or rename. Main plane remains GND.',smoke_native_snapshot_changes=changes,smoke_DSN_exact_projected_AST_equal=True,main_previous_gate_reused=True,main_byte_hash_revalidated=True))
print('EQUIVALENCE PASS')
