import pcbnew as p
b = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
filler = p.ZONE_FILLER(b)
filler.Fill(b.Zones())
p.SaveBoard('.issue292-runtime/wmain-work.kicad_pcb', b)
print('refilled + saved')
