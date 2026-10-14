"""Stage-1 public symbol/model coverage probe. Does not author a Main board.

Missing exact definitions are recorded, never replaced by passive boxes or
private cache insertion. Nearby definitions are inspection references only.
"""
import inspect
import json
from pathlib import Path
import kicad_sch_api as ksa
from kicad_sch_api.library.cache import set_symbol_cache

ROOT = Path(__file__).resolve().parent
LIBRARY = Path('/tmp/eda004g/symbols/usr/share/kicad/symbols')
MODELS = {
    'U_MCU': 'MCU_RaspberryPi:RP2040',
    'U_ESD': 'Power_Protection:USBLC6-2SC6',
    'U_LDO': 'Regulator_Linear:AP2112K-3.3',
    'U_LOAD': 'Power_Management:TPS22919',
    'U_FLASH': 'Memory_Flash:W25Q16JVUXIQ',
    'J_USB': 'Connector:TYPE-C-31-M-12',
    'J_WING': 'Connector:BM14B-GHS-TBT',
    'Y1': 'Device:Crystal_GND24',
}
REFERENCES = ['Memory_Flash:W25Q16JVSS', 'Connector:USB_C_Receptacle_USB2.0_16P',
              'Connector_Generic:Conn_01x14', 'Device:R', 'Device:C', 'Connector:TestPoint']


def pins(definition):
    return [dict(number=p.number, name=p.name, electrical_type=p.pin_type.value,
                 position_mm=[p.position.x, p.position.y]) for p in definition.pins]


if __name__ == '__main__':
    import hashlib
    cache = ksa.SymbolLibraryCache(enable_persistence=False)
    cache.discover_libraries([str(LIBRARY)])
    set_symbol_cache(cache)
    exact = {}
    references = {}
    for ref, lib_id in MODELS.items():
        definition = cache.get_symbol(lib_id)
        exact[ref] = dict(lib_id=lib_id, available=definition is not None,
                          pins=pins(definition) if definition else None)
    for lib_id in REFERENCES:
        definition = cache.get_symbol(lib_id)
        references[lib_id] = dict(available=definition is not None,
                                   pins=pins(definition) if definition else None,
                                   used_for_main_authoring=False)
    # Public authoring actually rejects a required missing device. Catch and
    # retain the exception as the result; no schematic file is saved or repaired.
    sch = ksa.create_schematic('model-coverage-probe')
    try:
        sch.components.add(MODELS['U_LOAD'], 'U1', 'TPS22919DCKR', position=(50.8,50.8))
        missing_model_probe = dict(rejected=False, exception=None)
    except Exception as exc:
        missing_model_probe = dict(rejected=True, exception_type=type(exc).__name__, exception=str(exc))
    public_methods = {
        'SymbolLibraryCache': [n for n, m in inspect.getmembers(ksa.SymbolLibraryCache, callable) if not n.startswith('_')],
        'ComponentCollection': [n for n, m in inspect.getmembers(type(sch.components), callable) if not n.startswith('_')],
    }
    files = {lib_id.split(':')[0] + '.kicad_sym' for lib_id in list(MODELS.values()) + REFERENCES}
    inventory = json.loads((ROOT / 'source-intent.partial.json').read_text())
    result = dict(
        status='MAIN_PIN_MODEL_COVERAGE_UNQUALIFIED', library_commit='505bca23e91cf3fa6e3b66976e529e775eada3ba',
        exact_lookup=exact, inspection_references=references, missing_model_public_add_probe=missing_model_probe,
        public_methods=public_methods,
        symbol_file_sha256={n:hashlib.sha256((LIBRARY/n).read_bytes()).hexdigest() for n in sorted(files)},
        source_inventory_counts=inventory['counts'],
        reconciliation='Available pin tables are observations, not approved complete Main pin-role mappings.',
        additional_limits=[
            'W25Q16JVSS inspection definition has 8 numbered pins; source UX has additional separate unassigned EP physical land.',
            'USB generic inspection definition uses A/B/S pin numbers; source uses 1..13 combined contacts and four distinct SHIELD lands.',
            'GH generic inspection definition has 14 numbered contacts; source also has two mechanical MP lands, one logical MP number.',
            'Public cache discovers/loads external symbol files. Public collection adds instances of those files; no public symbol-definition author/register method was found in the inspected pinned classes.',
            'This does not prove that independently prepared custom symbol files or another verified library could never work. None is qualified here.',
        ],
        circuit_erc='NOT ENTERED', full_main_generation='NOT ENTERED',
        generated_schematic_files=0, generated_pcb_files=0)
    (ROOT/'evidence/public-model-assessment.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))
