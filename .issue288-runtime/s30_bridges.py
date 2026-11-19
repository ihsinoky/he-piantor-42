"""S2.4g final bridges: MUXA_OUT cluster tie, VIN chain, EN_A HA5, REF_RAIL."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route, _seg_clear
from s28_component_route import POWER_NETS

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
BOARD = TREE / 'wmatrix.kicad_pcb'
RT = WT / '.issue288-runtime'
KCLI = '/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/bin/kicad-cli'
ENV = dict(os.environ)


def drc(tag):
    out = RT / f'drc-{tag}.json'
    subprocess.run([KCLI, 'pcb', 'drc', '--output', str(out), '--format', 'json',
                    '--severity-all', str(BOARD)], capture_output=True, env=ENV, check=True)
    d = json.loads(out.read_text())
    errs = [v for v in d['violations'] if v.get('severity') == 'error']
    return len(errs), len(d['unconnected_items'])


def hop(net, pa, pb, width=None):
    b = pcbnew.LoadBoard(str(BOARD))
    netobj = b.FindNet(net)
    w = width or (0.30 if net in POWER_NETS else 0.10)
    obs = Obstacles(b)
    res = route(obs, pa, pb, netobj.GetNetCode(), w)
    print(f'{net}: {pa} -> {pb} :', bool(res), flush=True)
    if res:
        add_route(b, netobj, w, res[0], res[1])
        b.Save(str(BOARD))
    return bool(res)


def main():
    # MUXA_OUT: F tie from via cluster (77.925,123.675) to pin fragment stub end (78.17,123.92)
    b = pcbnew.LoadBoard(str(BOARD))
    netobj = b.FindNet('MUXA_OUT')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    ok = _seg_clear(obs, 77.925, 123.675, 78.17, 123.92, 0, nc, 0.05)
    print('MUXA_OUT F tie clear:', ok, flush=True)
    if ok:
        add_route(b, netobj, 0.10, [(77.925, 123.675, 0), (78.17, 123.92, 0)], [])
        b.Save(str(BOARD))
    hop('MUXA_OUT', (80.20, 125.30, 1), (79.70, 126.30, 1))
    print('drc:', drc('g1'), flush=True)
    # VIN chain
    hop('VIN', (83.87, 128.63, 0), (87.015565, 130.0, 0))
    hop('VIN', (87.12, 129.88, 0), (95.0, 129.156067, 0))
    hop('VIN', (83.87, 128.63, 0), (74.66063, 122.42063, 0))
    print('drc:', drc('g2'), flush=True)
    # EN_A HA5 pad -> escape via
    hop('EN_A', (117.25, 107.7, 0), (115.869643, 104.319643, 0))
    print('drc:', drc('g3'), flush=True)
    # REF_RAIL pin9A stub -> B run
    hop('REF_RAIL', (84.932075, 124.275, 0), (87.432075, 130.525, 1))
    print('drc:', drc('g4'), flush=True)


if __name__ == '__main__':
    main()
