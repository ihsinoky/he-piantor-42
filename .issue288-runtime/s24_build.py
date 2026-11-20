"""S2.4: build the issue-288 board from the Rev.3 donor.

Donor in-place edit: net renames (text level), J_WING/link removal,
sensor swap DRV5055 SOT-23 -> TMAG5253BA3 X2SON, MUX re-termination,
south-strip additions (XIAO socket, USB-C, battery, LDO chain, TPs).
Connectivity repair is a separate DRC-driven step (s25_repair.py).
"""
import shutil
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
from s2_design import COMPONENTS, NC

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
DONOR = WT / 'hardware/kicad/qualification/issue-182-matrix-rev3/board/m1-matrix18.kicad_pcb'
LIB = str(TREE / 'wmatrix.pretty')
MM = 1e6

DESIGN = {ref: pins for ref, sym, val, pins in COMPONENTS}

# ---------------------------------------------------------------- stage files
dst = TREE / 'wmatrix.kicad_pcb'
shutil.copy(DONOR, dst)
txt = dst.read_text()
for old, new in (('HALL_5V', 'HALL_3V3'), ('MUX_OUT_A', 'MUXA_OUT'),
                 ('MUX_OUT_B', 'MUXB_OUT'), ('MUX_OUT_C', 'MUXC_OUT')):
    txt = txt.replace(f'"{old}"', f'"{new}"')
dst.write_text(txt)

board = pcbnew.LoadBoard(str(dst))
print('thickness:', board.GetDesignSettings().GetBoardThickness() / MM)
# NOTE (KiCad 9.0.9 swig quirk): board.Remove(footprint) corrupts later
# Tracks()/GetFootprints() iteration. Snapshot every item list up front and
# work from the snapshots; additions are tracked in ADDED_FPS.
FPS0 = list(board.GetFootprints())
TRACKS0 = list(board.GetTracks())
ADDED_FPS = []


def find_net(name):
    n = board.FindNet(name)
    if n is None:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
    return n


def set_pad_nets(fp, pinmap):
    for pad in fp.Pads():
        net = pinmap.get(pad.GetNumber())
        if net is None or net == NC:
            continue
        pad.SetNet(find_net(net))


# ---------------------------------------------------------------- deletions
for fp in FPS0:
    if fp.GetReference() in ('J_WING', 'TP_W_EN'):
        board.Remove(fp)
wing = find_net('WING_EN')
for t in TRACKS0:
    mid_y = (t.GetStart().y + t.GetEnd().y) / 2 / MM if not isinstance(t, pcbnew.PCB_VIA) \
        else t.GetPosition().y / MM
    if t.GetNetCode() == wing.GetNetCode() or mid_y >= 125.5:
        board.Remove(t)
print('deletions done')

# ---------------------------------------------------------------- sensor swap
halls = []
for fp in FPS0:
    raws = [p.GetNetname() for p in fp.Pads() if p.GetNetname().endswith('_RAW')]
    if raws and fp.GetFPID().GetLibItemName() == 'hall':
        halls.append((fp, raws[0]))
print('hall sensors found:', len(halls))
for fp, raw in halls:
    g, i = raw[2], int(raw[3])
    ref = f'U_H{g}{i}'
    pos, rot = fp.GetPosition(), fp.GetOrientationDegrees()
    board.Remove(fp)
    nf = pcbnew.FootprintLoad(LIB, 'TMAG5253BA3_X2SON-4')
    nf.SetReference(ref)
    nf.SetValue('TMAG5253BA3IQDMRR')
    nf.SetPosition(pos)
    nf.SetOrientationDegrees(rot)
    board.Add(nf)
    ADDED_FPS.append(nf)
    set_pad_nets(nf, DESIGN[ref])

# ---------------------------------------------------------------- MUX re-term
MUXFPS = {fp.GetReference(): fp for fp in FPS0}
for g in 'ABC':
    fp = MUXFPS[f'U_MUX_{g}']
    set_pad_nets(fp, DESIGN[f'U_MUX{g}'])
    fp.SetReference(f'U_MUX{g}')

# ---------------------------------------------------------------- cap refs
sensors = {f'U_H{g}{i}': None for g in 'ABC' for i in range(6)}
centres = {}
for fp in ADDED_FPS:
    if fp.GetReference() in sensors:
        p = fp.GetPosition()
        centres[fp.GetReference()] = (p.x / MM, p.y / MM)
for fp in FPS0:
    if fp.GetFPID().GetLibItemName() != 'capacitor':
        continue
    p = fp.GetPosition()
    x, y = p.x / MM, p.y / MM
    best = min(centres.items(), key=lambda kv: (kv[1][0] - x) ** 2 + (kv[1][1] - y) ** 2)
    if abs(best[1][0] + 3.5 - x) < 0.6 and abs(best[1][1] - y) < 0.6:
        fp.SetReference('C_H' + best[0][3:])
    elif y < 125:
        gx = 'A' if x < 95 else ('B' if x < 114 else 'C')
        fp.SetReference(f'C_MUX{gx}')

