import pcbnew as p
from collections import Counter
mm = p.ToMM
def census(path):
    B = p.LoadBoard(path)
    fps = {}
    for f in B.GetFootprints():
        pos = f.GetPosition()
        fps[f.GetReference()] = (round(mm(pos.x),3), round(mm(pos.y),3), round(f.GetOrientationDegrees(),3))
    trk = []
    for t in B.GetTracks():
        s, e = t.GetStart(), t.GetEnd()
        w = 0
        try: w = round(mm(t.GetWidth()),3)
        except Exception: pass
        trk.append((t.GetNetname(), t.GetLayerName(),
                    round(mm(s.x),3), round(mm(s.y),3), round(mm(e.x),3), round(mm(e.y),3), w))
    return fps, Counter(trk)
fb, tb = census('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
fw, tw = census('.issue292-runtime/wmain-work.kicad_pcb')
print('footprints base/work:', len(fb), len(fw))
for r in sorted(set(fb) | set(fw)):
    if fb.get(r) != fw.get(r):
        print('FP DIFF', r, fb.get(r), '->', fw.get(r))
BOX = lambda t: 100 <= min(t[2],t[4]) and max(t[2],t[4]) <= 118 and 130 <= min(t[3],t[5]) and max(t[3],t[5]) <= 139.5
print('tracks base/work:', sum(tb.values()), sum(tw.values()))
n = 0
for t, c in (tb - tw).items():
    if not BOX(t): print(' - removed outside box:', t); n += 1
for t, c in (tw - tb).items():
    if not BOX(t): print(' - added outside box:', t); n += 1
print('outside-box track diffs:', n)
