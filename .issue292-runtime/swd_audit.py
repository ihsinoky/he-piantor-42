import math, re, sys
import pcbnew as p
mm = p.ToMM

# ---- 1. outline (Edge.Cuts) text-level comparison ----
def edge_items(path):
    txt = open(path).read()
    items = re.findall(r'\((?:gr_line|gr_arc|gr_circle|gr_rect|gr_poly)\s+(?:(?!\((?:gr_|footprint|segment|via|zone|pad) ).)*?\(layer "Edge\.Cuts"\)(?:(?!\(gr_).)*?\)', txt, re.S)
    # simpler: split top-level by lines containing Edge.Cuts in graphic blocks
    out = []
    for m in re.finditer(r'\((gr_line|gr_arc|gr_circle|gr_rect|gr_poly)\n((?:.*\n)*?)\t\)', txt):
        blk = m.group(0)
        if '"Edge.Cuts"' in blk:
            nums = tuple(re.findall(r'-?\d+\.\d+', blk))
            out.append((m.group(1), nums))
    return sorted(out)
a = edge_items('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
b = edge_items('.issue292-runtime/wmain-work.kicad_pcb')
print('Edge.Cuts items base/work:', len(a), len(b), 'identical:', a == b)

# ---- 2. pad-level audit vs official geometry (rotated) ----
LOCAL = {  # from tc2050/PROVENANCE.md (maker drawing + KiCad lib check)
    '1': (-2.54, 0.635), '2': (-1.27, 0.635), '3': (0.0, 0.635),
    '4': (1.27, 0.635), '5': (2.54, 0.635), '6': (2.54, -0.635),
    '7': (1.27, -0.635), '8': (0.0, -0.635), '9': (-1.27, -0.635),
    '10': (-2.54, -0.635),
}
HOLES_LOCAL = [(-3.81, 0.0), (3.81, 1.016), (3.81, -1.016)]
C = (110.5, 135.99)
TH = math.radians(1.35)
# KiCad file coords: rotation by +TH maps (x,y) -> (x cos + y sin, -x sin + y cos)
# (empirically verified from the placed footprint read-back in the edit run)
def rot(x, y):
    return (x * math.cos(TH) + y * math.sin(TH), -x * math.sin(TH) + y * math.cos(TH))
B = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
fp = None
for f in B.GetFootprints():
    if f.GetReference() == 'JSWD':
        fp = f
maxerr = 0.0
seen = {}
for pad in fp.Pads():
    pos = (mm(pad.GetPosition().x), mm(pad.GetPosition().y))
    seen.setdefault(pad.GetNumber(), []).append((pos, pad))
for num, (lx, ly) in LOCAL.items():
    ex, ey = rot(lx, ly)
    exp = (C[0] + ex, C[1] + ey)
    (pos, pad), = seen[num]
    err = math.hypot(pos[0] - exp[0], pos[1] - exp[1])
    maxerr = max(maxerr, err)
    layers = 'paste' if p.F_Paste in pad.GetLayerSet().Seq() else 'NO-PASTE'
    print('pad %-2s at (%.3f,%.3f) exp (%.3f,%.3f) err %.4f size %.4f layers %s net %s'
          % (num, pos[0], pos[1], exp[0], exp[1], err,
             mm(pad.GetSize().x), ','.join(layers), pad.GetNetname()))
for (lx, ly) in HOLES_LOCAL:
    ex, ey = rot(lx, ly)
    exp = (C[0] + ex, C[1] + ey)
    best = None
    for (pos, pad) in seen['']:
        d = math.hypot(pos[0] - exp[0], pos[1] - exp[1])
        if best is None or d < best[0]:
            best = (d, pos, pad)
    maxerr = max(maxerr, best[0])
    print('hole at (%.3f,%.3f) exp (%.3f,%.3f) err %.4f drill %.4f'
          % (best[1][0], best[1][1], exp[0], exp[1], best[0], mm(best[2].GetDrillSize().x)))
print('MAX POSITION ERROR vs official geometry: %.4f mm' % maxerr)
