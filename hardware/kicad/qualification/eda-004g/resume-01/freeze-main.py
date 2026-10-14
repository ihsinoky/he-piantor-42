"""Manual source/locked-footprint Main expectation, independent of generators.

Four custom pin roles are the frozen model contract. Other roles come from
unchanged official definition snapshots, before any Main generation.
"""
import json
import math
from pathlib import Path
import kicad_sch_api as ksa
from capture import ROOT, save, digest, utc

OLD=ROOT.parent

if __name__=='__main__':
    partial=json.loads((OLD/'source-intent.partial.json').read_text())
    four=json.loads((ROOT/'model-contract-v1.json').read_text())['models']
    cache=ksa.SymbolLibraryCache(enable_persistence=False)
    cache.discover_libraries([str(ROOT/'library')])
    ids={'U_MCU':'MCU_RaspberryPi:RP2040','U_ESD':'Power_Protection:USBLC6-2SC6',
         'U_LDO':'Regulator_Linear:AP2112K-3.3','Y1':'Device:Crystal_GND24'}
    counters={};components=[];pads=[];holes=[]
    for c in partial['components']:
        ref=c['reference'];prefix='TP' if ref.startswith('TP_') else ref[0]
        counters[prefix]=counters.get(prefix,0)+1
        cad_ref=f'{prefix}{counters[prefix]}'
        lib_id='Qualification:'+four[ref]['symbol'] if ref in four else ids.get(ref,'Device:R' if prefix=='R' else 'Device:C' if prefix=='C' else 'Connector:TestPoint')
        if ref in four:
            role_table={n:{k:p[k] for k in ('name','role','local_schematic_mm')} for n,p in four[ref]['pins'].items()}
        else:
            symbol=cache.get_symbol(lib_id);assert symbol is not None
            role_table={p.number:dict(name=p.name,role=p.pin_type.value,local_schematic_mm=[p.position.x,p.position.y]) for p in symbol.pins}
        assert set(role_table)==set(c['pins']),(ref,role_table,c['pins'])
        components.append(dict(**c,cad_reference=cad_ref,lib_id=lib_id,display_value=c['value'] if c['value'] is not None else 'TestPoint',
            pin_roles=role_table,schematic_position_mm=[76.2+127*(len(components)%7),76.2+101.6*(len(components)//7)],
            footprint_id='Qualification:'+cad_ref))
        def pad(n,x,y,w,h,shape='rect',drill=None,idx=0):
            p=c['pins'][str(n)];a=math.radians(c['source_ccw_rotation_deg']);ox,oy=c['source_position_mm']
            sx=ox+x*math.cos(a)-y*math.sin(a);sy=oy+x*math.sin(a)+y*math.cos(a)
            size=[h,w] if c['source_ccw_rotation_deg']==90 else [w,h]
            pads.append(dict(id=f'{ref}.{n}.{idx}',source_id=ref,cad_reference=cad_ref,number=str(n),land_index=idx,
                net=p['named_net'],nc=p['intentional_nc'],source_local_mm=[x,y],source_position_mm=[round(sx,6),round(sy,6)],
                source_global_size_mm=size,shape=shape,drill_mm=drill or [0,0],layers=['F.Cu','B.Cu'] if drill else ['F.Cu'],
                attribute='PTH' if drill else 'SMD',corner_radius_mm=0))
        if ref=='U_MCU':
            for i in range(56):
                side=i//14;v=2.6-(i%14)*.4
                x=[-3.4375,-v,3.4375,v][side];y=[v,-3.4375,-v,3.4375][side]
                pad(i+1,x,y,.875 if side%2==0 else .2,.2 if side%2==0 else .875)
            pad(57,0,0,3.2,3.2)
        elif ref=='J_USB':
            for n,x,w in [(1,-3.25,.6),(2,-2.45,.6),(7,-1.75,.3),(3,-1.25,.3),(8,-.75,.3),(4,-.25,.3),(5,.25,.3),(9,.75,.3),(6,1.25,.3),(10,1.75,.3),(11,2.45,.6),(12,3.25,.6)]:pad(n,x,-4.045,w,1.45)
            for i,(x,y,h,d) in enumerate([(-4.32,-3.13,2.1,1.7),(4.32,-3.13,2.1,1.7),(-4.32,1.05,1.6,1.2),(4.32,1.05,1.6,1.2)]):pad(13,x,y,1,h,'oval',[.6,d],i)
            for i,x in enumerate([-2.89,2.89]):holes.append(dict(id=f'J_USB.NPTH.{i}',source_id=ref,source_position_mm=[-15+x,19-2.60],diameter_mm=.65,layers=['F.Cu','B.Cu']))
        elif ref=='U_FLASH':
            for n,x,y in [(1,-1.4478,-.750001),(2,-1.4478,-.25),(3,-1.4478,.25),(4,-1.4478,.750001),(5,1.4478,.750001),(6,1.4478,.25),(7,1.4478,-.25),(8,1.4478,-.750001)]:pad(n,x,y,.8128,.254)
            pad(9,0,0,.254,1.651)
        elif ref=='Y1':
            for n,x,y in [(1,-1.15,.875),(2,1.15,.875),(3,1.15,-.875),(4,-1.15,-.875)]:pad(n,x,y,1.3,1.05)
        elif ref=='J_WING':
            for i in range(14):pad(i+1,8.125-1.25*i,0,.6,1.7)
            for i,x in enumerate([-9.975,9.975]):pad(15,x,-3.35,1,2.8,idx=i)
        elif ref in ('U_ESD','U_LOAD'):
            pitch,offset,w,h=(.95,1.3,1,.6) if ref=='U_ESD' else (.65,.84,1.03,.35)
            for i,y in enumerate([pitch,0,-pitch,-pitch,0,pitch]):pad(i+1,-offset if i<3 else offset,y,w,h)
        elif ref=='U_LDO':
            for n,x,y in [(1,-1.1375,.95),(2,-1.1375,0),(3,-1.1375,-.95),(4,1.1375,-.95),(5,1.1375,.95)]:pad(n,x,y,1.325,.6)
        elif prefix=='TP':pad(1,0,0,1.2,1.2,'circle')
        else:
            w,h,dx={'0402':(.54,.64,.51),'0603':(.8,.95,.825),'0805':(1.025,1.4,.9125)}[c['source_footprint']]
            pad(1,-dx,0,w,h);pad(2,dx,0,w,h)
    assert len(components)==49 and len(pads)==197 and sum(p['nc'] for p in pads)==30 and len(holes)==2
    contract=dict(version=1,status='FROZEN_BEFORE_MAIN_GENERATION',frozen_utc=utc(),basis='Manual fixed TSX + locked footprinter constants, source-intent partial preserved; no fresh or routed generated input used to derive expected pads/nets.',
        components=components,pads=pads,holes=holes,named_nets=partial['named_nets'],board=partial['board'],local_bond=partial['local_bond'],
        coordinate_transform=dict(origin_kicad_mm=[100,100],source_y_inverted=True,component_angle_preserved=True),
        tolerance_mm=.000002,clearance_tolerance_policy='Measurement rounding only, never reduce 0.20mm physical minimum; ambiguous comparisons fail.',
        allowed_geometry=['axis-aligned native rect/circle pads','oval plated stakes','circle NPTH','straight round-ended tracks','circular through-vias'],
        unsupported_geometry_fails=True,required_pad_count=167,nc_physical_pad_count=30,virtual_power_flags=dict(VBUS='External USB host power enters the passive connector VBUS contacts; source isPowerNet.',GND='External USB host ground through passive receptacle contacts; not an invented chip supply.'),
        manufacturer_EP_policy='UX physical metal is source-NC passive annotation, independent of GND; no claimed ninth signal/supply or inherited electrical connection. Not manufacturing-release evidence.',
        source_keepouts=[],expected_pre_route_global_tracks=0,expected_pre_route_vias=0,
        model_contract_sha256=digest(ROOT/'model-contract-v1.json'),footprinter_source_sha256=digest(Path('/tmp/eda004g-resume01/frontend/node_modules/@tscircuit/footprinter/dist/index.js')))
    save(ROOT/'main-contract-v1.json',contract)
    save(ROOT/'evidence/main-contract-freeze-v1.json',dict(recorded_utc=utc(),sha256=digest(ROOT/'main-contract-v1.json')))
    print('full Main v1 frozen: 49 components, 197 physical pads, 2 NPTH, 37 nets; independent roles/nets/source shape expectations')