# ---------------------------------------------------------------- TP renames
TPMAP = {'TP_W_MUXA': 'TP_MUXA', 'TP_W_MUXB': 'TP_MUXB', 'TP_W_MUXC': 'TP_MUXC',
         'TP_W_A0': 'TP_A0', 'TP_W_A1': 'TP_A1', 'TP_W_A2': 'TP_A2',
         'TP_W_H5V': 'TP_RAIL_N', 'TP_W_GND': 'TP_GND_A',
         'TP_W_GND_A': 'TP_GND_B', 'TP_W_GND_B': 'TP_GND_C', 'TP_W_GND_C': 'TP_GND_D',
         'TP_H16_CTR_RAW': 'TP_H16_CTR', 'TP_H16_N_RAW': 'TP_H16_N',
         'TP_H16_DIAG_RAW': 'TP_H16_DIAG', 'TP_H17_CTR_RAW': 'TP_H17_CTR',
         'TP_H17_N_RAW': 'TP_H17_N', 'TP_H17_DIAG_RAW': 'TP_H17_DIAG'}
for fp in FPS0:
    r = fp.GetReference()
    if r in TPMAP:
        fp.SetReference(TPMAP[r])

# ---------------------------------------------------------------- new parts
ADD = [  # (ref, footprint, x, y, rot_deg)
    ('U_XIAO', 'XIAO_nRF52840_SOCKET', 56, 127, 90),
    ('J_USB', 'TYPE-C-31-M-12', 150, 136, 180),
    ('J_BATT', 'JST_XH_B2B-XH-A_1x02', 128, 124, 0),
    ('Q_PROT', 'AO3401A_SOT-23', 86, 130, 0),
    ('C_LDO_IN', 'C_0603', 95, 130, 0),
    ('U_LDO', 'AP2112_SOT-23-5', 104, 130, 0),
    ('C_LDO_OUT', 'C_0603', 113, 130, 0),
    ('R_SHUNT', 'R_0603', 121, 130, 90),
    ('R_DIV1', 'R_0603', 130, 130, 90),
    ('R_DIV2', 'R_0603', 137, 130, 90),
    ('R_CC1', 'R_0603', 142, 127, 0),
    ('R_CC2', 'R_0603', 158, 127, 0),
    ('R_LED', 'R_0603', 71, 133, 90),
    ('D_LED', 'LED_0805', 78, 133, 0),
    ('TP_VIN_SRC', 'TP_1.2mm', 74, 137, 0),
    ('TP_VIN', 'TP_1.2mm', 99, 134.5, 0),
    ('TP_3V3_SRC', 'TP_1.2mm', 109, 134.5, 0),
    ('TP_RAIL_E', 'TP_1.2mm', 158, 120, 0),
    ('TP_EN_A', 'TP_1.2mm', 69, 117, 0),
    ('TP_EN_B', 'TP_1.2mm', 69, 121, 0),
    ('TP_EN_C', 'TP_1.2mm', 69, 125, 0),
    ('TP_REF', 'TP_1.2mm', 133, 134.5, 0),
]
VALUES = {ref: val for ref, sym, val, pins in COMPONENTS}
for ref, fpname, x, y, rot in ADD:
    nf = pcbnew.FootprintLoad(LIB, fpname)
    nf.SetReference(ref)
    nf.SetValue(VALUES.get(ref, ''))
    nf.SetPosition(pcbnew.VECTOR2I(int(x * MM), int(y * MM)))
    nf.SetOrientationDegrees(rot)
    board.Add(nf)
    ADDED_FPS.append(nf)
    set_pad_nets(nf, DESIGN[ref])

# XIAO orientation assertion: pads 7/8 (antenna end, local x=-7.62) must be south
xiao = next(f for f in ADDED_FPS if f.GetReference() == 'U_XIAO')
pads = {p.GetNumber(): (p.GetPosition().x / MM, p.GetPosition().y / MM) for p in xiao.Pads()}
print('XIAO pad1', pads['1'], 'pad7', pads['7'], 'pad14', pads['14'])
assert pads['7'][1] > pads['1'][1], 'antenna end not south - flip rotation'

# ---------------------------------------------------------------- keep-out
zone = pcbnew.ZONE(board)
zone.SetIsRuleArea(True)
zone.SetDoNotAllowTracks(True)
zone.SetDoNotAllowVias(True)
zone.SetDoNotAllowPads(False)
zone.SetDoNotAllowCopperPour(True)
zone.SetLayer(pcbnew.F_Cu)
poly = zone.Outline()
poly.NewOutline()
for (x, y) in ((45, 135.8), (67, 135.8), (67, 139.9), (45, 139.9)):
    poly.Append(int(x * MM), int(y * MM))
board.Add(zone)
zone2 = pcbnew.ZONE(board)
zone2.SetIsRuleArea(True)
zone2.SetDoNotAllowTracks(True)
zone2.SetDoNotAllowVias(True)
zone2.SetDoNotAllowPads(False)
zone2.SetDoNotAllowCopperPour(True)
zone2.SetLayer(pcbnew.B_Cu)
poly2 = zone2.Outline()
poly2.NewOutline()
for (x, y) in ((45, 135.8), (67, 135.8), (67, 139.9), (45, 139.9)):
    poly2.Append(int(x * MM), int(y * MM))
board.Add(zone2)

board.Save(str(dst))
print('saved board file')
