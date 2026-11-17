"""R1: dump Wing outlines + J_WING anchor from routed boards (pcbnew)."""
import pcbnew as p, json
from pathlib import Path
E = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
out = {}
for name in ('wing-rev5-16mm-left', 'wing-rev5-16mm-right', 'wing-rev5-17mm-left', 'wing-rev5-17mm-right'):
    b = p.LoadBoard(str(E / name / 'routed.kicad_pcb'))
    poly = p.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(poly)
    o = poly.Outline(0)
    pts = [(p.ToMM(o.GetPoint(i).x), p.ToMM(o.GetPoint(i).y)) for i in range(o.PointCount())]
    jw = [f for f in b.GetFootprints() if f.GetReference() == 'J_WING'][0]
    jp = jw.GetPosition()
    out[name] = dict(jw_pos=[p.ToMM(jp.x), p.ToMM(jp.y)], jw_rot=jw.GetOrientationDegrees(),
                     flipped=jw.IsFlipped(), outline=pts)
    print(name, 'jw', out[name]['jw_pos'], out[name]['jw_rot'], 'flipped', out[name]['flipped'],
          'outline pts', len(pts), flush=True)
Path('/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime/r1-wings.json').write_text(json.dumps(out))
print('done')
