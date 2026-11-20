#!/usr/bin/env python3
"""Stage 4 of the SWD TC2050 respin: board edit on a WORKING COPY.
Deletes the TC2030 JSWD field + its local escape ends, places the
official TC2050 footprint at (110.5, 135.99) rotated +1.35 deg
(the rotation tips the west alignment hole south / east holes
north so all three maker holes clear the In2 PAD_SCL and MUX_EN0
tracks with no drill contact - see swd-routing-plan.md v3) and
routes the escapes. Tree board is NOT touched.

ORDERING CONSTRAINT (measured on this KiCad 9.0.9 build): SWIG
container accessors degrade after B.Remove() calls, and the IO
plugin object dies after a Remove too. Therefore: all loads,
probes, adds first; removals last, each from a list materialised
immediately before; nothing is read from the board afterwards.
Pad nets are assigned by a separate post-pass (swd_fix_padnets.py)
because SetNetCode on a board-less footprint is silently dropped.
"""
import pcbnew as p

SRC = 'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'
PRETTY = 'hardware/kicad/qualification/issue-292-wmain/wmain.pretty'
OUT = '.issue292-runtime/wmain-work.kicad_pcb'
FM = p.FromMM
mm = p.ToMM

B = p.LoadBoard(SRC)

def net(name):
    n = B.FindNet(name)
    assert n is not None, name
    return n.GetNetCode()

# ---- probes (before any mutation) ----
VIA_TYPE = None
for t in list(B.GetTracks()):
    if t.Type() == p.PCB_VIA_T:
        VIA_TYPE = t.GetViaType()
        break
assert VIA_TYPE is not None

# ---- load + place the new footprint, read back pad positions ----
fp = p.FootprintLoad(PRETTY, 'TC2050-IDC-NL')
assert fp is not None
print('loaded FPID:', fp.GetFPID().GetUniStringLibId())
fp.SetPosition(p.VECTOR2I(FM(110.5), FM(135.99)))
fp.SetOrientationDegrees(1.35)
fp.SetReference('JSWD')
fp.SetValue('TC2050-IDC-NL')
B.Add(fp)
PAD = {}
HOLES = []
for pad in fp.Pads():
    pos = (round(mm(pad.GetPosition().x), 3), round(mm(pad.GetPosition().y), 3))
    if pad.GetNumber():
        PAD[pad.GetNumber()] = pos
    else:
        HOLES.append(pos)
print('pads:', PAD)
print('holes:', HOLES)
assert len(PAD) == 10 and len(HOLES) == 3
# west hole must be the southernmost-shifted single hole
wh = min(HOLES, key=lambda h: h[0])
print('west hole at', wh)
assert wh[1] > 136.0, 'rotation sign wrong - west hole did not move south'

# ---- add new tracks and vias ----
def track(netname, layer, w, a, b):
    t = p.PCB_TRACK(B)
    t.SetStart(p.VECTOR2I(FM(a[0]), FM(a[1])))
    t.SetEnd(p.VECTOR2I(FM(b[0]), FM(b[1])))
    t.SetWidth(FM(w))
    t.SetLayer(layer)
    t.SetNetCode(net(netname))
    B.Add(t)

def via(netname, x, y, dia=0.6, drill=0.3):
    v = p.PCB_VIA(B)
    v.SetPosition(p.VECTOR2I(FM(x), FM(y)))
    v.SetViaType(VIA_TYPE)
    v.SetLayerPair(p.F_Cu, p.B_Cu)
    try:
        v.SetWidth(FM(dia))
    except Exception:
        v.SetWidth(p.F_Cu, FM(dia))
    v.SetDrill(FM(drill))
    v.SetNetCode(net(netname))
    B.Add(v)

FC, BC = p.F_Cu, p.B_Cu
P1, P2, P3, P4, P5, P9, P10 = (PAD['1'], PAD['2'], PAD['3'], PAD['4'],
                               PAD['5'], PAD['9'], PAD['10'])
