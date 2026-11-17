import pcbnew as p
print([n for n in dir(p) if 'KICAD_T' in n or 'VECTOR' in n][:20])
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
print('zones:', [(z.GetNetname(), z.GetLayerName()) for z in b.Zones()])
print('kicad version:', p.GetBuildVersion())
