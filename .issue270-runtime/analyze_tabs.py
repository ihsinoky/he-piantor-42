"""Tab-zone analysis in per-edge (t,d) frames (build-main2 convention).
Dumps sites.json: edge frames, pad/silk/courtyard extents, current tab.
Validation: raw max pad d should be 3.829 (J2) / 3.997 (J3)
(outline-extension d_pad_req 4.229/4.397 minus the 0.40 margin)."""
import json, math
from pathlib import Path
import pcbnew as p
from shapely.geometry import Polygon, Point

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
Q263 = ROOT / 'hardware/kicad/qualification/issue-263-implementation'
MM = 1e6
g = json.loads((HERE / 'geometry.json').read_text())
rev7 = Polygon(g['main_rev7_outline'])
ext = json.loads((Q263 / 'main-rev8/outline-extension.json').read_text())

b = p.LoadBoard(str(Q263 / 'main-rev8/main.kicad_pcb'))
sites = {}
for ref in ('J2', 'J3'):
    f = [x for x in b.GetFootprints() if x.GetReference() == ref][0]
    ox, oy = f.GetPosition().x / MM - 100, f.GetPosition().y / MM - 70
    yaw = f.GetOrientationDegrees()
    tabc = ext['tabs'][ref]['corners']
    tc = [(c[0] - 100, c[1] - 70) for c in tabc]
    centre = (sum(q[0] for q in tc) / 4, sum(q[1] for q in tc) / 4)
    # nearest Rev.7 outline segment to the tab centre
    coords = list(rev7.exterior.coords)
    best = None
    for a, bb in zip(coords, coords[1:]):
        mx, my = (a[0] + bb[0]) / 2, (a[1] + bb[1]) / 2
        d = math.hypot(mx - centre[0], my - centre[1])
        if best is None or d < best[0]:
            best = (d, a, bb)
    _, A, B = best
    ux, uy = B[0] - A[0], B[1] - A[1]
    L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
    cen = rev7.centroid
    mx, my = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2
    nx, ny = -uy, ux
    if (mx + nx - cen.x) ** 2 + (my + ny - cen.y) ** 2 < (mx - cen.x) ** 2 + (my - cen.y) ** 2:
        nx, ny = -nx, -ny

    def td(pt):
        return ((pt[0] - A[0]) * ux + (pt[1] - A[1]) * uy,
                (pt[0] - A[0]) * nx + (pt[1] - A[1]) * ny)

    pads_td, pads_true_td = [], []
    for pad in f.Pads():
        bb = pad.GetBoundingBox()
        for cx, cy in ((bb.GetLeft() / MM, bb.GetTop() / MM), (bb.GetRight() / MM, bb.GetTop() / MM),
                       (bb.GetLeft() / MM, bb.GetBottom() / MM), (bb.GetRight() / MM, bb.GetBottom() / MM)):
            pads_td.append(td((cx - 100, cy - 70)))
    for pd in g['main_zif_pads'][ref]:
        for c in pd['corners']:
            pads_true_td.append(td(c))
    th = math.radians(yaw)
    silk_td = []
    for lx, ly in ((-5.55, -1.80), (5.55, -1.80), (5.55, 4.60), (-5.55, 4.60)):
        q = (ox + lx * math.cos(th) + ly * math.sin(th), oy - lx * math.sin(th) + ly * math.cos(th))
        silk_td.append(td(q))
    cy = f.GetCourtyard(p.F_Cu)
    cy_td = []
    for i in range(cy.OutlineCount()):
        o = cy.Outline(i)
        for j in range(o.PointCount()):
            pt = o.GetPoint(j)
            cy_td.append(td((pt.x / MM - 100, pt.y / MM - 70)))
    tc_td = [td(c) for c in tc]
    sites[ref] = dict(
        A=list(A), u=[ux, uy], n=[nx, ny], origin=[ox, oy], yaw=yaw,
        tab_corners_case=tc, tab_t_range=ext['tabs'][ref]['t_range_mm'], depth=ext['tabs'][ref]['depth_mm'],
        tab_t_range_mine=[min(t for t, _ in tc_td), max(t for t, _ in tc_td)],
        tab_d_range_mine=[min(d for _, d in tc_td), max(d for _, d in tc_td)],
        pad_d_max=max(d for _, d in pads_td), pad_t_range=[min(t for t, _ in pads_td), max(t for t, _ in pads_td)],
        pad_true_d_max=max(d for _, d in pads_true_td),
        silk_d_max=max(d for _, d in silk_td), silk_t_range=[min(t for t, _ in silk_td), max(t for t, _ in silk_td)],
        cy_d_max=max(d for _, d in cy_td), cy_t_range=[min(t for t, _ in cy_td), max(t for t, _ in cy_td)],
        pads_td=[list(q) for q in pads_td], silk_td=[list(q) for q in silk_td])
    print(ref, 'edge A', [round(v, 2) for v in A], 'u', [round(v, 3) for v in (ux, uy)],
          'pad_d_max', round(sites[ref]['pad_d_max'], 3), '(expect 3.829/3.997)',
          'padTrue_d_max', round(sites[ref]['pad_true_d_max'], 3),
          'silk_d_max', round(sites[ref]['silk_d_max'], 3), 'cy_d_max', round(sites[ref]['cy_d_max'], 3),
          'tab t', ext['tabs'][ref]['t_range_mm'], 'depth', ext['tabs'][ref]['depth_mm'])
json.dump(sites, open(HERE / 'sites.json', 'w'), indent=1)
print('saved sites.json')