# P1 SYS_3V3: west via, F.Cu approach, B.Cu return with W-hole jog
via('SYS_3V3', 100.5, 134.95)
track('SYS_3V3', FC, 0.2, (100.5, 134.95), (100.5, 137.0))
track('SYS_3V3', FC, 0.2, (100.5, 137.0), (P1[0], 137.0))
track('SYS_3V3', FC, 0.2, (P1[0], 137.0), P1)
track('SYS_3V3', BC, 0.3, (100.5, 134.95), (100.5, 136.2))
track('SYS_3V3', BC, 0.3, (100.5, 136.2), (105.5, 136.2))
track('SYS_3V3', BC, 0.3, (105.5, 136.2), (105.5, 134.9))
track('SYS_3V3', BC, 0.3, (105.5, 134.9), (108.0, 134.9))
track('SYS_3V3', BC, 0.3, (108.0, 134.9), (108.0, 136.2))
track('SYS_3V3', BC, 0.3, (108.0, 136.2), (115.07, 136.2))
track('SYS_3V3', BC, 0.3, (115.07, 136.2), (115.07, 131.0))
track('SYS_3V3', BC, 0.3, (115.07, 131.0), (115.2, 131.0))
# P2 SWDIO: jogged F.Cu leg west of pad 9, diagonal in to pad 2
track('SWDIO', FC, 0.1, (109.4, 134.0), (108.78, 134.0))
track('SWDIO', FC, 0.1, (108.78, 134.0), (108.56, 135.2))
track('SWDIO', FC, 0.1, (108.56, 135.2), (108.56, 135.8))
track('SWDIO', FC, 0.1, (108.56, 135.8), (P2[0] - 0.48, P2[1]))
track('SWDIO', FC, 0.1, (P2[0] - 0.48, P2[1]), P2)
# P3 GND: own via south of the pad
track('GND', FC, 0.2, P3, (110.5, 137.05))
via('GND', 110.5, 137.05)
# P4 SWDCLK (all F.Cu)
track('SWDCLK', FC, 0.1, (110.0, 133.5), (110.5, 133.5))
track('SWDCLK', FC, 0.1, (110.5, 133.5), (110.5, 134.4))
track('SWDCLK', FC, 0.1, (110.5, 134.4), (111.05, 134.4))
track('SWDCLK', FC, 0.1, (111.05, 134.4), (111.05, 136.9))
track('SWDCLK', FC, 0.1, (111.05, 136.9), (P4[0], 136.9))
track('SWDCLK', FC, 0.1, (P4[0], 136.9), P4)
# P5 GND: own via south of the pad
track('GND', FC, 0.2, P5, (113.04, 137.05))
via('GND', 113.04, 137.05)
# P9 GND: own 0.45 via in the In2 window NW of the pad
track('GND', FC, 0.2, P9, (109.73, 134.925))
via('GND', 109.73, 134.925, dia=0.45, drill=0.3)
# P10 RESET_N: F.Cu stub, via down, B.Cu jog west, 0.45 via up, stub
track('RESET_N', FC, 0.1, (113.5, 133.4), (113.5, 133.75))
track('RESET_N', FC, 0.1, (113.5, 133.75), (112.9, 133.75))
via('RESET_N', 112.9, 133.75)
track('RESET_N', BC, 0.1, (112.9, 133.75), (112.9, 133.9))
track('RESET_N', BC, 0.1, (112.9, 133.9), (110.3, 133.9))
track('RESET_N', BC, 0.1, (110.3, 133.9), (109.9, 133.45))
track('RESET_N', BC, 0.1, (109.9, 133.45), (108.3, 133.45))
track('RESET_N', BC, 0.1, (108.3, 133.45), (108.3, 133.975))
via('RESET_N', 108.3, 133.975, dia=0.45, drill=0.3)
track('RESET_N', FC, 0.1, (108.3, 133.975), (108.3, 135.05))
track('RESET_N', FC, 0.1, (108.3, 135.05), P10)
print('new tracks/vias added')

# ---- removals (last; from freshly materialised lists) ----
old = None
for f in list(B.GetFootprints()):
    if f.GetFPID().GetUniStringLibId() == 'TC2030-IDC-NL_Pads':
        old = f
assert old is not None
B.Remove(old)
print('old JSWD footprint removed')

DEL = [
    ('GND',     (114.770, 135.565), (115.720, 135.565)),
    ('RESET_N', (113.500, 133.400), (113.500, 135.600)),
    ('SYS_3V3', (112.200, 133.300), (112.200, 135.600)),
    ('SWDIO',   (109.400, 134.000), (112.200, 136.800)),
    ('SWDCLK',  (110.000, 133.500), (111.600, 135.100)),
    ('SWDCLK',  (111.600, 135.100), (111.600, 135.800)),
    ('SWDCLK',  (111.600, 135.800), (112.000, 136.200)),
    ('SWDCLK',  (112.000, 136.200), (112.900, 136.200)),
    ('SWDCLK',  (112.900, 136.200), (113.500, 136.800)),
]
def close(a, b, tol=0.01):
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol
removed = 0
for t in list(B.GetTracks()):
    if t.Type() != p.PCB_TRACE_T:
        continue
    s = (mm(t.GetStart().x), mm(t.GetStart().y))
    e = (mm(t.GetEnd().x), mm(t.GetEnd().y))
    for n, a, b in DEL:
        if t.GetNetname() == n and ((close(s, a) and close(e, b)) or
                                    (close(s, b) and close(e, a))):
            B.Remove(t)
            removed += 1
            break
print('escape tracks removed:', removed)
assert removed == 9, removed

B.Save(OUT)
print('saved', OUT)
