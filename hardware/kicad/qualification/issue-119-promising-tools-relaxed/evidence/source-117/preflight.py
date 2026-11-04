from common import *
base=subprocess.check_output(['git','--git-dir='+GIT,'rev-parse','origin/main'],text=True).strip()
rows=subprocess.check_output(['git','--git-dir='+GIT,'ls-tree','-r','-z',base]).split(b'\0')
bad=[];count=0
for row in rows:
 if not row:continue
 meta,name=row.split(b'\t');mode,typ,h=meta.decode().split();p=R/os.fsdecode(name)
 if typ!='blob':continue
 data=p.read_bytes();actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 if actual!=h:bad.append(str(p.relative_to(R)))
 count+=1
assert not bad,bad
checks={}
for issue,filename,root in [('113','source-manifest.json',KRT),('113','inspection-runtime-hashes.json',RT),('103','source-manifest.json',FAB)]:
 folder={'113':'issue-113-kicad-routing-tools-falsification','103':'issue-103-fab-router-falsification'}[issue]
 manifest=json.loads((R/'hardware/kicad/qualification'/folder/'evidence'/filename).read_text())
 bad={p:dict(expected=h,actual=sha(root/p) if (root/p).exists() else None) for p,h in manifest.items() if not (root/p).exists() or sha(root/p)!=h}
 checks[issue+'-'+filename]=dict(files=len(manifest),mismatches=bad)
 assert not bad,checks
binary=list(KRT.rglob('grid_router*.so'));assert len(binary)==1 and sha(binary[0])=='4411ccf3f074f519d8d69be29ac58b46ca7c4c2fe4f4be889d253d40996c2c0f'
save(E/'preflight.json',dict(utc=utc(),base=base,base_files=count,base_mismatches=[],checks=checks,krt_binary_sha256=sha(binary[0]),krt_commit=subprocess.check_output(['git','-C',str(KRT),'rev-parse','HEAD'],text=True).strip(),fab_commit=subprocess.check_output(['git','-C',str(FAB),'rev-parse','HEAD'],text=True).strip(),start_utc='2026-11-04T09:05:00+00:00',stage0_deadline_utc='2026-11-04T10:35:00+00:00',deadline_utc='2026-11-04T12:05:00+00:00'))
probe="""import pcbnew as p
b=p.BOARD();s=b.GetDesignSettings()
for o in [b,s,p.ZONE(b),p.ZONE_FILLER]:print(type(o),[x for x in dir(o) if any(v in x.lower() for v in ['stack','layer','fill','poly','outline','net','thermal','island'])])
print(p.In1_Cu,p.In2_Cu,p.LT_POWER,p.LT_SIGNAL)
"""
assert run('api-probe',['/usr/bin/python3','-c',probe])==0
