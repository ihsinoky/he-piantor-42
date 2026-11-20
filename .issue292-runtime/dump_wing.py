import pcbnew as p, json, sys
b = p.LoadBoard(sys.argv[1])
def mm(v): return v/1e6
holes = []
for fp in b.GetFootprints():
    for pad in fp.Pads():
        d = mm(pad.GetDrillSize().x)
        if d >= 1.5:
            holes.append({"fp": fp.GetReference(), "pad": pad.GetNumber(),
                          "pos": [round(mm(pad.GetPosition().x),3), round(mm(pad.GetPosition().y),3)], "drill": round(d,2)})
# standalone board holes (pads not in fps are rare; also check drawings)
out = {"holes": holes}
json.dump(out, open(sys.argv[2], "w"))
for h in holes: print(h)
