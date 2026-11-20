import pcbnew
b = pcbnew.LoadBoard('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-182-matrix-rev3/board/m1-matrix18.kicad_pcb')
for fp in list(b.GetFootprints()):
    if fp.GetReference() in ('J_WING', 'TP_W_EN'):
        b.Remove(fp)
print('removed fps')
n = sum(1 for _ in b.GetTracks())
print('tracks after removal:', n)
