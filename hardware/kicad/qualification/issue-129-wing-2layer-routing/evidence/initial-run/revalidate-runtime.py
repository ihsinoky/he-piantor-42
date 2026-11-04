"""Compare reused tool/runtime bytes against committed historical provenance."""
from common import *
checks={}
old=R/'hardware/kicad/qualification/issue-113-kicad-routing-tools-falsification/evidence'
for name,root in [('source-manifest.json',T/'KiCadRoutingTools'),('inspection-runtime-hashes.json',T)]:
 rows=json.loads((old/name).read_text());bad={f:dict(expected=v,actual=digest(root/f) if (root/f).exists() else None) for f,v in rows.items() if not (root/f).exists() or digest(root/f)!=v};assert not bad,bad;checks[name]=dict(files=len(rows),mismatches=bad)
for name,expected in [('fab_router','69cf598db98c136bff16bbe02bccdded95674b18'),('KiCadRoutingTools','c64c0db25e6cf23afa6769ee05665c7ea22b3ff2')]:
 root=T/name;head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip();assert head==expected;assert not subprocess.check_output(['git','-C',str(root),'diff','--name-only']);manifest={}
 for f in subprocess.check_output(['git','-C',str(root),'ls-files','-z']).decode().split('\0'):
  if f and (root/f).is_file():manifest[f]=digest(root/f)
 save(E/(name+'-source-hashes.json'),manifest);checks[name]=dict(commit=head,tracked_source_unchanged=True,files=len(manifest),source_backup='/home/hatch/workspace/goals/he-piantor-42-keyboard-pmo/hidden_files/clone-backup-20261105',remote=subprocess.check_output(['git','-C',str(root),'remote','get-url','origin'],text=True).strip())
binary=T/'KiCadRoutingTools/rust_router/grid_router.so';assert digest(binary)=='4411ccf3f074f519d8d69be29ac58b46ca7c4c2fe4f4be889d253d40996c2c0f';checks['krt_binary']=dict(sha256=digest(binary))
checks['bun']={str(f.relative_to(T)):digest(f) for f in (T/'bun').rglob('bun') if f.is_file()};checks['kicad_cli']=dict(sha256=digest(T/'kicad/usr/bin/kicad-cli'))
save(E/'runtime-revalidation.json',dict(utc=now(),checks=checks))
