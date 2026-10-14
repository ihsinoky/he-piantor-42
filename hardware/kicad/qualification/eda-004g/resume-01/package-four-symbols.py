"""Package ONLY four identified definitions using public sexpdata serializer.

Structured library-input edits precede generation. No generic schematic writer,
private cache injection, generated-output patch, footprint replacement or fork.
"""
import copy
import gzip
import json
from pathlib import Path
import sexpdata as sx

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[4]

def kids(node,key):
    return [x for x in node if isinstance(x,list) and x and str(x[0])==key]

def field(node,key):
    xs=kids(node,key);assert len(xs)==1,(key,len(xs));return xs[0]

def pins(node):
    result=kids(node,'pin')
    for sub in kids(node,'symbol'):result+=pins(sub)
    return result

if __name__=='__main__':
    c=json.loads((ROOT/'model-contract-v1.json').read_text())
    legacy=sx.loads((REPO/'hardware/sensor-test/kicad/integrated-sensor-test.kicad_sch').read_text())
    defs={x[1]:x for x in kids(field(legacy,'lib_symbols'),'symbol')}
    official=Path('/tmp/eda004g/symbols/usr/share/kicad/symbols')
    generic=sx.loads((official/'Connector_Generic.kicad_sym').read_text())
    gh=next(x for x in kids(generic,'symbol') if x[1]=='Conn_01x14')
    selected={'U_LOAD':defs['HEP:TPS22919DCKR'],'U_FLASH':defs['HEP:W25Q16JVUXIQ'],
              'J_USB':defs['HEP:HRO_TYPE-C-31-M-12'],'J_WING':gh}
    lib=ROOT/'library';lib.mkdir(exist_ok=False)
    out=[sx.Symbol('kicad_symbol_lib'),copy.deepcopy(field(generic,'version')),copy.deepcopy(field(generic,'generator'))]
    for ref,definition in selected.items():
        node=copy.deepcopy(definition);old=node[1].split(':')[-1];new=c['models'][ref]['symbol'];node[1]=new
        for sub in kids(node,'symbol'):
            assert sub[1].startswith(old+'_');sub[1]=new+sub[1][len(old):]
        for prop in kids(node,'property'):
            if prop[1]=='Footprint':prop[2]=''
            if prop[1]=='Value':prop[2]=next(x['value'] for x in json.loads((ROOT.parent/'source-intent.partial.json').read_text())['components'] if x['reference']==ref)
        if ref=='U_FLASH':
            ep=next(x for x in pins(node) if field(x,'number')[1]=='9');field(ep,'at')[1:3]=[5.08,-10.16]
        if ref=='J_USB':
            for p in pins(node):field(p,'number')[1]=c['models'][ref]['old_to_source_number'][field(p,'number')[1]]
        if ref=='J_WING':
            unit=next(x for x in kids(node,'symbol') if kids(x,'pin'))
            mp=copy.deepcopy(next(x for x in pins(node) if field(x,'number')[1]=='14'))
            field(mp,'number')[1]='15';field(mp,'name')[1]='MP';field(mp,'at')[1:3]=[-5.08,-22.86];unit.append(mp)
        got={field(p,'number')[1]:dict(name=field(p,'name')[1],role=str(p[1]),local_schematic_mm=field(p,'at')[1:3]) for p in pins(node)}
        exp={n:{k:p[k] for k in ('name','role','local_schematic_mm')} for n,p in c['models'][ref]['pins'].items()}
        assert got==exp,(ref,got,exp)
        out.append(node)
    (lib/'Qualification.kicad_sym').write_text(sx.dumps(out)+'\n')
    for name in ('Device','Connector','MCU_RaspberryPi','Regulator_Linear','Power_Protection'):
        (lib/(name+'.kicad_sym')).write_bytes(gzip.decompress((ROOT.parent/'library'/(name+'.kicad_sym.gz')).read_bytes()))
    (lib/'power.kicad_sym').write_bytes(gzip.decompress((ROOT.parent.parent/'eda-004f/library/power.kicad_sym.gz').read_bytes()))
    (lib/'LICENSE.md').write_bytes((ROOT.parent/'library/LICENSE.md').read_bytes())
    print('four individual definitions packaged; typed pins equal independently frozen contract; no default footprints')
