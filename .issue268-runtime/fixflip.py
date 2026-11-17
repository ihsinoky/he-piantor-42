"""Fix J_WING: apply a true board flip so the B.Cu geometry mirrors like the Wing boards'."""
import pcbnew as p

SRC = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
b = p.LoadBoard(SRC)
for fp in b.GetFootprints():
    if fp.GetReference() == 'J_WING':
        fp.SetLayer(p.F_Cu)  # start unflipped on front, then flip properly
        try:
            fp.Flip(fp.GetPosition(), p.FLIP_DIRECTION.FLIP_TOP_BOTTOM)
        except Exception:
            fp.Flip(fp.GetPosition(), False)
        print('layer now', int(fp.GetLayer()), 'flipped', fp.IsFlipped(), 'rot', fp.GetOrientationDegrees())
b.Save(SRC)
print('saved')
