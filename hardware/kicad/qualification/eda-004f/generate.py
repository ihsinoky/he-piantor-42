"""Disposable fixture authoring through public kicad-sch-api calls only."""
import argparse
from pathlib import Path
import kicad_sch_api as ksa
from kicad_sch_api.library.cache import set_symbol_cache

ROOT = Path(__file__).resolve().parent


def generate(destination, case):
    cache = ksa.SymbolLibraryCache(enable_persistence=False)
    cache.discover_libraries([str(ROOT / 'library')])
    set_symbol_cache(cache)
    sch = ksa.create_schematic('fixture')
    for ref, pos in [('U1', (76.2, 76.2)), ('U2', (152.4, 76.2))]:
        sch.components.add('74xGxx:74LVC1G04', ref, '74LVC1G04', position=pos)
    sch.components.add('Device:R', 'R1', '12k' if case == 'value' else '10k', position=(38.1, 76.2))
    sch.components.add('Device:R', 'R2', '1k', position=(114.3, 114.3))
    sch.components.add('power:PWR_FLAG', '#FLG01', 'PWR_FLAG', position=(38.1, 38.1))
    sch.components.add('power:PWR_FLAG', '#FLG02', 'PWR_FLAG', position=(38.1, 139.7))
    # Fixed design intent, deliberately separate from the independent oracle.
    assignments = {
        'VCC': [('U1', '5'), ('U2', '5'), ('R1', '1'), ('#FLG01', '1')],
        'GND': [('U1', '3'), ('U2', '3'), ('R2', '2'), ('#FLG02', '1')],
        'INPUT': [('R1', '2'), ('U1', '2')],
        'SIGNAL': [('U1', '4'), ('U2', '2'), ('R2', '1')],
    }
    if case == 'disconnect':
        assignments['SIGNAL'].remove(('U2', '2'))
    if case == 'conflict':
        assignments['SIGNAL'].append(('U2', '4'))
    for net, endpoints in assignments.items():
        for ref, number in endpoints:
            pin = sch.get_component_pin_position(ref, number)
            assert pin is not None, (ref, number)
            # Short wire stubs exercise wires as well as named connectivity.
            end = (pin.x - 2.54, pin.y)
            sch.wires.add(start=pin, end=end)
            sch.add_label(net, position=end)
    for ref, number in [('U1', '1'), ('U2', '1')] + ([] if case == 'conflict' else [('U2', '4')]):
        sch.no_connects.add(position=sch.get_component_pin_position(ref, number))
    destination.mkdir(parents=True, exist_ok=True)
    sch.save(str(destination / 'fixture.kicad_sch'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', type=Path)
    parser.add_argument('--case', choices=['normal', 'disconnect', 'conflict', 'value'], default='normal')
    args = parser.parse_args()
    generate(args.destination, args.case)
