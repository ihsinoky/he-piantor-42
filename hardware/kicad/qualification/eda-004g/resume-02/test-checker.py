"""Fixed Main-shaped synthetic fault fixtures, before fresh KiCad Main generation.
This produces verification DATA, never schematic/PCB or routing inputs.
"""
import copy,importlib.util,json
from capture import ROOT,save,digest,utc
spec=importlib.util.spec_from_file_location('checker',ROOT/'check-main.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
C=m.C
def baseline():
    s=dict(components=[],pads=[],tracks=[],zones=0,layers=2,thickness=1.2,rules={k:.2 for k in ['m_MinClearance','m_HoleClearance','m_HoleToHoleMin','m_CopperEdgeClearance','m_TrackMinWidth']},default=dict(clearance=.2,width=.2,via=.6,drill=.3),edges=[])
    for c in C['components']:
        x,y=c['source_position_mm'];s['components'].append(dict(ref=c['cad_reference'],source_id=c['reference'],value=c['display_value'],position=[100+x,100-y],angle=c['source_ccw_rotation_deg'],footprint=c['footprint_id']))
    for e in C['pads']:
        c=next(x for x in C['components'] if x['reference']==e['source_id']);x,y=e['source_position_mm'];w,h=e['source_global_size_mm'];a=c['source_ccw_rotation_deg']
        s['pads'].append(dict(ref=e['cad_reference'],number=e['number'],position=[100+x,100-y],size=[h,w] if a==90 else [w,h],angle=a,net=e['net'] or '',attribute=e['attribute'],shape=e['shape'],drill=e['drill_mm'],layers=[0,2] if e['attribute']=='PTH' else [0]))
    for e in C['holes']:
        x,y=e['source_position_mm'];s['pads'].append(dict(ref='J1',number='',position=[100+x,100-y],size=[.65,.65],angle=0,net='',attribute='NPTH',shape='circle',drill=[.65,.65],layers=[0,2]))
    points=[[80.68,84.13],[80.68,79.95],[89.32,79.95],[89.32,84.13]]
    for a,z in zip(points,points[1:]):s['tracks'].append(dict(kind='track',start=a,end=z,width=.2,net='GND',layer=0))
    corners=[[76,78],[124,78],[124,122],[76,122]]
    for a,z in zip(corners,corners[1:]+corners[:1]):s['edges'].append(dict(start=a,end=z,width=.05))
    return s
if __name__=='__main__':
    save(ROOT/'evidence/checker-freeze.json',dict(utc=utc(),checker_sha256=digest(ROOT/'check-main.py'),fixture_code_sha256=digest(ROOT/'test-checker.py'),oracle_sha256=digest(ROOT/'main-contract-v2.json'),target_generation_started=False,scope='49-component fixed geometry only. Unknown geometry fails. Copper annuli exclude drills; no net-name/shared-number joins. Polygon near-contact ambiguity fails. Spacing acceptance additionally requires effective-rule injection and KiCad DRC.'))
    good=baseline();save(ROOT/'evidence/fault-fixtures/baseline.json',good);positive=m.pcb(good)
    cases={}
    short=copy.deepcopy(good);short['tracks'].append(dict(kind='track',start=[81.75,85.045],end=[82.55,85.045],width=.2,net='VBUS',layer=0));cases['wrong-net-real-copper']=(short,'actual wrong-net copper short')
    missing=copy.deepcopy(good);missing['pads']=[x for x in missing['pads'] if not (x['ref']=='U1' and x['number']=='1')];cases['required-pad-missing']=(missing,'required/NC pad missing')
    duplicate=copy.deepcopy(good);duplicate['tracks']=duplicate['tracks'][1:];cases['duplicate-shield-copper-missing']=(duplicate,'duplicate shield actual copper missing')
    rule=copy.deepcopy(good);rule['rules']['m_MinClearance']=0;rule['default']['clearance']=0;cases['material-rule-missing']=(rule,'missing material rule')
    results={}
    for name,(data,reason) in cases.items():
        save(ROOT/'evidence/fault-fixtures'/f'{name}.json',data)
        try:m.pcb(data)
        except AssertionError as e:
            assert reason in str(e),(name,str(e));results[name]=dict(detected=True,reason=str(e))
        else:raise AssertionError((name,'fault escaped'))
    save(ROOT/'evidence/checker-fault-acceptance.json',dict(utc=utc(),positive=positive,cases=results,status='PASS_WITH_SCOPE',actual_main_generation_acceptance=False,spacing_enforcement=False,scope='Main-shaped independently specified data; does not replace fresh KiCad read/geometry/ERC/parity or physical rule injection.'))
    print('positive and four targeted Main-shaped faults detected')
