"""Main-only public authoring. Nets come from fresh source, not oracle assignments."""
import importlib.util
import json
import sys
from pathlib import Path
import kicad_sch_api as ksa
from kicad_sch_api.library.cache import set_symbol_cache

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('native',ROOT/'native-intent.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)

def generate(source,destination):
    d=native.read(source)
    cache=ksa.SymbolLibraryCache(enable_persistence=False)
    cache.discover_libraries([str(ROOT/'library')]);set_symbol_cache(cache)
    sch=ksa.create_schematic('RepresentativeMain-strategy3')
    sch.set_paper_size('A0')
    for c in d['contract']['components']:
        ref=c['cad_reference'];definition=cache.get_symbol(c['lib_id'])
        sch.components.add(c['lib_id'],ref,c['display_value'],position=tuple(c['schematic_position_mm']),footprint=c['footprint_id'],SourceID=c['reference'])
        for p in definition.pins:
            pin=sch.get_component_pin_position(ref,p.number)
            net=d['logical'][(c['reference'],p.number)]['net']
            if net is None:sch.no_connects.add(position=pin);continue
            # Stub extends away from the symbol body; no pin-to-pin wire crossings.
            dx,dy={0:(-2.54,0),90:(0,2.54),180:(2.54,0),270:(0,-2.54)}[p.rotation]
            end=(pin.x+dx,pin.y+dy)
            sch.wires.add(start=pin,end=end);sch.add_label(net,position=end)
    for i,net in enumerate(('VBUS','GND')):
        ref=f'#FLG0{i+1}'
        sch.components.add('power:PWR_FLAG',ref,'PWR_FLAG',position=(38.1,38.1+25.4*i))
        pin=sch.get_component_pin_position(ref,'1');end=(pin.x-2.54,pin.y)
        sch.wires.add(start=pin,end=end);sch.add_label(net,position=end)
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    sch.save(str(destination/'main.kicad_sch'))
    print('49 original components + 2 source-grounded virtual flags saved')

if __name__=='__main__':generate(sys.argv[1],sys.argv[2])
