import pcbnew as p
DST = '.issue292-runtime/wmain-work.kicad_pcb'
SRC = 'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'
def mm2(v): return v / 1e6
SITES = {(75.60,112.03), (77.06,110.67), (74.86,112.71), (74.13,113.40), (77.79,109.99)}
work = p.LoadBoard(DST)
have = set()
for t in work.GetTracks():
    if isinstance(t, p.PCB_VIA):
        v = t.GetPosition(); have.add((round(mm2(v.x),2), round(mm2(v.y),2)))
src = p.LoadBoard(SRC)
n = 0
for t in list(src.GetTracks()):
    if t.GetNetname() != 'GND' or not isinstance(t, p.PCB_VIA): continue
    v = t.GetPosition(); k = (round(mm2(v.x),2), round(mm2(v.y),2))
    if k in SITES and k not in have:
        src.Remove(t); work.Add(t); n += 1
p.SaveBoard(DST, work)
print('restored tab vias:', n)
