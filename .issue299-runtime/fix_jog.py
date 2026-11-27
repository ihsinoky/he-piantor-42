"""Replace the 17L H_C5_RAW jog: the first version's opening segment
passed 0.05 mm from the HALL_3V3 F.Cu chain end (133.23,99.85) -
DRC shorting_items/tracks_crossing. New route swings EAST first,
keeping >=0.44 mm from the HALL vertical (133.86,98.72-99.47) and
>=0.63 mm from the chain end:
(133.250,99.175) -> (134.300,99.600) -> (134.300,100.200)
                 -> (131.900,100.200) -> (131.900,97.400)
                 -> (132.000,96.300)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew

NM = 1e6
OLD = [((133.250, 99.175), (133.300, 100.200)), ((133.300, 100.200), (131.900, 100.200)),
       ((131.900, 100.200), (131.900, 97.400)), ((131.900, 97.400), (132.000, 96.300))]
NEW = [(133.250, 99.175), (134.300, 99.600), (134.300, 100.200),
       (131.900, 100.200), (131.900, 97.400), (132.000, 96.300)]

path = sys.argv[1]
board = pcbnew.LoadBoard(path)
removed = 0
netcode = None
for t in list(board.GetTracks()):
    if t.Type() == pcbnew.PCB_VIA_T or t.GetNetname() != "H_C5_RAW" or t.GetLayer() != pcbnew.F_Cu:
        continue
    s, e = t.GetStart(), t.GetEnd()
    sp = (round(s.x / NM, 3), round(s.y / NM, 3))
    ep = (round(e.x / NM, 3), round(e.y / NM, 3))
    if (sp, ep) in OLD or (ep, sp) in OLD:
        netcode = t.GetNetCode()
        board.Remove(t)
        removed += 1
assert removed == 4, f"removed {removed} jog segments, expected 4"
for p, q in zip(NEW, NEW[1:]):
    tr = pcbnew.PCB_TRACK(board)
    tr.SetStart(pcbnew.VECTOR2I(int(round(p[0] * NM)), int(round(p[1] * NM))))
    tr.SetEnd(pcbnew.VECTOR2I(int(round(q[0] * NM)), int(round(q[1] * NM))))
    tr.SetWidth(int(round(0.10 * NM)))
    tr.SetLayer(pcbnew.F_Cu)
    tr.SetNetCode(netcode)
    board.Add(tr)
pcbnew.SaveBoard(path, board)
print("jog replaced with east-first route")
