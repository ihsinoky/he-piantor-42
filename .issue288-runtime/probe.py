import pcbnew
b = pcbnew.LoadBoard('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-182-matrix-rev3/board/m1-matrix18.kicad_pcb')
n = 0
for t in b.GetTracks():
    n += 1
print('GetTracks iterated:', n)
print('AllItems count check via Drawings:', sum(1 for _ in b.GetDrawings()))
