"""16L: components of MUX_A1/MUX_A2 via KiCad CONNECTIVITY_DATA."""
import pcbnew as p
from pathlib import Path
w = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation/wing-rev5-16mm-left')
b = p.LoadBoard(str(w / 'main.kicad_pcb'))
p.ZONE_FILLER(b).Fill(b.Zones())
b.BuildConnectivity()
conn = b.GetConnectivity()
for net in ('MUX_A1', 'MUX_A2'):
    pads = {}
    by_uuid = {}
    for f in b.GetFootprints():
        for a in f.Pads():
            if a.GetNetname() == net:
                pads[a.m_Uuid.AsString()] = f'{f.GetReference()}.{a.GetNumber()}'
                by_uuid[a.m_Uuid.AsString()] = a
    parent = {u: u for u in pads}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for u, a in by_uuid.items():
        for it in conn.GetConnectedItems(a, [p.PCB_PAD_T]):
            iu = it.m_Uuid.AsString()
            if iu in parent:
                parent[find(u)] = find(iu)
    comps = {}
    for u, ident in pads.items():
        comps.setdefault(find(u), []).append(ident)
    print(net, len(comps), 'pad-components:')
    for members in comps.values():
        print('   ', sorted(members))
print('done')
