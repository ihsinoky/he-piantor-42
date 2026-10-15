from prepare import *
J=Path('/home/codespace/java/21.0.12+1-ms')
f=json.loads((OLD/'evidence/runtime-freeze.json').read_text())
assert all(digest(J/p)==h for p,h in f['java_file_sha256'].items())
run('router-download',['curl','-fL',f['router_url'],'-o',str(BASE/'freerouting.jar')],BASE,180)
assert digest(BASE/'freerouting.jar')==f['router_sha256']
run('router-help',[str(J/'bin/java'),'-Djava.awt.headless=true','-jar',str(BASE/'freerouting.jar'),'-help'],BASE,60)
save(ROOT/'evidence/router-reuse.json',dict(prior=str((OLD/'evidence/runtime-freeze.json').relative_to(REPO)),java_all_files_hash_match=True,router_sha256=digest(BASE/'freerouting.jar'),java_version='Microsoft 21.0.12+1-ms',version='2.1.0',full_environment_reconstruction_qualified=False))
