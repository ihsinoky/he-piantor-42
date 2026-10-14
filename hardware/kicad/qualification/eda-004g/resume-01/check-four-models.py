"""Independent structured file + public cache/instance checks, no PCB changes."""
import json
from pathlib import Path
import kicad_sch_api as ksa
from kicad_sch_api.library.cache import set_symbol_cache
import sexpdata

ROOT=Path(__file__).resolve().parent

def kids(n,k):return [x for x in n if isinstance(x,list) and x and str(x[0])==k]
def one(n,k):
    xs=kids(n,k);assert len(xs)==1,(k,len(xs));return xs[0]
def pins(n):
    p=kids(n,'pin')
    for x in kids(n,'symbol'):p+=pins(x)
    return p

if __name__=='__main__':
    c=json.loads((ROOT/'model-contract-v1.json').read_text())
    tree=sexpdata.loads((ROOT/'library/Qualification.kicad_sym').read_text())
    defs={d[1]:d for d in kids(tree,'symbol')}
    assert set(defs)=={m['symbol'] for m in c['models'].values()}
    cache=ksa.SymbolLibraryCache(enable_persistence=False)
    cache.discover_libraries([str(ROOT/'library')]);set_symbol_cache(cache)
    sch=ksa.create_schematic('four-part-public-model-check')
    result={}
    for i,(ref,m) in enumerate(c['models'].items()):
        lib_id='Qualification:'+m['symbol'];definition=cache.get_symbol(lib_id);assert definition is not None
        got={p.number:dict(name=p.name,role=p.pin_type.value,local_schematic_mm=[p.position.x,p.position.y]) for p in definition.pins}
        exp={n:{k:p[k] for k in ('name','role','local_schematic_mm')} for n,p in m['pins'].items()}
        assert got==exp,(ref,got,exp)
        node=defs[m['symbol']]
        assert all(p[2]=='' for p in kids(node,'property') if p[1]=='Footprint')
        instance=sch.components.add(lib_id,f'U{i+1}',m['symbol'],position=(76.2+152.4*i,76.2),footprint='Qualification:'+ref,SourceID=ref)
        assert instance.footprint=='Qualification:'+ref
        locations={}
        for n,p in m['pins'].items():
            pos=sch.get_component_pin_position(f'U{i+1}',n)
            expected=[76.2+152.4*i+p['local_schematic_mm'][0],76.2-p['local_schematic_mm'][1]]
            assert all(abs(a-b)<1e-6 for a,b in zip([pos.x,pos.y],expected)),(ref,n,pos,expected)
            locations[n]=[pos.x,pos.y]
        assert len({tuple(v) for v in locations.values()})==len(locations),ref
        result[ref]=dict(public_load_and_add=True,identity_pins_roles_positions=True,independent_nc_intent={n:p['nc'] for n,p in m['pins'].items()},unique_pin_endpoints=True,old_default_footprint_not_used=True,
                         physical_duplicates=m.get('physical_duplicates',{}))
    assert result['U_FLASH']['unique_pin_endpoints']
    (ROOT/'evidence/four-model-acceptance.json').write_text(json.dumps(dict(status='PASS_WITH_SCOPE',models=result,
        scope='Four schematic definitions and declared logical/physical correspondence only. Full Main/ERC/PCB shape and actual copper still required.',
        pcb_geometry_changed=False,full_main_pass=False),indent=2)+'\n')
    print('four model public loads/instances + independently frozen typed pin/position contracts PASS_WITH_SCOPE')
