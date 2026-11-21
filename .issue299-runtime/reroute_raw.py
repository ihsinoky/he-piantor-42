"""Local pocket respin for 17L U_HC5 (Issue #299): jog the F.Cu
H_C5_RAW track north so a standard 0.60/0.30 GND stitch via fits the
pocket. The direct diagonal (133.250,99.175)->(132.000,96.300) passes
0.21-0.29 mm from every B.Cu-valid via-A centre (needs >=0.45 to the
track centreline); the EN pad corner <-> RAW centreline gap is
0.617 mm total, so no via-A exists at any via size >=0.40 (proven by
respin_diag tally ok=0 and the bisector bound ~0.28 < 0.30).

New path (F.Cu, w=0.10, same net, same endpoint vias):
(133.250,99.175) -> (133.300,100.200) -> (131.900,100.200)
                 -> (131.900,97.400) -> (132.000,96.300)
Clearances checked by hand against the pocket dump and re-verified
afterwards by pairscan/DRC: >=0.35 to the HALL_3V3 F.Cu chain end
(133.23,99.85), 0.581 to HALL via (132.481,98.725), 0.40 parallel to
H_C6_RAW x=131.50.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew

NM = 1e6
OLD = ((133.250, 99.175), (132.000, 96.300))
NEW = [(133.250, 99.175), (133.300, 100.200), (131.900, 100.200),
       (131.900, 97.400), (132.000, 96.300)]

path = sys.argv[1]
board = pcbnew.LoadBoard(path)
hit = None
for t in board.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T or t.GetNetname() != "H_C5_RAW":
        continue
    if t.GetLayer() != pcbnew.F_Cu:
        continue
    s, e = t.GetStart(), t.GetEnd()
    sp = (round(s.x / NM, 3), round(s.y / NM, 3))
    ep = (round(e.x / NM, 3), round(e.y / NM, 3))
    if (sp, ep) == OLD or (ep, sp) == OLD:
        hit = t
        break
assert hit is not None, "target RAW segment not found"
netcode = hit.GetNetCode()
board.Remove(hit)
for p, q in zip(NEW, NEW[1:]):
    tr = pcbnew.PCB_TRACK(board)
    tr.SetStart(pcbnew.VECTOR2I(int(round(p[0] * NM)), int(round(p[1] * NM))))
    tr.SetEnd(pcbnew.VECTOR2I(int(round(q[0] * NM)), int(round(q[1] * NM))))
    tr.SetWidth(int(round(0.10 * NM)))
    tr.SetLayer(pcbnew.F_Cu)
    tr.SetNetCode(netcode)
    board.Add(tr)
pcbnew.SaveBoard(path, board)
print("RAW jog applied:", OLD, "->", NEW)
