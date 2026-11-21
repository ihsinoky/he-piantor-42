"""Replace the 17L H_C5_RAW jog v2 (crossed the HALL_3V3 vertical
track body x=133.856, y 98.72..99.47) with v3, a south-west route
under the HALL staircase:
(133.250,99.175) -> (132.900,98.420) -> (132.100,97.900)
                 -> (131.900,97.400) -> (132.000,96.300)
Hand-checked centreline distances: 0.563 to stitch via A
(133.206,97.947) [need 0.45], 0.484 to HALL via (132.481,98.725)
[need 0.45], 0.638 to the staircase end (132.61,99.35) [need 0.30],
0.40 parallel to H_C6_RAW x=131.50 [need 0.20]. DRC + pairscan are
the judges.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew

NM = 1e6
OLD = [((133.250, 99.175), (134.300, 99.600)), ((134.300, 99.600), (134.300, 100.200)),
       ((134.300, 100.200), (131.900, 100.200)), ((131.900, 100.200), (131.900, 97.400)),
       ((131.900, 97.400), (132.000, 96.300))]
NEW = [(133.250, 99.175), (132.900, 98.420), (132.100, 97.900),
       (131.900, 97.400), (132.000, 96.300)]

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
assert removed == 5, f"removed {removed} jog segments, expected 5"
for p, q in zip(NEW, NEW[1:]):
    tr = pcbnew.PCB_TRACK(board)
    tr.SetStart(pcbnew.VECTOR2I(int(round(p[0] * NM)), int(round(p[1] * NM))))
    tr.SetEnd(pcbnew.VECTOR2I(int(round(q[0] * NM)), int(round(q[1] * NM))))
    tr.SetWidth(int(round(0.10 * NM)))
    tr.SetLayer(pcbnew.F_Cu)
    tr.SetNetCode(netcode)
    board.Add(tr)
pcbnew.SaveBoard(path, board)
print("jog v3 applied")
