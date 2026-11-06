"""Read-only audit; default mode writes new final-verification/manifest evidence."""
import ast,csv,gzip,json,os,re,sys,zipfile
from pathlib import Path
from common import E,R,save,digest,now
verify='--verify-only' in sys.argv
skip='--skip-workspace-baseline' in sys.argv
report=R/'docs/issue-149-wing-silkscreen.md'
protected=json.loads(gzip.open(E/'protected-resume-hashes.json.gz','rt').read())
changed=[]
if not skip:
 for i,(rel,old) in enumerate(protected.items(),1):
  f=R/rel
  if 'link' in old:
   good=f.is_symlink() and os.readlink(f)==old['link']
  else:
   good=f.is_file() and not f.is_symlink() and digest(f)==old['sha256']
  if not good:changed.append(rel)
  if i%10000==0:print('protected paths checked',i,flush=True)
 assert not changed,changed
files=[p for p in E.rglob('*') if p.is_file()]
json_count=0;python_count=0;link_count=0
for f in files:
 if f.suffix=='.json':json.loads(f.read_text());json_count+=1
 if f.suffix=='.py':ast.parse(f.read_text(),filename=str(f));python_count+=1
for doc in [report,E/'README.md',E/'inputs/README.md']:
 for href in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
  if '://' in href or href.startswith('#'):continue
  assert (doc.parent/href.split('#')[0]).exists(),(doc,href)
  link_count+=1
provenance=json.loads((E/'inputs/provenance.json').read_text())
for item in provenance['files']:assert digest(E/item['path'])==item['sha256'] and item['original_byte_equal']
zip_checks=[]
for pitch in (16,17):
 d=E/f'{pitch}mm';idn=json.loads((d/'identity-check.json').read_text())
 pcb=d/f'wing-{pitch}mm-silk149.kicad_pcb';assert digest(pcb)==idn['derived_sha256']
 src=R/json.loads((d/'design-evidence.json').read_text())['source']
 s=src.read_bytes();v=pcb.read_bytes();idx=s.rfind(b')');tail=s[idx:]
 assert v[:idx]==s[:idx] and v[-len(tail):]==tail and len(v)>len(s)
 assert digest(src)==idn['source_sha256']
 assert src.with_suffix('.kicad_pro').read_bytes()==pcb.with_suffix('.kicad_pro').read_bytes()
 assert idn['only_new_F_SilkS_drawings'] and idn['all_native_geometry_equal']
 drc=json.loads((d/'drc.json').read_text())
 assert not drc['violations'] and not drc['unconnected_items']
 assert set(drc['included_severities'])=={'error','warning','exclusion'}
 assert drc['kicad_version']=='9.0.9'
 for job in ('drc','gerbers','drill','paste-reference'):
  record=json.loads((E/f'processes/{pitch}mm-{job}/record.json').read_text());assert record['exit_code']==0
  if job=='drc':assert {'--severity-all','--all-track-errors','--exit-code-violations'}.issubset(record['argv'])
 cam=json.loads((d/'cam-identity.json').read_text());assert cam['all_non_silk_graphic_objects_equal_to_issue147']
 mf=json.loads((d/'manufacturing-check.json').read_text());archive=E/mf['archive']
 assert digest(archive)==mf['archive_sha256'] and mf['printed_silk_dark_primitives']>100
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None and len(z.namelist())==9 and len(set(z.namelist()))==9
  assert set(z.namelist())=={x['name'] for x in mf['archive_members']}
  assert sum(x.endswith('.drl') for x in z.namelist())==2
  for item in mf['archive_members']:
   f=d/'gerber'/item['name'];assert z.read(item['name'])==f.read_bytes() and digest(f)==item['sha256']
 holes=list(csv.DictReader((d/'mounting-holes.csv').open()));assert len(holes)==4
 assert all(float(q['diameter_mm'])==2.2 and float(q['keepout_diameter_mm'])==5 for q in holes)
 for image in ('front-silkscreen.png','all-layers.png','top-copper-holes.png','bottom-copper-holes.png'):
  f=d/'preview-review'/image;assert f.read_bytes().startswith(b'\x89PNG\r\n\x1a\n') and f.stat().st_size>10000
 zip_checks.append(dict(pitch_mm=pitch,sha256=digest(archive),members=9,crc_ok=True))
assert json.loads((E/'visual-review.json').read_text())['both_pitches_reviewed']
if verify:
 manifest=json.loads((E/'manifest.json').read_text())
 for rel,sha in manifest['sha256'].items():assert digest(R/rel)==sha,rel
 actual={str(p.relative_to(R)) for p in E.rglob('*') if p.is_file() and p.name not in ('manifest.json','publication.json')}
 actual.add(str(report.relative_to(R)))
 assert actual==set(manifest['sha256']),('manifest file inventory changed',actual.symmetric_difference(manifest['sha256']))
 print('Manifest verified:',len(actual),'files',flush=True)
else:
 save(E/'final-verification.json',dict(utc=now(),result='pass',protected_paths=len(protected),protected_paths_checked=0 if skip else len(protected),protected_changed=changed,workspace_baseline_skipped=skip,python_ast_files=python_count,json_parsed_files=json_count,local_links=link_count,source_and_project_unchanged=True,drc_both_pitches_zero=True,archives=zip_checks,manufacturer_upload=False,order=False,payment=False,merge=False))
 paths=sorted([p for p in E.rglob('*') if p.is_file() and p.name not in ('manifest.json','publication.json')]+[report])
 save(E/'manifest.json',dict(utc=now(),exclusions=['manifest.json (self)','publication.json (later publication record)'],sha256={str(p.relative_to(R)):digest(p) for p in paths}))
print('Audit passed; protected changed=0; workspace baseline skipped='+str(skip),flush=True)
