"""Read-only evidence, chronology, scope and protected-byte checks after STOP."""
import base64
import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
R=ROOT/'evidence'
ALLOWED={'docs/native-kicad-authoring-feasibility.md','docs/eda-path-history.md','docs/development-workflow.md','docs/project-status.md','task/data/project-status.js'}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def raw(d,name):return (d/name).read_bytes() if (d/name).exists() else gzip.decompress((d/(name+'.gz')).read_bytes())
def verify_record(record,out,err):
    assert record['exit_code'] is not None and record['end_utc'] is not None
    assert hashlib.sha256(out).hexdigest()==record['stdout_sha256']
    assert hashlib.sha256(err).hexdigest()==record['stderr_sha256']
    assert record['display_unset'] is True
    for a in record['artifacts']:
        if a['present']:assert sha(R/a['saved_path'])==a['sha256']

if __name__=='__main__':
    assert not list(ROOT.rglob('*.pyc'))
    for name,digest in read(R/'integrity.json')['sha256'].items():assert sha(ROOT/name)==digest,name
    errors=[];files=json.loads(gzip.decompress((R/'starting-files.json.gz').read_bytes()))
    for name,digest in files.items():
        if name not in ALLOWED:assert sha(REPO/name)==digest,name
    changed=subprocess.check_output(['git','diff','--name-only','67b0523b513742fa7e3cc2f09b710a79eef2e6ac'],cwd=REPO).decode().splitlines()
    untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=REPO).decode().splitlines()
    for name in changed+untracked:assert name in ALLOWED or name.startswith('hardware/kicad/qualification/eda-004e/'),name
    stop=read(R/'stop-decision.json');assert stop['initial_fixture_acceptance']=='FAIL'
    count=0;elapsed=0
    for d in (R/'processes').iterdir():
        rec=read(d/'record.json');verify_record(rec,raw(d,'stdout'),raw(d,'stderr'));count+=1;elapsed+=rec['elapsed_seconds']
        if rec['start_utc']>stop['utc']:assert d.name.startswith(('verify-','record-','git-','ci-')),d.name
    archive=R/'package-extractions.json.gz';assert sha(archive)==read(R/'package-extractions-index.json')['sha256']
    records=json.loads(gzip.decompress(archive.read_bytes()));assert len(records)==read(R/'package-extractions-index.json')['count']
    for item in records:
        rec=item['record'];verify_record(rec,base64.b64decode(item['stdout_base64']),base64.b64decode(item['stderr_base64']));assert rec['exit_code']==0;elapsed+=rec['elapsed_seconds']
    freeze=read(R/'fixture-freeze.json');assert sha(ROOT/'fixture.json')==freeze['fixture_sha256'];assert sha(ROOT/'author.py')==freeze['author_sha256_before_first_run']
    assert read(R/'processes/initial-create/record.json')['start_utc']>freeze['frozen_utc']
    assert sha(ROOT/'library/Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod')==freeze['official_footprint_sha256']
    a=read(R/'processes/initial-reload-resave-corrected/before.json');b=read(R/'processes/initial-resaved-inspect/after.json');assert a==b
    g=[x for fp in b['footprints'] if fp['reference']=='U1' for x in fp['pads'] if x['number']=='1'];assert len(g)==3 and all(x['net']=='GND' for x in g)
    assert b['copper_layers']==2 and b['thickness_mm']==1.2 and len(b['tracks'])==2
    drc=read(R/'processes/initial-drc/drc.json');assert len(drc['unconnected_items'])==2
    assert sorted(x['type'] for x in drc['violations'])==['lib_footprint_issues','silk_over_copper']
    assert all(x['severity']=='warning' for x in drc['violations'])
    descriptions=[x['items'] for x in drc['unconnected_items']]
    assert sum(any('Pad 2 [GND] of R1' in i['description'] for i in x) and any('Track [GND]' in i['description'] for i in x) for x in descriptions)==1
    assert sum(any('Pad 1 [SIG] of R1' in i['description'] for i in x) and any('Pad 2 [SIG] of U1' in i['description'] for i in x) for x in descriptions)==1
    cmp=read(R/'comparison.json');assert cmp['fresh']=='NOT ENTERED' and cmp['fresh_semantics_equal'] is None and cmp['effective_rules']=='UNQUALIFIED'
    refs=read(R/'references.json');assert refs['commit']=='67b0523b513742fa7e3cc2f09b710a79eef2e6ac'
    for name,digest in refs['files'].items():assert sha(REPO/name)==digest
    for p in [REPO/'docs/native-kicad-authoring-feasibility.md',REPO/'docs/eda-path-history.md',ROOT/'README.md']:
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' not in link and not link.startswith('#'):assert (p.parent/link.split('#')[0]).exists(),(p,link)
    print(json.dumps({'report_validation':'PASS','protected_starting_files_checked':len(files)-len(ALLOWED),'process_records_checked':count+len(records),'sum_process_elapsed_seconds_overlaps_session':round(elapsed,3),'planned_unconnected':2,'unexpected_warnings':2,'technical_classification':stop['classification'],'fresh':'NOT ENTERED'},indent=2))
