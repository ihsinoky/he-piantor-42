"""S2.4k: HB3 spur relocation + HA5 east detour."""
import math
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route, _seg_clear
from s28_component_route import Comp
from s29_finish import try_connect

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
step = sys.argv[1]
b = pcbnew.LoadBoard(str(BOARD))

if step == 'hb3del':
    n = 0
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != 'HALL_3V3':
            continue
        s, e = t.GetStart(), t.GetEnd()
        seg = (round(s.x / MM, 2), round(s.y / MM, 2), round(e.x / MM, 2), round(e.y / MM, 2))
        if seg in [(134.75, 72.05, 135.25, 73.05), (135.25, 73.05, 134.75, 72.05),
                   (135.25, 73.05, 134.00, 88.66), (134.00, 88.66, 135.25, 73.05),
                   (134.00, 71.80, 134.50, 71.80), (134.50, 71.80, 134.00, 71.80),
                   (134.50, 71.80, 134.75, 72.05), (134.75, 72.05, 134.50, 71.80)]:
            b.Remove(t)
            n += 1
    b.Save(str(BOARD))
    print('deleted', n, 'rail spur segs')

elif step == 'hb3arc':
    netobj = b.FindNet('H_B3_RAW')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    pts = [(134.25, 72.3, 0), (134.95, 72.14, 0), (136.5, 72.6, 0),
           (136.5, 74.3, 0), (134.25, 74.3, 0)]
    ok = all(_seg_clear(obs, a[0], a[1], c[0], c[1], 0, nc, 0.05) for a, c in zip(pts, pts[1:]))
    print('HB3 arc clear:', ok)
    if ok:
        add_route(b, netobj, 0.10, pts, [])
        b.Save(str(BOARD))

elif step == 'rail':
    obs = Obstacles(b)
    comp = Comp(b)
    comps = comp.components('HALL_3V3')
    print('HALL_3V3 comps:', [len(c) for c in comps])
    if len(comps) > 1:
        if try_connect(b, obs, comp, 'HALL_3V3', comps):
            b.Save(str(BOARD))
            print('rail reconnected')

elif step == 'ha5':
    netobj = b.FindNet('EN_A')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    pts = [(117.25, 107.7, 0), (118.05, 108.35, 0), (118.3, 108.6, 0)]
    ok = all(_seg_clear(obs, a[0], a[1], c[0], c[1], 0, nc, 0.05) for a, c in zip(pts, pts[1:]))
    print('HA5 detour stub clear:', ok)
    if ok:
        add_route(b, netobj, 0.10, pts, [])
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
        obs = Obstacles(b)
        res = route(obs, (118.3, 108.6, 0), (115.869643, 104.319643, 0), nc, 0.10)
        print('HA5 detour->via:', bool(res))
        if res:
            add_route(b, netobj, 0.10, res[0], res[1])
            b.Save(str(BOARD))


elif step == 'ha5del':
    n = 0
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != 'H_A5_RAW':
            continue
        s, e = t.GetStart(), t.GetEnd()
        seg = (round(s.x / MM, 2), round(s.y / MM, 2), round(e.x / MM, 2), round(e.y / MM, 2))
        if seg in [(117.40, 108.05, 117.75, 107.80), (117.75, 107.80, 117.40, 108.05),
                   (117.75, 107.80, 117.75, 106.80), (117.75, 106.80, 117.75, 107.80),
                   (117.40, 108.05, 109.90, 113.70), (109.90, 113.70, 117.40, 108.05),
                   (117.75, 106.80, 117.25, 106.30), (117.25, 106.30, 117.75, 106.80)]:
            b.Remove(t)
            n += 1
    b.Save(str(BOARD))
    print('deleted', n, 'HA5 RAW wrap segs')

elif step == 'ha5raw':
    obs = Obstacles(b)
    comp = Comp(b)
    comps = comp.components('H_A5_RAW')
    print('H_A5_RAW comps:', [len(c) for c in comps])
    if len(comps) > 1:
        if try_connect(b, obs, comp, 'H_A5_RAW', comps):
            b.Save(str(BOARD))
            print('HA5 RAW reconnected')
