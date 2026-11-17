"""Dump a named connector footprint's pose + pads from a board."""
import json, sys
import pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
want = sys.argv[2]
for fp in b.GetFootprints():
    if fp.GetReference() == want:
        pos = fp.GetPosition()
        print(json.dumps(dict(
            ref=want, lib=str(fp.GetFPID().GetLibItemName()), layer=int(fp.GetLayer()),
            x=pos.x/1e6, y=pos.y/1e6, rot=fp.GetOrientationDegrees(),
            pads=[dict(n=p.GetNumber(), net=p.GetNetname(),
                       x=p.GetPosition().x/1e6, y=p.GetPosition().y/1e6) for p in fp.Pads()]), indent=1))
