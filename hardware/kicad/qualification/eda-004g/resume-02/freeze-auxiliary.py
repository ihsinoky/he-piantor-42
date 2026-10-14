"""Historical NON-COPPER comparison only, never authoring/routing input.
Source identity/pose is checked before taking auxiliary expectation records.
No old pad/track/via data is extracted or passed to a generator.
"""
import gzip,json,hashlib
from collections import Counter
from capture import ROOT,save,digest,utc
TYPES={'pcb_silkscreen_path','pcb_silkscreen_rect','pcb_silkscreen_text','pcb_courtyard_outline','pcb_courtyard_rect','pcb_solder_paste'}
def normalize(rows):
    sc={x['source_component_id']:x['name'] for x in rows if x['type']=='source_component'}
    pc={x['pcb_component_id']:sc[x['source_component_id']] for x in rows if x['type']=='pcb_component'}
    def values(x):
        if isinstance(x,float):return round(x,6)
        if isinstance(x,list):return [values(y) for y in x]
        if isinstance(x,dict):return {k:values(v) for k,v in x.items()}
        return x
    result=[]
    for x in rows:
        if x['type'] not in TYPES:continue
        out={k:v for k,v in x.items() if not k.endswith('_id') and k not in ('subcircuit_id',)}
        out['source_identity']=pc.get(x.get('pcb_component_id'))
        result.append(values(out))
    return sorted(result,key=lambda x:json.dumps(x,sort_keys=True))
if __name__=='__main__':
    path=ROOT.parents[4]/'hardware/tscircuit/qualification/eda-003c/evidence/raw/latest-main.circuit.json.gz'
    raw=gzip.decompress(path.read_bytes());assert hashlib.sha256(raw).hexdigest()=='97d51d510ecc7096261ad36297b48939609a14435a24926967b61197ed951131'
    rows=json.loads(raw);c=json.loads((ROOT/'main-contract-v2.json').read_text());expected={x['reference']:x for x in c['components']}
    sc={x['source_component_id']:x['name'] for x in rows if x['type']=='source_component'}
    components=[x for x in rows if x['type']=='pcb_component'];assert len(components)==49
    for x in components:
        e=expected[sc[x['source_component_id']]]
        assert [x['display_offset_x'],x['display_offset_y']]==e['source_position_mm'] and x['rotation']==e['source_ccw_rotation_deg']
    auxiliary=normalize(rows)
    save(ROOT/'auxiliary-contract-v2.json',dict(version=2,frozen_utc=utc(),status='FROZEN_BEFORE_RESUME02_TARGET_GENERATION',basis='Read-only non-copper comparison from fixed historical source pose; no copper extracted/reused; generator consumes fresh source, not this table.',comparison_source_sha256=hashlib.sha256(raw).hexdigest(),records=auxiliary))
    save(ROOT/'evidence/auxiliary-contract-freeze.json',dict(utc=utc(),sha256=digest(ROOT/'auxiliary-contract-v2.json'),counts=dict(Counter(x['type'] for x in auxiliary)),authoring_input=False,old_copper_reuse=False))
    print('non-copper comparison expectations frozen before fresh generation')
