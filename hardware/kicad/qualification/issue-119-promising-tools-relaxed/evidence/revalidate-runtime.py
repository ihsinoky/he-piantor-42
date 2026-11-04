from common import *
checks={}
for issue,name,root in [('113','source-manifest.json',KRT),('113','inspection-runtime-hashes.json',RT),('103','source-manifest.json',FAB)]:
 prior=next((R/'hardware/kicad/qualification').glob('issue-'+issue+'-*'))/'evidence'/name
 rows=json.loads(prior.read_text());bad=[p for p,h in rows.items() if sha(root/p)!=h];assert not bad,bad
 checks[issue+'-'+name]=dict(files=len(rows),mismatches=bad,manifest_sha256=sha(prior))
commits={}
for name,root,expected in [('fab',FAB,'69cf598db98c136bff16bbe02bccdded95674b18'),('krt',KRT,'c64c0db25e6cf23afa6769ee05665c7ea22b3ff2')]:
 actual=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip();assert actual==expected
 assert not subprocess.check_output(['git','-C',str(root),'diff','--name-only']);commits[name]=actual
binary=list(KRT.rglob('grid_router*.so'));assert len(binary)==1;assert sha(binary[0])=='4411ccf3f074f519d8d69be29ac58b46ca7c4c2fe4f4be889d253d40996c2c0f'
jar=Path('/home/hatch/workspace/tools/issue-93/freerouting-2.5.0.jar');assert sha(jar)=='f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7'
save(E/'runtime-revalidation.json',dict(utc=utc(),checks=checks,commits=commits,krt_binary_sha256=sha(binary[0]),freerouting_jar_sha256=sha(jar)))
