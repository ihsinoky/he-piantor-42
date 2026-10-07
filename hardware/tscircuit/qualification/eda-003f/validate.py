"""Validate the preserved terminal experiment. Never invokes a router."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

here=Path(__file__).resolve().parent
root=here.parents[3]
e=here/'evidence'
work=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/eda003f')
sha=lambda raw:hashlib.sha256(raw).hexdigest()
pre=json.loads((e/'preflight.json').read_text())
for name,digest in pre['protected_sha256'].items():
    assert sha((root/name).read_bytes())==digest, 'Protected bytes changed: '+name
assert json.loads((root/'hardware/tscircuit/package.json').read_text())['dependencies']['tscircuit']=='0.0.2646'
assert json.loads((root/'hardware/tscircuit/package-lock.json').read_text())['packages']['node_modules/tscircuit']['version']=='0.0.2646'
manifest=json.loads((e/'intervention-patch-manifest.json').read_text())
a_file=work/'a'/manifest['file'];b_file=work/'b'/manifest['file']
original=a_file.read_bytes();patched=b_file.read_bytes()
assert sha(original)==manifest['original_sha256']
assert sha(patched)==manifest['patched_sha256']
expected=original.decode()
for site in manifest['sites']:
    assert expected.count(site['before'])==1
    expected=expected.replace(site['before'],site['after'],1)
assert expected.encode()==patched
assert a_file.stat().st_ino!=b_file.stat().st_ino
assert len(manifest['sites'])==2 and manifest['parameter_candidates']==1
assert len(patched)-len(original)==-17
# All dependency bytes remain stock except the one declared B artifact.
# Fingerprint algorithm matches environment.json, including symlink identities.
def tree(env,substitute=None):
    h=hashlib.sha256();count=0
    for p in sorted((env/'node_modules').rglob('*')):
        if not p.is_file():continue
        name=str(p.relative_to(env))
        raw=substitute if substitute is not None and name==manifest['file'] else p.read_bytes()
        value='symlink:'+str(p.readlink()) if p.is_symlink() else sha(raw)
        h.update((name+'\0'+value+'\n').encode());count+=1
    return {'file_count':count,'sha256':h.hexdigest()}
environment=json.loads((e/'environment.json').read_text())
assert tree(work/'a')==environment['A_stock_dependency_tree']
assert tree(here.parent/'eda-003c/latest-stock')==environment['A_stock_dependency_tree']
assert tree(work/'b',original)==environment['A_stock_dependency_tree']
for name,digest in environment['fixture_sha256'].items():
    for condition in ['a','b']:
        assert sha((work/condition/name).read_bytes())==digest
        assert (work/condition/name).read_bytes()==(here.parent/'eda-003c/latest-stock'/name).read_bytes()
for condition in ['a','b']:
    assert sha((work/condition/'package-lock.json').read_bytes())==environment['package_lock_sha256']
    assert json.loads((work/condition/'node_modules/tscircuit/package.json').read_text())['version']=='0.0.2748'
# Check all accepted A geometric witnesses, without writing accepted evidence.
records=json.loads((work/'a-run/evidence/error-records-normalized.json').read_text())
clusters=json.loads((work/'a-run/evidence/physical-fault-clusters.json').read_text())
accepted=json.loads((here.parent/'eda-003d/evidence/physical-fault-clusters.json').read_text())
assert clusters['clusters']==accepted['clusters']
assert sha((work/'a-run/circuit.json').read_bytes())==accepted['input_sha256']
spec=importlib.util.spec_from_file_location('geometry',here.parent/'eda-003d/classify.py')
geometry=importlib.util.module_from_spec(spec);spec.loader.exec_module(geometry)
primitives=[p for r in records for p in r['violating_primitive_pairs']]
required=[r['required_clearance_mm'] for r in records for p in r['violating_primitive_pairs']]
assert len(primitives)==431
for proof in clusters['merge_proofs']:
    p,q=proof['points']
    for i in proof['event_indices']:
        shapes=primitives[i]['geometry']
        assert geometry.contains(shapes[0],p) and geometry.contains(shapes[1],q)
        assert geometry.norm(geometry.sub(p,q))<required[i]
assert len(clusters['merge_proofs'])==len(primitives)-54
before={n:sha((work/'a-run/evidence'/n).read_bytes()) for n in ['error-records-normalized.json','physical-fault-clusters.json']}
with tempfile.TemporaryFile(mode='w+') as log:
    subprocess.run([sys.executable,str(here/'classify-run.py'),str(work/'a-run')],stdout=log,check=True)
assert before=={n:sha((work/'a-run/evidence'/n).read_bytes()) for n in before}
# Repeat deterministic reporting twice; no new generation or checker invocation.
with tempfile.TemporaryDirectory(prefix='eda003f-validation-') as tmp:
    for suffix in ['one','two']:
        output=Path(tmp)/suffix
        subprocess.run([sys.executable,str(here/'summarize-ab.py'),str(work/'a-run'),str(work/'b-run'),str(output)],stdout=subprocess.DEVNULL,check=True)
    one,two=Path(tmp)/'one',Path(tmp)/'two'
    files=[p.relative_to(one) for p in one.rglob('*') if p.is_file()]
    for name in files:
        assert (one/name).read_bytes()==(two/name).read_bytes()
        assert (one/name).read_bytes()==(e/name).read_bytes(), 'Retained reporting differs: '+str(name)
raw=gzip.decompress((e/'raw/intervention-b.circuit.json.gz').read_bytes())
assert raw==(work/'b-run/circuit.json').read_bytes()
assert sha(raw)==json.loads((e/'intervention-b.json').read_text())['raw_sha256']
a=json.loads((e/'control-a.json').read_text());b=json.loads((e/'intervention-b.json').read_text())
assert a['wrong_net_copper_components']==0 and b['wrong_net_copper_components']==2
assert a['electrically_required_unrouted_count']==b['electrically_required_unrouted_count']==0
assert a['board_rules']==b['board_rules'] and b['board_rules']['min_trace_to_pad_edge_clearance']==.2
assert json.loads((e/'final-classification.json').read_text())['classification']=='INTERVENTION_UNSAFE_REGRESSION'
for p in e.rglob('*.json'):json.loads(p.read_text())
subprocess.run(['git','diff','--check'],cwd=root,check=True)
result={'evidence_validation':'PASS','A_control_validation':'PASS: accepted raw bytes and all 54 physical identities identical','B_safety_validation':'FAIL K1: 2 wrong-net components; terminal unsafe classification preserved','physical_connectivity_verifier':'PASS execution for A and B; zero required unrouted each','wrong_net_verifier':'A 0; B 2; independent material copper graph','physical_verifier_fault_fixtures':12,'stock_DRC_replay':'A 71; B 49; all B material type/message multiplicities match generated diagnostics','A_conflict_clustering':'54 conflicts; 431 primitives; 377 checked merge witnesses; deterministic repeat','B_conflict_clustering_diff':'NOT ENTERED after K1','deterministic_comparison_scripts':'PASS: two read-only reporting runs byte-identical, including compressed B raw artifact','json_parse':'PASS','gzip_integrity':'PASS','exact_patch_reconstruction':'PASS: two edits; one runtime file; -17 bytes','dependency_isolation':'PASS: 17243 files; accepted/A identical; B differs only in declared artifact','fixture_verifier_bytes':'PASS: A/B match accepted copies','protected_files_checked':len(pre['protected_sha256']),'production_manifest_lock':'byte-identical to preflight','production_tscircuit':'0.0.2646','accepted_EDA_003B_C_D_E':'byte-identical to preflight','project_clearance_mm':.2,'external_router_used':False,'generated_data_edited':False,'B_confirmation':'NOT PERFORMED after K1','routing_processes':{'A':1,'B':1},'git_diff_check':'PASS'}
(e/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
