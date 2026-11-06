"""Audit existing deliverables only; --write also emits final audit and manifest."""
import ast
import datetime
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from common import E, R, now, digest, save

G=['git','--git-dir='+str(R/'.issue147-runtime/git'),'--work-tree='+str(R)]
report=R/'docs/issue-147-wing-order-prep.md'
start=json.loads((E/'resume-start.json').read_text())
for name,h in start['inherited_file_hashes'].items():
    assert digest(R/name)==h, name
json_files=list(E.rglob('*.json'))
for p in json_files:json.loads(p.read_text())
py_files=list(E.glob('*.py'))
for p in py_files:ast.parse(p.read_text(),filename=str(p))
svg_files=list(E.rglob('*.svg'))
for p in svg_files:ET.parse(p)
links=0
for p in [report,E/'README.md']:
    for raw in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if '://' in raw or raw.startswith('#'):continue
        target=raw.split('#')[0]
        assert (p.parent/target).exists(),(p,target)
        links+=1
checks=json.loads((E/'manufacturing-checks.json').read_text())
visual=json.loads((E/'visual-review.json').read_text())
for check in checks:
    pitch=check['pitch_mm']
    pre=json.loads((E/f'{pitch}mm'/'preflight.json').read_text())
    assert digest(R/pre['source'])==check['source_sha256']
    archive=E/check['archive']
    assert digest(archive)==check['archive_sha256']
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.namelist())==9
        assert set(z.namelist())=={m['name'] for m in check['archive_members']}
        for member in check['archive_members']:
            contents=z.read(member['name'])
            assert hashlib.sha256(contents).hexdigest()==member['sha256']
            assert contents==(E/f'{pitch}mm'/'gerber'/member['name']).read_bytes()
    review=next(v for v in visual['reviews'] if v['pitch_mm']==pitch)
    assert review['no_unexplained_anomalies']
    for item in review['files']:assert digest(E/item['path'])==item['sha256']
base=json.loads((E/'start.json').read_text())['base']
status=subprocess.check_output(G+['diff','--cached','--name-status',base],text=True)
entries=[line.split('\t',1) for line in status.splitlines()]
assert entries and all(s=='A' for s,p in entries),entries
assert all(p=='docs/issue-147-wing-order-prep.md' or p.startswith('hardware/kicad/qualification/issue-147-wing-order-prep/') for s,p in entries)
assert not subprocess.check_output(G+['diff','--name-only'],text=True).strip()
whitespace=subprocess.run(G+['diff','--cached','--check',base],text=True,capture_output=True)
allowed='hardware/kicad/qualification/issue-147-wing-order-prep/common.py:61: new blank line at EOF.'
assert whitespace.stdout.strip() in ('',allowed),whitespace.stdout
end=datetime.datetime.now(datetime.timezone.utc)
first=datetime.datetime.fromisoformat('2026-11-05T07:10:33+00:00')
assert (end-first).total_seconds()<7200
result=dict(utc=now(),resume_start_utc=first.isoformat(),elapsed_seconds=(end-first).total_seconds(),
 timebox_seconds=7200,within_timebox=True,inherited_files_unchanged=len(start['inherited_file_hashes']),
 original_baseline_audit='resumption-verification.json: 45864 original paths, zero changes',
 json_parsed=len(json_files),python_syntax_parsed=len(py_files),svg_xml_parsed=len(svg_files),local_markdown_links_checked=links,
 archives_crc_and_member_hashes=True,source_and_visual_hashes=True,staged_only_additions=True,staged_scope_correct=True,
 staged_count_before_this_record=len(entries),unstaged_tracked_changes=0,
 whitespace=dict(exit_code=whitespace.returncode,output=whitespace.stdout,disposition='Only the inherited common.py extra EOF blank line is retained byte-identical under the no-existing-edits constraint. No new resumed-source whitespace findings.'),
 no_cad_regeneration_in_resumed_run=True,no_manufacturer_upload_contact_order_payment=True,no_merge=True,
 ci_note='Local manufacturing checks only. Remote CI status is not implied.')
if '--write' in sys.argv:
    assert not (E/'final-verification.json').exists()
    save(E/'final-verification.json',result)
    paths=[report]+sorted(p for p in E.rglob('*') if p.is_file() and p.name not in ('manifest.json','publication.json'))
    assert not (E/'manifest.json').exists()
    save(E/'manifest.json',dict(utc=now(),algorithm='SHA256',exclusions=['manifest.json (self)','publication.json (added after publication attempt)'],
         files={str(p.relative_to(R)):digest(p) for p in paths}))
else:
    manifest=E/'manifest.json'
    if manifest.exists():
        for name,h in json.loads(manifest.read_text())['files'].items():assert digest(R/name)==h,name
print(json.dumps(result,indent=2,ensure_ascii=False))
