"""Sequential KRT fixup: strip KRT additions of MUX_OUT_C + MUX_A1, lock all,
re-route MUX_A1 alone (first pick of the field), then MUX_OUT_C + GND."""
import subprocess, sys
from pathlib import Path
import pcbnew as p

MM = 1e6
RT = Path("/home/hatch/workspace/projects/he-piantor-mainsym/.issue275-runtime")
TREE = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-275-main-rev10/main-rev10")
BOARD = TREE / "main.kicad_pcb"
REV9 = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
KRT = Path("/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools")
KRT_PY = "/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3"

def geo_key(t):
    s, e = t.GetStart(), t.GetEnd()
    if isinstance(t, p.PCB_VIA):
        return ("via", t.GetNetname(), round(s.x / MM, 3), round(s.y / MM, 3))
    return ("trk", t.GetNetname(), t.GetLayer(),
            tuple(sorted([(round(s.x / MM, 3), round(s.y / MM, 3)), (round(e.x / MM, 3), round(e.y / MM, 3))])))

b9 = p.LoadBoard(str(REV9))
geo9 = {geo_key(t) for t in b9.GetTracks()}
del b9

def load(path):
    return p.LoadBoard(str(path))

def snapshot(b):
    return {geo_key(t): t for t in b.GetTracks()}

def lock_all(b):
    for t in b.GetTracks():
        t.SetLocked(True)

def run_krt(board_path, out_path, nets, logname):
    cmd = [KRT_PY, str(KRT / "py_router/route.py"), str(board_path), str(out_path),
           "--nets", *nets, "--track-width", "0.1", "--power-nets", "HALL_5V", "GND",
           "--power-nets-widths", "0.3", "0.3", "--clearance", "0.1",
           "--via-size", "0.6", "--via-drill", "0.3",
           "--same-net-pad-clearance", "0.15", "--escalation", "board"]
    env = dict(__import__("os").environ)
    r = subprocess.run(cmd, cwd=str(KRT), capture_output=True, text=True, env=env)
    (RT / logname).write_text(r.stdout[-6000:] + "\n--- STDERR ---\n" + r.stderr[-2000:])
    print("KRT", nets, "exit", r.returncode)
    return r.returncode == 0

def merge_additions(base_path, routed_path, nets, out_path):
    bb = load(base_path)
    base_keys = set(snapshot(bb).keys())
    netobjs = {}
    for t in bb.GetTracks():
        netobjs.setdefault(t.GetNetname(), t.GetNet())
    br = load(routed_path)
    added = 0
    keep = []
    for t in br.GetTracks():
        if geo_key(t) in base_keys or t.GetNetname() not in nets:
            continue
        s, e = t.GetStart(), t.GetEnd()
        if isinstance(t, p.PCB_VIA):
            nt = p.PCB_VIA(bb)
            nt.SetPosition(s); nt.SetWidth(t.GetWidth(p.F_Cu)); nt.SetDrill(t.GetDrillValue()); nt.SetViaType(t.GetViaType())
        else:
            nt = p.PCB_TRACK(bb)
            nt.SetStart(s); nt.SetEnd(e); nt.SetWidth(t.GetWidth()); nt.SetLayer(t.GetLayer())
        nt.SetNet(netobjs[t.GetNetname()])
        bb.Add(nt); keep.append(nt); added += 1
    del br
    filler = p.ZONE_FILLER(bb)
    filler.Fill(bb.Zones())
    bb.BuildConnectivity()
    bb.Save(str(out_path))
    print("merged additions:", added)
    return added

# step 1: strip KRT additions of MUX_OUT_C + MUX_A1, lock, save prep2
b = load(BOARD)
rm = [t for t in b.GetTracks() if t.GetNetname() in ("MUX_OUT_C", "MUX_A1") and geo_key(t) not in geo9]
for t in rm:
    b.Remove(t)
print("stripped KRT additions:", len(rm))
lock_all(b)
PREP2 = RT / "rev10-prep2.kicad_pcb"
filler = p.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.Save(str(PREP2))
del b

# step 2: MUX_A1 alone
RA = RT / "rev10-fixA.kicad_pcb"
assert run_krt(PREP2, RA, ["MUX_A1"], "krt-fixA.log")
BA = RT / "rev10-boardA.kicad_pcb"
merge_additions(PREP2, RA, {"MUX_A1"}, BA)

# step 3: lock board A, route MUX_OUT_C + GND
b = load(BA)
lock_all(b)
b.Save(str(BA))
del b
RB = RT / "rev10-fixB.kicad_pcb"
assert run_krt(BA, RB, ["MUX_OUT_C", "GND"], "krt-fixB.log")
merge_additions(BA, RB, {"MUX_OUT_C", "GND"}, BOARD)
print("fixup complete -> tree board updated")
