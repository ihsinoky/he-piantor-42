#!/usr/bin/env python3
"""Apply the pre-staged C_HC2 stitch (Issue #299 option b, staged in
scratch/17r-optb.kicad_pcb last round) to a 17R board file:
  via A (117.4733, 81.9505) 0.60/0.30 GND
  via B (116.4733, 83.0005) 0.60/0.30 GND
  F.Cu track (117.2233,82.1505)->(116.6233,82.7505) w 0.30 GND
Geometry extracted verbatim from the optb file (extract_hc2 dump).
Run refill.py afterwards so the HALL_3V3 fill carves its rings.
Usage: apply_hc2.py <board.kicad_pcb>"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew

NM = 1e6
FCU = pcbnew.F_Cu

def main():
    path = sys.argv[1]
    board = pcbnew.LoadBoard(path)
    gnd_code = None
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() == "GND":
                gnd_code = pad.GetNetCode()
    assert gnd_code is not None
    # sanity: nothing already at the via sites
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            for (vx, vy) in ((117.4733, 81.9505), (116.4733, 83.0005)):
                assert abs(p.x / NM - vx) > 0.01 or abs(p.y / NM - vy) > 0.01, "via already present"
    def via(x, y):
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(int(round(x * NM)), int(round(y * NM))))
        try:
            v.SetViaType(pcbnew.VIATYPE_THROUGH)
        except Exception:
            pass
        v.SetWidth(int(round(0.60 * NM)))
        if hasattr(v, "SetDrillValue"):
            v.SetDrillValue(int(round(0.30 * NM)))
        else:
            v.SetDrill(int(round(0.30 * NM)))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNetCode(gnd_code)
        board.Add(v)
    via(117.4733, 81.9505)
    via(116.4733, 83.0005)
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(int(round(117.2233 * NM)), int(round(82.1505 * NM))))
    t.SetEnd(pcbnew.VECTOR2I(int(round(116.6233 * NM)), int(round(82.7505 * NM))))
    t.SetWidth(int(round(0.30 * NM)))
    t.SetLayer(FCU)
    t.SetNetCode(gnd_code)
    board.Add(t)
    pcbnew.SaveBoard(path, board)
    print("C_HC2 stitch applied")

if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    main()
