"""Local rip-up of the J3.8 knot: delete the short GND/MUX_A1 fanout segments
that fence J3.8's escape, so the KRT completion pass can re-weave the box.
GND pads stay plane-connected; MUX_A1 keeps its via and pad-side stub."""
import pcbnew as p
from verify import xy

E = '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation'
b = p.LoadBoard(f'{E}/main-rev8/routed.kicad_pcb')

def near(a, z, pts):
    return any(abs(a[0] - pts[0]) < 0.06 and abs(a[1] - pts[1]) < 0.06 for _ in [0]) and False

DELETE = [
    # (net, start, end) approx endpoints from en1-box dump
    ('GND', (123.700, 112.300), (124.100, 112.300)),
    ('GND', (124.100, 112.300), (124.500, 112.700)),
    ('GND', (124.500, 112.700), (124.800, 112.700)),
    ('GND', (124.800, 112.700), (125.000, 112.900)),
    ('MUX_A1', (124.100, 112.000), (124.500, 112.000)),
    ('MUX_A1', (124.500, 112.000), (125.000, 112.500)),
    ('MUX_A1', (125.000, 112.500), (125.200, 112.500)),
]
def close(p, q, tol=0.06):
    return abs(p[0] - q[0]) <= tol and abs(p[1] - q[1]) <= tol

removed = 0
for t in list(b.GetTracks()):
    if isinstance(t, p.PCB_VIA):
        continue
    a, z = xy(t.GetStart()), xy(t.GetEnd())
    for net, da, dz in DELETE:
        if t.GetNetname() == net and ((close(a, da) and close(z, dz)) or (close(a, dz) and close(z, da))):
            b.Remove(t); removed += 1
            break
print('removed', removed, 'of', len(DELETE))
b.BuildConnectivity()
p.SaveBoard(f'{E}/main-rev8/repair-in.kicad_pcb', b)
print('repair-in saved')
