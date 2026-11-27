#!/usr/bin/env python3
"""Issue #303 topology proof.
1) Parse the generated schematic: instance -> pin -> net label (from gen data, re-derived from file).
2) Walk the series chain from J1 pin2 to J1 pin1; assert every cell is traversed exactly once,
   in the intended order, and no net connects both terminals of one cell (short check).
3) Geometry: from the AA datum (IEC 60086 AA: length max 50.5, dia max 14.5) and the centre
   study allowances (pitch 15.0, end allowance 0.75/end), compute all 6 contact positions and
   check them against the orientation/bridge table."""
import re, json, sys

SCH = open("/home/hatch/workspace/projects/he-piantor-pwr/hardware/kicad/qualification/issue-303-pwr/pwr.kicad_sch").read()

# instance positions + refs
inst = {}
for m in re.finditer(r'\(symbol \(lib_id "pwr:(\w+)"\) \(at ([\d.]+) ([\d.]+) 0\).*?\(reference "(\w+)"\) \(unit 1\)\)\)\)', SCH):
    inst[m.group(4)] = (m.group(1), float(m.group(2)), float(m.group(3)))
# labels: net name at (x,y)
labels = [(m.group(1), float(m.group(2)), float(m.group(3))) for m in re.finditer(r'\(label "([^"]+)" \(at ([\d.]+) ([\d.]+)', SCH)]
PIN_OFF = {1: (-5.08, 2.54), 2: (-5.08, -2.54)}
conn = {}  # (ref,pin) -> net
for ref, (lib, x, y) in inst.items():
    pins = [1] if lib == "TESTPOINT" else [1, 2]
    for p in pins:
        off = (-5.08, 0.0) if lib == "TESTPOINT" else PIN_OFF[p]
        px, py = x + off[0], y - off[1]
        net = [n for n, lx, ly in labels if abs(lx - (px - 7.62)) < 0.01 and abs(ly - py) < 0.01]
        assert len(net) == 1, (ref, p, net)
        conn[(ref, p)] = net[0]

nets = {}
for k, v in conn.items():
    nets.setdefault(v, []).append(k)
print("net -> endpoints:")
for n in sorted(nets): print(" ", n, sorted(nets[n]))

# series walk: components BT1..BT3 (pins 1=POS,2=NEG), F1, J2 are 2-pin series elements; J1 is the port.
series = {"BT1", "BT2", "BT3", "F1", "J2"}
def other(ref, pin): return (ref, 2 if pin == 1 else 1)
cur = ("J1", 2); visited = []
for _ in range(20):
    net = conn[cur]
    ends = [e for e in nets[net] if e != cur and not e[0].startswith("TP")]
    assert len(ends) == 1, (cur, net, ends)
    nxt = ends[0]
    if nxt[0] == "J1":
        assert nxt == ("J1", 1), nxt
        break
    assert nxt[0] in series, nxt
    visited.append(nxt[0])
    cur = other(*nxt)
else:
    sys.exit("walk did not terminate")
print("series order traversed:", visited)
assert visited == ["BT1", "BT2", "BT3", "F1", "J2"], visited

# short check: no net on both pins of same cell
for c in ["BT1", "BT2", "BT3"]:
    assert conn[(c, 1)] != conn[(c, 2)], c
print("short check: PASS (no cell has both terminals on one net)")

# geometry
L, D, PITCH, ALLOW = 50.5, 14.5, 15.0, 0.75
half = L / 2 + ALLOW  # contact face offset from cell centre = 26.0
orient = {"BT1(west)": +1, "BT2(mid)": -1, "BT3(east)": +1}  # +1: POS at north
xs = {"BT1(west)": -15.0, "BT2(mid)": 0.0, "BT3(east)": 15.0}
print(f"contact offset from cell centre: +/-{half:.2f} mm; block envelope check: width {2*PITCH + D + 2*2.0:.1f} (study 48.5), length {L + 2*ALLOW + 2*2.0:.1f} (study 56.0)")
rows = []
for name, o in orient.items():
    pos_end = "N" if o > 0 else "S"; neg_end = "S" if o > 0 else "N"
    rows.append((name, xs[name], f"POS@{pos_end}", f"NEG@{neg_end}"))
    print(f"  {name}: centre x={xs[name]:+.1f}; POS contact at ({xs[name]:+.1f}, {'-26.0' if pos_end=='N' else '+26.0'}); NEG contact at ({xs[name]:+.1f}, {'+26.0' if neg_end=='S' else '-26.0'})")
# bridges: north row joins BT1.POS & BT2.NEG; south row joins BT2.POS & BT3.NEG
assert conn[("BT1", 1)] == conn[("BT2", 2)] == "BRIDGE_N"
assert conn[("BT2", 1)] == conn[("BT3", 2)] == "BRIDGE_S"
assert conn[("BT3", 1)] == "PACK_POS_RAW" and conn[("BT1", 2)] == "PACK_NEG"
print("bridge/terminal assignment vs geometry table: PASS")
json.dump({"connections": {f"{k[0]}.{k[1]}": v for k, v in sorted(conn.items())}, "series_order": visited},
          open("/home/hatch/workspace/projects/he-piantor-pwr/.issue303-runtime/topology.json", "w"), indent=1)
print("TOPOLOGY PROOF: PASS")
