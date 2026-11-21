"""Gate 7: schematic netlist (kicad-cli export) vs placed board pads.
Usage: s2_gate7.py <variant> <netlist.net>"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-wwing/.issue299-runtime')
import s2_env
s2_env.apply_env()
import pcbnew  # noqa: E402

VAR = sys.argv[1]
board = pcbnew.LoadBoard(sys.argv[3])
padmaps = json.loads((s2_env.RT / 'padmaps-rev6.json').read_text())[VAR]
elec_refs = {r for r, e in padmaps.items() if e['fp'] != 'NPTH'}
elec_refs.discard('TP_W_H5V')
elec_refs.add('TP_W_H3V3')

board_map = {}
for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref not in elec_refs:
        continue
    for pad in fp.Pads():
        net = pad.GetNetname()
        if net:
            board_map[(ref, pad.GetNumber())] = net

text = Path(sys.argv[2]).read_text()
sch_map = {}
nc_nodes = []
cur = None
token_re = re.compile(
    r'\(net\s+\(code\s+"?\d+"?\)\s+\(name\s+"([^"]*)"\)'
    r'|\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)')
for m in token_re.finditer(text):
    if m.group(1) is not None:
        cur = m.group(1)
    elif cur is not None:
        if cur.startswith('unconnected-('):
            nc_nodes.append((m.group(2), m.group(3)))
        else:
            sch_map[(m.group(2), m.group(3))] = cur.lstrip('/')
# PWR_FLAG pseudo-components are not board parts
sch_map = {k: v for k, v in sch_map.items() if not k[0].startswith('#FLG')}

missing = {f'{k[0]}.{k[1]}': v for k, v in board_map.items() if k not in sch_map}
extra = {f'{k[0]}.{k[1]}': v for k, v in sch_map.items() if k not in board_map}
mismatch = {f'{k[0]}.{k[1]}': (board_map[k], sch_map[k])
            for k in board_map.keys() & sch_map.keys() if board_map[k] != sch_map[k]}
refs_board = {r for r, _ in board_map}
refs_sch = {r for r, _ in sch_map}
print(json.dumps({'gate': 7, 'variant': VAR,
                  'board_nodes': len(board_map), 'sch_nodes': len(sch_map),
                  'board_refs': len(refs_board), 'sch_refs': len(refs_sch),
                  'sch_nc_nodes': [f'{r}.{p}' for r, p in sorted(nc_nodes)],
                  'missing_in_sch': missing, 'extra_in_sch': extra,
                  'net_mismatch': mismatch}))
