from common import *
import collections
src=R/'hardware/kicad/qualification/issue-131-wing-condition-search/evidence/KRT-source-hashes.json';hashes=json.loads(src.read_text());bad={x:dict(expected=h,actual=digest(K/x) if (K/x).exists() else None) for x,h in hashes.items() if not (K/x).exists() or digest(K/x)!=h};assert not bad
assert len(hashes)==2055
G=['git','--git-dir='+str(T/'git'),'--work-tree='+str(R)]
base='ac74ef964e2c64a5dfde1f67af8f440e539b317d'
changed=subprocess.check_output(G+['diff','--name-only',base,'--'],text=True).splitlines();assert not changed,changed
save(E/'runtime-check.json',dict(utc=now(),source_files=len(hashes),mismatches=bad,source_manifest_sha256=digest(src),grid_router_sha256=digest(K/'rust_router/grid_router.so'),kicad_cli_sha256=digest(B/'kicad/usr/bin/kicad-cli'),no_prior_tracked_files_modified=True,prior_branch_head=base,decisions_unchanged=True,work_repo=str(R),git_metadata=str(T/'git')))
print('Prior tracked files unchanged; KRT 2055 source hashes identical')
