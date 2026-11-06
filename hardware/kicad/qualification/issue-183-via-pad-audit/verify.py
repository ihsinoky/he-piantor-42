"""Validate saved evidence and input identity, without rerunning geometry audits."""
from pathlib import Path
import collections,csv,gzip,hashlib,json,math,subprocess
E=Path(__file__).resolve().parent

def read(path):return json.loads(path.read_text())
def digest(raw):return hashlib.sha256(raw).hexdigest()
def csv_equal(path,rows):
    reader=csv.DictReader(path.open());actual=list(reader)
    expected=[]
    for r in rows:
        values={k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else '' if v is None else str(v) for k,v in r.items()}
        expected.append({k:values.get(k,'') for k in reader.fieldnames})
    assert actual==expected,path

def verify():
    checks=[]
    sources=read(E/'sources.json')
    for s in sources:
        w=E/s['board'];raw=gzip.decompress((E/s['snapshot']).read_bytes())
        assert digest(raw)==s['sha256']
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==s['blob']
        # Reads the immutable git object, never a board on a mutable source ref.
        original=subprocess.check_output(['git','show',s['commit']+':'+s['path']],cwd=E)
        assert original==raw
        rows=read(w/'all-vias.json');summary=read(w/'summary.json');pads=read(w/'pads.json')
        assert summary['source_sha256']==s['sha256']
        assert len(rows)==summary['total_vias']==len({r['uuid'] for r in rows})
        assert len(pads)==summary['copper_pads']
        assert dict(collections.Counter(r['classification'] for r in rows))==summary['classification_counts']
        pairs=[h for r in rows for h in r['hits']]
        assert len(pairs)==summary['pad_hit_pairs']
        assert len({h['pad_uuid'] for h in pairs})==summary['unique_hit_pads']
        assert sum(r['classification']!='none' for r in rows)==summary['overlapping_vias']
        assert sum(not r['passes_0p10'] for r in rows)==summary['violates_0p10']
        assert sum(r['classification']=='none' and not r['passes_0p10'] for r in rows)==summary['nonoverlap_below_0p10']
        assert min(r['min_annulus_gap_mm'] for r in rows)==summary['min_annulus_gap_mm']
        assert min(r['min_physical_gap_mm'] for r in rows)==summary['min_physical_gap_mm']
        for kind in ['mounted','testpad']:
            assert sum(kind in r['hit_kinds'] for r in rows)==summary['overlapping_vias_by_pad_kind'][kind]
        for r in rows:
            assert r['diameter_mm']==0.6 and r['drill_mm']==0.3
            assert r['passes_0p10']==(r['min_annulus_gap_mm']>=0.1-1e-12)
            assert r['min_physical_gap_mm']==max(0,r['min_annulus_gap_mm'])
            c=next((c for c in ['center','drill-edge','annulus-only'] if any(h['classification']==c for h in r['hits'])),'none')
            assert r['classification']==c
        csv_equal(w/'all-vias.csv',[{k:v for k,v in r.items() if k!='hits'} for r in rows])
        csv_equal(w/'pad-hits.csv',pairs)
        probes=read(w/'move-probes.json');move=read(w/'move-summary.json');native=read(w/'move-native-check.json')
        assert move['method']=='independent-probe-v2-mm-anchors'
        assert move['source_sha256']==native['source_sha256']==s['sha256']
        assert len(probes)==move['violating_vias']==summary['violates_0p10']
        assert {q['via_uuid'] for q in probes}=={r['uuid'] for r in rows if not r['passes_0p10']}
        assert dict(collections.Counter(q['status'] for q in probes))==move['status_counts']
        assert native['checked_vias']==len(probes) and native['stub_failures']==0
        assert {q['via_uuid'] for q in native['checks']}=={q['via_uuid'] for q in probes}
        for q in probes:
            assert q['tested_positions']==4320
            if s['board'].startswith('wing-') and q['net'] in ['HALL_5V','GND']:
                assert all(a['width_mm']>=0.3 for a in q['anchors'] if a['kind']=='pad')
            if q['status']=='candidate-with-straight-local-stubs':assert q['straight_stub_candidate_mm'] and q['anchors']
            if q['fixed_copper_nearest_mm'] is not None:
                assert 0<math.dist(q['origin_mm'],q['fixed_copper_nearest_mm'])<=3.000001
            checked=next(c for c in native['checks'] if c['via_uuid']==q['via_uuid'])
            expected_keys={k for k in ['fixed_copper_nearest_mm','straight_stub_candidate_mm'] if q[k] is not None}
            assert {c['candidate'] for c in checked['candidates']}==expected_keys
            for c in checked['candidates']:
                assert c['position_mm']==q[c['candidate']]
                assert c['min_pad_gap_mm']>=0.1-1e-12 and c['min_other_via_gap_mm']>=0.1-1e-12
        csv_equal(w/'move-probes.csv',probes)
        checks.append(dict(board=s['board'],total_vias=len(rows),overlapping_vias=summary['overlapping_vias'],violates_0p10=summary['violates_0p10'],min_nonoverlap_gap_mm=min(r['min_annulus_gap_mm'] for r in rows if r['classification']=='none'),move_status_counts=move['status_counts'],native_candidate_check='pass'))
    reference=read(E/'reference-175/pofv-reclassification-final.json')
    main=read(E/'main-rev2/all-vias.json')
    old={r['uuid'] for r in reference['observations'] if r['classification']!='no-pad-or-paste-overlap'}
    assert old=={r['uuid'] for r in main if r['classification']!='none'}
    assert reference['source_sha256']==sources[0]['sha256']
    for record in read(E/'manufacturer-sources/retrieval.json'):
        assert digest(gzip.decompress((E/'manufacturer-sources'/record['snapshot']).read_bytes()))==record['sha256_html']
    for record in read(E/'resume-integrity.json')['preserved_files']:
        assert digest((E/record['path']).read_bytes())==record['sha256']
    assert len(read(E/'move-summary.json'))==3
    if (E/'manifest.json').exists():
        for name,sha in read(E/'manifest.json')['files'].items():
            assert digest((E.parents[3]/name).read_bytes())==sha,name
    result=dict(status='pass',geometry_audit_reexecuted=False,source_objects_and_snapshots_identical=True,main_175_candidate_uuid_set_identical=True,completed_audit_files_preserved=True,boards=checks)
    (E/'verification.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__':verify()
