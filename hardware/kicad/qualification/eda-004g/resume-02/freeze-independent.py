"""New target oracle: frozen source geometry + official RAW typed definitions.

Never reads an old generated netlist/PCB to determine expected roles or geometry.
Old failed contract remains failed. New version precedes fresh target generation.
"""
import copy,json
from pathlib import Path
import sexpdata as sx
from capture import ROOT,save,digest,utc
def kids(n,k):return [x for x in n if isinstance(x,list) and x and str(x[0])==k]
def field(n,k):
    xs=kids(n,k);assert len(xs)==1,(k,len(xs));return xs[0]
def definitions(path):return {x[1]:x for x in kids(sx.loads(path.read_text()),'symbol')}
def rawpins(node,defs):
    result={}
    extends=kids(node,'extends')
    if extends:result.update(rawpins(defs[extends[0][1]],defs))
    for unit in kids(node,'symbol'):
        for p in kids(unit,'pin'):
            n=field(p,'number')[1];assert n not in result
            result[n]=dict(name=field(p,'name')[1],role=str(p[1]),local_schematic_mm=field(p,'at')[1:3])
    return result
if __name__=='__main__':
    old=ROOT.parent/'resume-01';c=json.loads((old/'main-contract-v1.json').read_text())
    four=json.loads((old/'model-contract-v1.json').read_text())
    # Public pretty printer fixes library INPUT line structure, no output patch.
    for path in (ROOT/'library').glob('*.kicad_sym'):
        tree=sx.loads(path.read_text());printed=sx.dumps(tree,pretty_print=True)
        assert sx.loads(printed)==tree;path.write_text(printed+'\n')
    comparison=[]
    for component in c['components']:
        lib,name=component['lib_id'].split(':');defs=definitions(ROOT/'library'/f'{lib}.kicad_sym');actual=rawpins(defs[name],defs)
        assert set(actual)==set(component['pins'])
        if component['reference'] in four['models']:
            exp={n:{k:p[k] for k in ['name','role','local_schematic_mm']} for n,p in four['models'][component['reference']]['pins'].items()};assert actual==exp
        comparison.append(dict(source_id=component['reference'],lib_id=component['lib_id'],official_raw_pins=actual,previous_observation=component['pin_roles'],library_sha256=digest(ROOT/'library'/f'{lib}.kicad_sym')))
        component['pin_roles']=actual
    changed=[(x['source_id'],n,x['previous_observation'][n]['role'],p['role']) for x in comparison for n,p in x['official_raw_pins'].items() if p['role']!=x['previous_observation'][n]['role']]
    assert changed==[('U_LDO','4','passive','no_connect')]
    assert next(x for x in c['components'] if x['reference']=='U_LDO')['pins']['4']['intentional_nc']
    c.update(version=2,frozen_utc=utc(),status='FROZEN_BEFORE_RESUME02_TARGET_GENERATION',basis='Independent source geometry transcription preserved from failed v1; all 193 logical roles/names/positions read from official structured library definitions including inheritance, not cache defaults or old generated output.',previous_failed_contract_sha256=digest(old/'main-contract-v1.json'),expectation_change_scope='New fresh target only. No previous trial promoted or oracle changed retrospectively.')
    four.update(version=2,frozen_utc=utc(),prior_model_contract_sha256=digest(old/'model-contract-v1.json'),status='FROZEN_BEFORE_RESUME02_TARGET_GENERATION')
    save(ROOT/'model-contract-v2.json',four);c['model_contract_sha256']=digest(ROOT/'model-contract-v2.json')
    save(ROOT/'main-contract-v2.json',c)
    save(ROOT/'evidence/raw-definition-reconciliation.json',dict(utc=utc(),components=comparison,role_observation_difference=changed,prior_fail_not_repaired=True,all_logical_pins=193))
    save(ROOT/'evidence/contracts-freeze.json',dict(utc=utc(),main=digest(ROOT/'main-contract-v2.json'),models=digest(ROOT/'model-contract-v2.json'),libraries={p.name:digest(p) for p in (ROOT/'library').iterdir()},generation_started=False))
    print('v2 frozen from raw official definitions:193 pins; old failed v1 unchanged')
