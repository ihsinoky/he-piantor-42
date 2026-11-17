"""Dump track/via topology of the 14 Wing-link nets + connected pads (Rev.3, read-only)."""
import json, sys
import pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
nets = ['HALL_5V','GND','MUX_A0','MUX_A1','MUX_A2','WING_EN','MUX_OUT_A','MUX_OUT_B','MUX_OUT_C']
pads = {}
for fp in b.GetFootprints():
    for p in fp.Pads():
        n = p.GetNetname()
        if n in nets:
            pads.setdefault(n, []).append(f"{fp.GetReference()}.{p.GetNumber()}")
segs = {}
for t in b.GetTracks():
    n = t.GetNetname()
    if n in nets:
        s = t.GetStart(); e = t.GetEnd()
        kind = 'via' if isinstance(t, pcbnew.PCB_VIA) else f"L{int(t.GetLayer())}"
        segs.setdefault(n, []).append((kind, round(s.x/1e6,2), round(s.y/1e6,2), round(e.x/1e6,2), round(e.y/1e6,2), round(t.GetWidth()/1e6,3)))
out = {}
for n in nets:
    out[n] = dict(pads=sorted(set(pads.get(n, []))), nseg=len(segs.get(n, [])),
                  ymin=min([min(s[2], s[4]) for s in segs.get(n, [(0,0,999,0,999,0)])]),
                  ymax=max([max(s[2], s[4]) for s in segs.get(n, [(0,0,-1,0,-1,0)])]))
print(json.dumps(out, indent=1))
with open('.issue268-runtime/link-segs.json', 'w') as f:
    json.dump(segs, f)
