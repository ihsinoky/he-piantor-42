"""S2.5 parity gate: schematic netlist (kicad-cli export) vs placed board pads.

Independent of s2_design: the schematic side comes from KiCad's own
netlist export of wmatrix.kicad_sch; the board side from placed pads.
Board-only items (mounting NPTH, no-number pads) and schematic-only
items (#FLG power flags) are excluded by rule and counted.
"""
import re
import subprocess
import sys
from pathlib import Path

import pcbnew

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
MM = 1e6
KCLI = '/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/bin/kicad-cli'
ENV = {'LD_LIBRARY_PATH': '/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/lib/x86_64-linux-gnu:/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/lib/kicad',
       'PATH': '/usr/bin:/bin'}

netlist = TREE / 'netlist-s2.sexpr'
subprocess.run([KCLI, 'sch', 'export', 'netlist', '--format', 'kicadsexpr',
                '--output', str(netlist), str(TREE / 'wmatrix.kicad_sch')],
               env=ENV, capture_output=True)
txt = netlist.read_text()

# parse (net (code) (name) (node (ref) (pin) ...)...) blocks by scanning
sch = {}  # (ref, pin) -> net name
for m in re.finditer(r'\(net\s+\(code\s+"?\d+"?\)\s+\(name\s+"([^"]*)"\)', txt):
    name = m.group(1)
    start = m.end()
    # nodes until the net block closes: take the following chunk up to the next (net or end
    chunk = txt[start:start + 200000]
    nxt = chunk.find('(net ')
    if nxt > 0:
        chunk = chunk[:nxt]
    for nm in re.finditer(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', chunk):
        sch[(nm.group(1), nm.group(2))] = name

b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
board = {}
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetNumber():
            board[(fp.GetReference(), p.GetNumber())] = p.GetNetname() or None

mismatch = []
for key, net in sch.items():
    if key[0].startswith('#'):
        continue
    got = board.get(key, 'MISSING')
    if got != net:
        mismatch.append((key, net, got))
board_only = [(k, v) for k, v in board.items() if k not in sch and v]
print(f'schematic pins: {len(sch)}, board pads: {len(board)}')
print(f'mismatches (schematic vs board): {len(mismatch)}')
for m in mismatch[:12]:
    print('  ', m)
print(f'board pads with nets but absent from schematic: {len(board_only)}')
for m in board_only[:12]:
    print('  ', m)
