"""S2.4f hand finish: delete the grazing MUXA_OUT segment, then close the
remaining DRC pairs one by one (route() with exact anchors first, hand
polylines for the USB-C field hops), DRC after each hop.
"""
import json
import math
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
MM = 1e6
KCLI = '/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/bin/kicad-cli'
ENV = dict(os.environ)


def drc(tag):
    out = RT / f'drc-{tag}.json'
    subprocess.run([KCLI, 'pcb', 'drc', '--output', str(out), '--format', 'json',
                    '--severity-all', str(BOARD)], capture_output=True, env=ENV, check=True)
    d = json.loads(out.read_text())
    errs = [v for v in d['violations'] if v.get('severity') == 'error']
    return len(errs), len(d['unconnected_items'])


def place(b, net, width, points, vias=()):
    netobj = b.FindNet(net)
    add_route(b, netobj, width, points, list(vias))


def try_route(b, net, pa, pb, width=None):
    netobj = b.FindNet(net)
    nc = netobj.GetNetCode()
    w = width or (0.30 if net in POWER_NETS else 0.10)
    obs = Obstacles(b)
    res = route(obs, pa, pb, nc, w)
    if res:
        add_route(b, netobj, w, res[0], res[1])
        return True
    return False


def hand_poly(b, net, points, width=0.10, vias=()):
    """Place a polyline on F (layer flags in points) after _seg_clear checks."""
    netobj = b.FindNet(net)
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    for a, c in zip(points, points[1:]):
        if a[2] == c[2] and not _seg_clear(obs, a[0], a[1], c[0], c[1], a[2], nc, width / 2):
            print(f'  hand poly BLOCKED {net}: {a} -> {c}')
            return False
    add_route(b, netobj, width, points, list(vias))
    return True


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else 'all'
    b = pcbnew.LoadBoard(str(BOARD))
    if only in ('all', 'muxa'):
        # delete the grazing MUXA_OUT segment starting at (78.2, 123.8)
        for t in list(b.GetTracks()):
            if t.Type() == pcbnew.PCB_TRACE_T and t.GetNetname() == 'MUXA_OUT':
                s = t.GetStart()
                if math.hypot(s.x / MM - 78.2, s.y / MM - 123.8) < 0.3:
                    b.Remove(t)
                    print('deleted grazing MUXA_OUT segment')
        # pin8 pad -> south escape point -> TP_MUXA
        if hand_poly(b, 'MUXA_OUT', [(79.067925, 124.275, 0), (79.067925, 125.9, 0)]):
            print('MUXA_OUT pin8 south stub placed')
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
        ok = try_route(b, 'MUXA_OUT', (79.067925, 125.9, 0), (82.0, 127.0, 0))
        print('MUXA_OUT escape->TP route:', ok)
        b.Save(str(BOARD))
        print('after muxa:', drc('hand-muxa'))
    if only in ('all', 'vin'):
        b = pcbnew.LoadBoard(str(BOARD))
        ok = try_route(b, 'VIN', (73.87, 122.13, 1), (63.62, 119.38, 1))
        print('VIN via->XIAO pad14 (B):', ok)
        b.Save(str(BOARD))
        print('after vin:', drc('hand-vin'))
    if only in ('all', 'ena'):
        b = pcbnew.LoadBoard(str(BOARD))
        ok1 = try_route(b, 'EN_A', (117.25, 107.7, 0), (115.869643, 104.319643, 0))
        print('EN_A HA5 pad->via:', ok1)
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
        ok2 = try_route(b, 'EN_A', (115.869643, 104.319643, 1), (66.12, 123.75, 1))
        print('EN_A via->B track:', ok2)
        b.Save(str(BOARD))
        print('after ena:', drc('hand-ena'))
    if only in ('all', 'ref'):
        b = pcbnew.LoadBoard(str(BOARD))
        ok = try_route(b, 'REF_RAIL', (84.932075, 124.275, 0), (103.646847, 123.989772, 0))
        print('REF_RAIL pin9A->trackB:', ok)
        b.Save(str(BOARD))
        print('after ref:', drc('hand-ref'))
    if only in ('all', 'usb'):
        b = pcbnew.LoadBoard(str(BOARD))
        # VIN_SRC: F stub east (152.3,132.705) south, west along y=133.4, north into pad11
        ok = hand_poly(b, 'VIN_SRC', [(152.3, 132.705, 0), (152.3, 133.4, 0),
                                      (147.55, 133.4, 0), (147.55, 131.955, 0)], width=0.30)
        print('VIN_SRC stub->pad11 hand poly:', ok)
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
        ok = try_route(b, 'VIN_SRC', (142.548019, 128.798019, 1), (147.55, 133.4, 1))
        print('VIN_SRC B track->channel via route:', ok)
        b.Save(str(BOARD))
        print('after vinsrc:', drc('hand-vinsrc'))
        b = pcbnew.LoadBoard(str(BOARD))
        ok = hand_poly(b, 'CC1', [(151.25, 133.4, 0), (151.25, 131.955, 0)])
        print('CC1 channel->pad3 stub:', ok)
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
        ok = try_route(b, 'CC1', (142.0, 126.156067, 0), (151.25, 133.4, 0))
        print('CC1 R->channel route:', ok)
        b.Save(str(BOARD))
        print('after cc1:', drc('hand-cc1'))
        b = pcbnew.LoadBoard(str(BOARD))
        ok = hand_poly(b, 'CC2', [(148.741874, 130.647941, 0), (148.25, 130.9, 0),
                                  (148.25, 131.955, 0)])
        print('CC2 via->pad10 hand poly:', ok)
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
        ok = try_route(b, 'CC2', (157.991874, 126.147941, 1), (148.741874, 130.647941, 1))
        print('CC2 via->via (B) route:', ok)
        b.Save(str(BOARD))
        print('after cc2:', drc('hand-cc2'))


if __name__ == '__main__':
    main()
