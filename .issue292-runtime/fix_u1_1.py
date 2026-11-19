import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
TREE = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
# restore GND via (70.85,121.35) + track (71.60,121.35)-(70.85,121.35)
def mm2(v): return v / 1e6
n = 0
for t in list(TREE.GetTracks()):
    if t.GetNetname() != 'GND': continue
    if isinstance(t, p.PCB_VIA):
        v = t.GetPosition()
        if abs(mm2(v.x) - 70.85) < 0.01 and abs(mm2(v.y) - 121.35) < 0.01:
            TREE.Remove(t); b.Add(t); n += 1
    else:
        s, e = t.GetStart(), t.GetEnd()
        if abs(mm2(s.x)-71.60)<0.01 and abs(mm2(s.y)-121.35)<0.01 and abs(mm2(e.x)-70.85)<0.01 and abs(mm2(e.y)-121.35)<0.01:
            TREE.Remove(t); b.Add(t); n += 1
# cut LED vertical + horizontal (they will be re-routed by K:LED_DRV)
CUTS = {((71.10,121.00),(71.10,121.85)), ((71.10,121.85),(71.95,121.85))}
c = 0
for m in list(MODEL):
    if not m['alive'] or m['net'] != 'LED_DRV': continue
    o = m['obj']
    if isinstance(o, p.PCB_VIA): continue
    s, e = o.GetStart(), o.GetEnd()
    k = ((round(mm2(s.x),2), round(mm2(s.y),2)), (round(mm2(e.x),2), round(mm2(e.y),2)))
    if k in CUTS or (k[1], k[0]) in CUTS:
        b.Remove(o); m['alive'] = False; c += 1
p.SaveBoard(DST, b)
print('restored U1.1 GND:', n, ' cut LED:', c)
