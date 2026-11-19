"""S0 baseline: state of the swapped working board BEFORE any edit.
Counts tracks/vias, unconnected pads (all + U1 module field)."""
import pcbnew as p, json, sys
from pathlib import Path
E = Path('.').resolve()
b = p.LoadBoard(str(E/'wmain-v28-fp.kicad_pcb'))
tracks = [t for t in b.GetTracks() if isinstance(t, p.PCB_TRACK)]
vias = [t for t in b.GetTracks() if isinstance(t, p.PCB_VIA)]
print('tracks:', len(tracks), 'vias:', len(vias), 'zones:', b.GetAreaCount())
b.BuildConnectivity()
unc = []
for fp in b.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetname() and pad.IsConnected():
            pass
# pcbnew: use connectivity via board.GetConnectivity() ratsnest per net
from collections import defaultdict
pads_by_net = defaultdict(list)
for fp in b.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetname():
            pads_by_net[pad.GetNetname()].append((str(fp.GetReference()), pad.GetNumber()))
print('nets with pads:', len(pads_by_net))
# Unconnected via ratsnest: conn.GetRatsnestForNet? Use DRC json instead (separate step).
u1 = [f for f in b.GetFootprints() if str(f.GetReference()) == 'U1'][0]
print('U1 pads:', u1.GetPadCount(), 'pos:', u1.GetPosition().x/1e6, u1.GetPosition().y/1e6,
      'rot:', u1.GetOrientationDegrees())
print('U1 fp name:', u1.GetFPID().GetLibItemName())
# module-field tracks: tracks whose both endpoints within 12mm box of U1 centre
cx, cy = 75.1, 124.85
mf = [t for t in tracks if abs(t.GetStart().x/1e6-cx) < 12 and abs(t.GetStart().y/1e6-cy) < 12
      and abs(t.GetEnd().x/1e6-cx) < 12 and abs(t.GetEnd().y/1e6-cy) < 12]
print('tracks fully inside module 24mm box:', len(mf))
json.dump({'tracks': len(tracks), 'vias': len(vias)}, open(E/'baseline-s0.json', 'w'))
