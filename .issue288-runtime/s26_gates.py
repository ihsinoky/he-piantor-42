"""S2.5 gates from PLACED board data: field deviation + channel assignment.

Reads only the saved board (donor board for the field reference) and
compares against s2_design expectations. Writes JSON evidence.
"""
import json
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
from s2_design import COMPONENTS, NC

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
DONOR = WT / 'hardware/kicad/qualification/issue-182-matrix-rev3/board/m1-matrix18.kicad_pcb'
MM = 1e6
DESIGN = {ref: pins for ref, sym, val, pins in COMPONENTS}

b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}


def padnet(fp, num):
    for p in fp.Pads():
        if p.GetNumber() == num:
            return p.GetNetname()
    return None


# ---------------------------------------------------------------- field
donor = pcbnew.LoadBoard(str(DONOR))
donor_centres = {}
for fp in donor.GetFootprints():
    raws = [p.GetNetname() for p in fp.Pads() if p.GetNetname().endswith('_RAW')]
    if raws and fp.GetFPID().GetLibItemName() == 'hall':
        p = fp.GetPosition()
        donor_centres[raws[0]] = (p.x / MM, p.y / MM)

field_rows = []
max_dev = 0.0
for g in 'ABC':
    for i in range(6):
        ref = f'U_H{g}{i}'
        fp = fps[ref]
        p = fp.GetPosition()
        got = (p.x / MM, p.y / MM)
        want = donor_centres[f'H_{g}{i}_RAW']
        dev = max(abs(got[0] - want[0]), abs(got[1] - want[1]))
        max_dev = max(max_dev, dev)
        field_rows.append({'sensor': ref, 'placed': got, 'rev3': want, 'dev_mm': round(dev, 4),
                           'rotation': fp.GetOrientationDegrees()})
print(f'FIELD: 18 sensors, max centre deviation vs Rev.3 = {max_dev:.4f} mm')

# ---------------------------------------------------------------- assignment
AIN = {'1': 'AIN0 (P0.02)', '2': 'AIN1 (P0.03)', '3': 'AIN4 (P0.28)'}
S_ADDR = {'4': 0, '5': 1, '6': 2, '7': 3, '12': 4, '11': 5, '10': 6, '9': 7}
xiao = fps['U_XIAO']
xiao_nets = {p.GetNumber(): p.GetNetname() for p in xiao.Pads()}
rows = []
errors = []
for g in 'ABC':
    mux = fps[f'U_MUX{g}']
    mux_nets = {p.GetNumber(): p.GetNetname() for p in mux.Pads()}
    out_net = mux_nets['8']
    xiao_pad = next((n for n, net in xiao_nets.items() if net == out_net), None)
    for i in range(6):
        ref = f'U_H{g}{i}'
        s = fps[ref]
        raw = padnet(s, '4')
        spin = next((n for n, net in mux_nets.items() if net == raw and n in S_ADDR), None)
        en = padnet(s, '3')
        en_xiao = next((n for n, net in xiao_nets.items() if net == en), None)
        row = {'sensor': ref, 'raw_net': raw, 'mux': f'U_MUX{g}', 'mux_pin': spin,
               'address': S_ADDR.get(spin), 'mux_out': out_net, 'xiao_pad': xiao_pad,
               'adc': AIN.get(xiao_pad), 'en_net': en, 'en_xiao_pad': en_xiao,
               'vcc_net': padnet(s, '1'), 'gnd2': padnet(s, '2'), 'ep5': padnet(s, '5')}
        rows.append(row)
        if row['address'] != i or raw != f'H_{g}{i}_RAW' or en != f'EN_{g}' \
           or row['vcc_net'] != 'HALL_3V3' or row['gnd2'] != 'GND' or row['ep5'] != 'GND':
            errors.append(row)
    # reference channels
    rows.append({'sensor': f'REF_{g}', 'mux': f'U_MUX{g}', 'addr6_S7_pin10': mux_nets['10'],
                 'addr7_S8_pin9': mux_nets['9'], 'mux_en_pin2': mux_nets['2'],
                 'mux_vss_pin3': mux_nets['3']})
print(f'ASSIGNMENT: {len([r for r in rows if "sensor" in r and not r["sensor"].startswith("REF")])} sensor channels extracted, errors: {len(errors)}')
for e in errors:
    print('  ERROR:', e)

# full schematic-vs-board pad parity is s27_parity.py; here: design-table check
mismatch = []
for ref, pins in DESIGN.items():
    if ref not in fps:
        mismatch.append((ref, 'missing on board'))
        continue
    for num, net in pins.items():
        got = padnet(fps[ref], num)
        want = None if net == NC else net
        if (got or None) != want and not (got == '' and want is None):
            mismatch.append((ref, num, want, got))
print(f'DESIGN-TABLE parity: {len(mismatch)} mismatches')
for m in mismatch[:10]:
    print('  ', m)

json.dump({'field': field_rows, 'max_dev_mm': max_dev, 'assignment': rows,
           'assignment_errors': errors, 'design_mismatches': mismatch},
          open(TREE / 'verification-s2.json', 'w'), indent=1)
print('wrote verification-s2.json')
