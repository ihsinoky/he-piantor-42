"""Issue #268 stage 3d cleanup: trim dangling spurs onto real junctions,
delete duplicate micro-segment stacks, extend GND bus across pad-10 neck."""
import pcbnew as p

SRC = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
mm = lambda v: v/1e6
b = p.LoadBoard(SRC)

def key(t):
    s, e = t.GetStart(), t.GetEnd()
    return (t.GetNetname(), t.GetLayerName(), round(mm(s.x), 2), round(mm(s.y), 2), round(mm(e.x), 2), round(mm(e.y), 2))

DELETE_ALL = {
    ('GND', 'B.Cu', 98.55, 130.20, 98.50, 130.20),      # x7 dup stack inside bus
    ('HALL_5V', 'F.Cu', 122.45, 119.65, 122.40, 119.60),  # x8 dup stack inside via-corner copper
    ('GND', 'F.Cu', 85.70, 127.70, 85.75, 127.70),      # chain-B micro
    ('GND', 'F.Cu', 85.75, 127.70, 85.75, 127.65),      # chain-B micro
    ('MUX_A2', 'F.Cu', 103.50, 128.50, 103.50, 128.90),  # spur tip
    ('MUX_A2', 'F.Cu', 103.60, 128.40, 103.50, 128.50),  # spur base (via keeps B.Cu termination)
}
NECK_TRIM = {96.75: 130.40, 97.75: 130.20, 98.75: 130.20}  # lane x -> new north end y
deleted = trimmed = 0
for t in list(b.GetTracks()):
    if isinstance(t, p.PCB_VIA): continue
    k = key(t)
    if k in DELETE_ALL:
        b.RemoveNative(t); deleted += 1; continue
    if k[0] == 'GND' and k[1] == 'B.Cu' and round(mm(t.GetWidth()), 2) == 0.15:
        x = k[2]
        if x in NECK_TRIM and abs(k[3] - 131.00) < 0.01 and abs(k[5] - 129.90) < 0.01:
            t.SetEnd(p.VECTOR2I(p.FromMM(x), p.FromMM(NECK_TRIM[x]))); trimmed += 1
    if k == ('WING_EN', 'F.Cu', 109.70, 124.20, 106.10, 127.80):
        t.SetEnd(p.VECTOR2I(p.FromMM(107.50), p.FromMM(126.35))); trimmed += 1
        print('EN spur trimmed onto via (107.50,126.35)')
print('deleted', deleted, 'trimmed', trimmed)

t = p.PCB_TRACK(b)
t.SetStart(p.VECTOR2I(p.FromMM(98.55), p.FromMM(130.20)))
t.SetEnd(p.VECTOR2I(p.FromMM(98.90), p.FromMM(130.20)))
t.SetWidth(p.FromMM(0.30)); t.SetLayer(p.B_Cu); t.SetNet(b.GetNetInfo().GetNetItem('GND'))
b.Add(t)
print('GND bus extended across pad-10 neck')
b.Save(SRC)
print('saved')
