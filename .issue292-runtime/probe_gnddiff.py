import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
def mm(v): return v / 1e6
def key(t):
    if isinstance(t, p.PCB_VIA):
        v = t.GetPosition(); return ('V', round(mm(v.x), 3), round(mm(v.y), 3))
    s, e = t.GetStart(), t.GetEnd()
    return ('T', t.GetLayer(), round(mm(s.x), 3), round(mm(s.y), 3), round(mm(e.x), 3), round(mm(e.y), 3), round(mm(t.GetWidth()), 3))
work = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
wk = {key(t) for t in work.GetTracks() if t.GetNetname() == 'GND'}
tree = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
missing = []
for t in tree.GetTracks():
    if t.GetNetname() != 'GND': continue
    if key(t) not in wk: missing.append(key(t))
print('GND items in tree missing from work:', len(missing))
for k in missing[:40]: print(' ', k)
