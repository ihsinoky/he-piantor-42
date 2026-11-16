"""Build N1/N2 modified input boards (17L) from Rev.4 input.
Case transform (verified on pads 1/14): case = R(+30) * native + t.
Case-north move of 3.5 mm -> native delta (-1.75, -3.0310889).
N1: J_WING translated by delta; tab-tip outline points translated equally.
N2: J_WING rotated +180 deg about its anchor, then translated by delta;
    outline as N1."""
import pcbnew, math, os

SRC = '/home/hatch/workspace/projects/he-piantor-north/hardware/kicad/qualification/issue-235-wing-round2/wing-rev4-17mm-left/input.kicad_pcb'
OUT = '/home/hatch/workspace/projects/he-piantor-north/.issue253-runtime'
DX, DY = -1.75, -3.0310889  # mm, native

def v(x_mm, y_mm):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm))

def move_tab_tip(board, dx, dy):
    n = 0
    for d in board.GetDrawings():
        if d.GetLayerName() != 'Edge.Cuts':
            continue
        # collect points via shape API depending on type
        try:
            pts = []
            if d.Type() == pcbnew.S_SEGMENT_T:
                cand = [('s', d.GetStart()), ('e', d.GetEnd())]
            elif d.Type() == pcbnew.S_ARC_T:
                cand = [('s', d.GetStart()), ('e', d.GetEnd()), ('m', d.GetMid())]
            elif d.Type() == pcbnew.S_CIRCLE_T:
                cand = [('c', d.GetCenter())]
            else:
                cand = []
        except Exception:
            cand = []
        for tag, p in cand:
            x, y = p.x/1e6, p.y/1e6
            if 95.0 <= x <= 145.0 and y <= 24.0:
                np_ = v(x+dx, y+dy)
                if tag == 's': d.SetStart(np_)
                elif tag == 'e': d.SetEnd(np_)
                elif tag == 'm': d.SetMid(np_)
                elif tag == 'c': d.SetCenter(np_)
                n += 1
    return n

for opt in ('n1', 'n2'):
    b = pcbnew.LoadBoard(SRC)
    fp = b.FindFootprintByReference('J_WING')
    if opt == 'n2':
        fp.SetOrientationDegrees(fp.GetOrientationDegrees() + 180.0)
    pos = fp.GetPosition()
    fp.SetPosition(v(pos.x/1e6 + DX, pos.y/1e6 + DY))
    moved = 0  # outline unchanged: radial check shows header gains edge distance
    out = os.path.join(OUT, f'{opt}-17L')
    os.makedirs(out, exist_ok=True)
    b.Save(os.path.join(out, 'input.kicad_pcb'))
    print(opt, 'outline points moved:', moved, 'JWING orient now', fp.GetOrientationDegrees())
