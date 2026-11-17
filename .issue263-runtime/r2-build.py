"""R2: build respin inputs.
- Backup current boards to .issue263-runtime/board-backup/respin-pre/.
- Apply the R1 notch to Edge.Cuts of input.kicad_pcb (qualify reference)
  and of the candidate base (main.kicad_pcb).
- Blocked variants (16L/16R/17R): remove every track/via intersecting the
  fanout respin box around J_WING (Chebyshev half-size 22 mm for 16L,
  18 mm for 16R/17R) -> respin-in.kicad_pcb.
- 17L: notch only -> respin-in.kicad_pcb (no copper removed)."""
import sys, json, shutil
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/geometry/lib/python3.12/site-packages')
from shapely.geometry import LineString, box as sbox
import pcbnew as p
from pathlib import Path
RT = Path('/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime')
E = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
design = json.load(open(RT / 'r1-notch-design.json'))
V = lambda x, y: p.VECTOR2I(round(x * 1e6), round(y * 1e6))
MM = lambda v: p.ToMM(v)
BOX = {'wing-rev5-16mm-left': 22.0, 'wing-rev5-16mm-right': 18.0,
       'wing-rev5-17mm-right': 18.0, 'wing-rev5-17mm-left': 0.0}

def apply_notch(b, name):
    d = design[name]
    prof = [tuple(pt) for pt in d['profile']]
    edge_x, y_lo, y_hi = d['edge_x'], d['y_lo'], d['y_hi']
    target = None
    for dr in list(b.GetDrawings()):
        if dr.GetLayer() != p.Edge_Cuts or dr.Type() != p.PCB_SHAPE_T or dr.GetShape() != p.SHAPE_T_SEGMENT:
            continue
        s, e = dr.GetStart(), dr.GetEnd()
        xs = (MM(s.x), MM(e.x)); ys = (MM(s.y), MM(e.y))
        if abs(xs[0] - edge_x) < 0.01 and abs(xs[1] - edge_x) < 0.01 and min(ys) < y_lo and max(ys) > y_hi:
            target = dr; top = max(ys); bot = min(ys); width = dr.GetWidth()
            break
    assert target is not None, f'{name}: west edge segment not found'
    b.Remove(target)
    chain = [(edge_x, top)] + prof + [(edge_x, bot)]
    for (x0, y0), (x1, y1) in zip(chain, chain[1:]):
        if abs(x0 - x1) < 1e-9 and abs(y0 - y1) < 1e-9:
            continue
        sh = p.PCB_SHAPE(b)
        sh.SetShape(p.SHAPE_T_SEGMENT)
        sh.SetStart(V(x0, y0)); sh.SetEnd(V(x1, y1))
        sh.SetLayer(p.Edge_Cuts); sh.SetWidth(width)
        b.Add(sh)
    return top, bot

for name in sorted(design):
    if len(sys.argv) > 1 and name not in sys.argv[1:]:
        continue
    w = E / name
    bak = RT / 'board-backup' / 'respin-pre' / name
    bak.mkdir(parents=True, exist_ok=True)
    for fn in ('input.kicad_pcb', 'main.kicad_pcb', 'routed.kicad_pcb'):
        if (w / fn).exists():
            shutil.copyfile(w / fn, bak / fn)
    # notch the qualify reference
    bi = p.LoadBoard(str(w / 'input.kicad_pcb'))
    apply_notch(bi, name)
    p.SaveBoard(str(w / 'input.kicad_pcb'), bi)
    # candidate base
    b = p.LoadBoard(str(w / 'main.kicad_pcb'))
    apply_notch(b, name)
    jw = [f for f in b.GetFootprints() if f.GetReference() == 'J_WING'][0]
    jp = jw.GetPosition(); cx, cy = MM(jp.x), MM(jp.y)
    half = BOX[name]
    removed = 0
    if half:
        region = sbox(cx - half, cy - half, cx + half, cy + half)
        for t in list(b.GetTracks()):
            s, e = t.GetStart(), t.GetEnd()
            seg = LineString([(MM(s.x), MM(s.y)), (MM(e.x), MM(e.y))])
            if seg.intersects(region):
                b.Remove(t); removed += 1
    p.SaveBoard(str(w / 'respin-in.kicad_pcb'), b)
    print(f'{name}: notch applied; fanout box {half} mm -> removed {removed} tracks/vias', flush=True)
print('done')
