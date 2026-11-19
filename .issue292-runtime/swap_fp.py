"""Issue #292 fix round: swap U1's derived ISP1807 footprint for the
official maker-CAD footprint (wmain.pretty, regenerated from Insight
SiP's Altium library). Same centre; orientation 90 -> 0 (official
frame: pin 1 NW, antenna edge +Y = board south, per DS1807 S3 TOP
VIEW / S4.3 and the board antenna strip at y>=128.9). Nets follow pad
numbers; new pads 65-78 (NC) get no net. Then rip up U1-net routing
inside the module region so KRT can re-escape the new pad field;
GND copper outside the pad box is kept."""
import pcbnew as p
from pathlib import Path
from collections import Counter

E = Path('.').resolve()
TREE = E.parent/'hardware/kicad/qualification/issue-292-wmain'
SRC = TREE/'wmain.kicad_pcb'
OUT = E/'wmain-v28-fp.kicad_pcb'
b = p.LoadBoard(str(SRC))
u1 = [f for f in b.GetFootprints() if str(f.GetReference()) == 'U1'][0]
pos = u1.GetPosition()
CX, CY = p.ToMM(pos.x), p.ToMM(pos.y)
net_of = {pad.GetNumber(): pad.GetNet() for pad in u1.Pads()}
U1NETS = {pad.GetNetname() for pad in u1.Pads() if pad.GetNetname()}
print('centre', CX, CY, 'old orient', u1.GetOrientationDegrees(), 'nets', len(U1NETS))

new = p.FootprintLoad(str(TREE/'wmain.pretty'), 'ISP1807-LR')
new.SetFPID(p.LIB_ID('wmain', 'ISP1807-LR'))
new.SetReference('U1')
new.SetValue(u1.GetValue())
for f in u1.GetFields():
    try:
        nf = new.GetFieldByName(f.GetName())
        if nf is not None:
            nf.SetText(f.GetText())
    except Exception as ex:
        print('field copy skipped', f.GetName(), ex)
try:
    new.SetPath(u1.GetPath())
except Exception as ex:
    print('path copy skipped', ex)
new.SetAttributes(u1.GetAttributes())
for pad in new.Pads():
    if pad.GetNumber() in net_of:
        pad.SetNet(net_of[pad.GetNumber()])
new.SetPosition(pos)
new.SetOrientationDegrees(0.0)
b.Remove(u1)
b.Add(new)
chk = [f for f in b.GetFootprints() if str(f.GetReference()) == 'U1'][0]
print('new U1 pads:', len(list(chk.Pads())), 'orient', chk.GetOrientationDegrees())
p1 = [pd for pd in chk.Pads() if pd.GetNumber() == '1'][0]
print('pad1 board rel:', round(p.ToMM(p1.GetPosition().x) - CX, 3), round(p.ToMM(p1.GetPosition().y) - CY, 3), p1.GetNetname())
p71 = [pd for pd in chk.Pads() if pd.GetNumber() == '71'][0]
print('pad71 (NC row) board rel:', round(p.ToMM(p71.GetPosition().x) - CX, 3), round(p.ToMM(p71.GetPosition().y) - CY, 3), repr(p71.GetNetname()))

# --- rip up ---
def inbox(x, y, h):
    return abs(x - CX) <= h and abs(y - CY) <= h
killed = Counter()
for t in list(b.GetTracks()):
    net = t.GetNetname()
    if net not in U1NETS:
        continue
    h = 4.7 if net == 'GND' else 12.0
    if isinstance(t, p.PCB_VIA):
        hit = inbox(p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y), h)
    else:
        s, e = t.GetStart(), t.GetEnd()
        hit = any(inbox(p.ToMM(q.x), p.ToMM(q.y), h) for q in (s, e))
    if hit:
        b.Remove(t)
        killed[net] += 1
print('ripped:', dict(killed))
b.Save(str(OUT))
print('saved', OUT)
