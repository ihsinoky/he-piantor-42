"""South-band census: footprints and J_WING-net segment endpoints with y>=116."""
import json, sys
import pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
fps = []
for fp in b.GetFootprints():
    p = fp.GetPosition()
    if p.y/1e6 >= 112:
        fps.append((fp.GetReference(), round(p.x/1e6,2), round(p.y/1e6,2), int(fp.GetLayer())))
print("FOOTPRINTS y>=112:", json.dumps(fps))
nets = ['HALL_5V','GND','MUX_A0','MUX_A1','MUX_A2','WING_EN','MUX_OUT_A','MUX_OUT_B','MUX_OUT_C']
# endpoints histogram per net in band: count segments touching y>=124
for n in nets:
    cnt = 0; vias = []
    for t in b.GetTracks():
        if t.GetNetname() != n: continue
        s, e = t.GetStart(), t.GetEnd()
        if max(s.y, e.y)/1e6 >= 124:
            cnt += 1
            if isinstance(t, pcbnew.PCB_VIA):
                vias.append((round(s.x/1e6,2), round(s.y/1e6,2)))
    print(n, "segs touching y>=124:", cnt, "vias:", vias)
