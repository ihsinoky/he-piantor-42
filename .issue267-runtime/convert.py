#!/usr/bin/env python3
"""Issue #267: convert #263 DRAFT packages to JLCPCB-ready BOM/CPL.

Frame method (PR #220 style): fit the translation between the source board's
Edge.Cuts geometry (KiCad frame) and the package's Edge_Cuts gerber (gerber
frame), verify every outline vertex, then apply the same translation to the
native CPL and cross-check against footprint origins from the same board file.
"""
import csv, json, math, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
Q = ROOT / 'hardware/kicad/qualification'
I263 = Q / 'issue-263-implementation'
OUT = ROOT / '.issue267-runtime'

# ---------- s-expression parsing ----------
def tokenize(text):
    toks, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c in ' \t\r\n':
            i += 1
        elif c in '()':
            toks.append(c); i += 1
        elif c == '"':
            j = i + 1; buf = ''
            while j < n and text[j] != '"':
                if text[j] == '\\' and j + 1 < n:
                    buf += text[j + 1]; j += 2
                else:
                    buf += text[j]; j += 1
            toks.append(('str', buf)); i = j + 1
        else:
            j = i
            while j < n and text[j] not in ' \t\r\n()':
                j += 1
            toks.append(text[i:j]); i = j
    return toks

def parse(text):
    toks = tokenize(text); pos = 0
    def rec():
        nonlocal pos
        t = toks[pos]; pos += 1
        if t == '(':
            lst = []
            while toks[pos] != ')':
                lst.append(rec())
            pos += 1
            return lst
        if isinstance(t, tuple):
            return t[1]
        return t
    return rec()

def is_node(x, head):
    return isinstance(x, list) and x and x[0] == head

def children(node, head):
    return [c for c in node[1:] if is_node(c, head)]

def first(node, head):
    for c in node[1:]:
        if is_node(c, head):
            return c
    return None

def layer_of(node):
    ln = first(node, 'layer')
    if ln: return ln[1]
    ln = first(node, 'layers')
    if ln: return ln[1]
    return None

def pt(node, head):
    n = first(node, head)
    return (float(n[1]), float(n[2])) if n else None

def board_geometry(pcb_path):
    tree = parse(pcb_path.read_text())
    outline = []   # Edge.Cuts points, KiCad frame
    footprints = {}  # ref -> dict(x, y, rot, layer, fpid)
    for node in tree[1:]:
        if is_node(node, 'footprint'):
            fpid = node[1] if len(node) > 1 else ''
            ref = None
            for pr in children(node, 'property'):
                if len(pr) > 2 and pr[1] == 'Reference':
                    ref = pr[2]
            if ref is None:
                for ft in children(node, 'fp_text'):
                    if len(ft) > 2 and ft[1] == 'reference':
                        ref = ft[2]
            at = first(node, 'at')
            x, y = float(at[1]), float(at[2])
            rot = float(at[3]) if len(at) > 3 else 0.0
            footprints[ref] = dict(x=x, y=y, rot=rot,
                                   layer=layer_of(node), fpid=fpid)
        elif node and isinstance(node, list) and node[0] in (
                'gr_line', 'gr_arc', 'gr_rect', 'gr_circle', 'gr_poly'):
            if layer_of(node) != 'Edge.Cuts':
                continue
            for h in ('start', 'end', 'mid'):
                p = pt(node, h)
                if p: outline.append(p)
            if node[0] == 'gr_poly':
                pts = first(node, 'pts')
                if pts:
                    for xyn in children(pts, 'xy'):
                        outline.append((float(xyn[1]), float(xyn[2])))
    return outline, footprints

# ---------- gerber parsing ----------
def gerber_points(path):
    text = path.read_text()
    m = re.search(r'%FS[LT]A[IX](\d)(\d)(\d)(\d)\*%', text)
    if m:
        xi, xd = int(m.group(1)), int(m.group(2))
    else:
        xi, xd = 4, 6
    pts = []
    for mm in re.finditer(r'(?:G0?[123]\s*)?(?:X(-?\d+))?(?:Y(-?\d+))?(?:I-?\d+)?(?:J-?\d+)?(D0[123])?\*', text):
        xs, ys, d = mm.group(1), mm.group(2), mm.group(3)
        if xs is None and ys is None:
            continue
        if d == 'D03' or (xs is not None and ys is not None):
            if xs is None or ys is None:
                continue
            def cv(s):
                sign = -1 if s.startswith('-') else 1
                s2 = s.lstrip('-').rjust(xi + xd, '0')
                return sign * (int(s2[:-xd]) + int(s2[-xd:]) / 10**xd) if xd else sign * int(s2)
            pts.append((cv(xs), cv(ys)))
    return pts

def fit_and_verify(kpts, gpts):
    # Candidates: pair the first pcb outline vertex with every gerber vertex.
    # Score by exact hits on a 0.0005 mm grid (gerber files may carry stray
    # moves, e.g. to the origin, so a bbox fit is not robust). Then report the
    # true worst nearest-neighbour deviation under the winning translation.
    gset = {(round(x * 2000), round(y * 2000)) for (x, y) in gpts}
    kx0, ky0 = kpts[0]
    best = None
    for (gx, gy) in gpts:
        tx, ty = gx - kx0, gy + ky0
        hits = sum(1 for (x, y) in kpts
                   if (round((x + tx) * 2000), round((-y + ty) * 2000)) in gset)
        if best is None or hits > best[0]:
            best = (hits, tx, ty)
    _, tx, ty = best
    def nearest(p, arr):
        return min(math.hypot(p[0] - a[0], p[1] - a[1]) for a in arr)
    worst = max(nearest((x + tx, -y + ty), gpts) for (x, y) in kpts)
    return tx, ty, worst

# ---------- BOM maps ----------
def load_rev6_map():
    mp = {}
    with open(Q / 'issue-226-main-rev6/manufacturing/BOM.csv', newline='') as fh:
        for r in csv.DictReader(fh):
            mp[r['Designator']] = (r['Comment'], r['LCSC Part #'])
    # adopted substitutes (docs/issue-175, PR #177/#189) for Rev.6's blank rows
    for d in ('C26', 'C27', 'C28'):
        mp[d] = ('C3225X7R1C226MT000N', 'C342699')
    mp['R17'] = ('RT0603BRD0754K9L', 'C728593')
    return mp

WING_MAP = {
    'DRV5055A3QDBZR': 'C266128',      # Matrix Rev.3 BOM (issue-182)
    'GRM188R71C104KA01D': 'C45000',   # Matrix Rev.3 BOM
    'TMUX1208PWR': 'C494728',         # Matrix Rev.3 BOM
}

def read_csv(path):
    with open(path, newline='') as fh:
        return list(csv.DictReader(fh))

def split_refs(s):
    return [r.strip() for r in s.replace('"', '').split(',') if r.strip()]

# ---------- per-board conversion ----------
def convert(board_dir, pcb_path, kind):
    man = board_dir / 'manufacturing'
    native_bom = read_csv(man / 'BOM.csv')
    native_cpl = read_csv(man / 'CPL.csv')
    outline, footprints = board_geometry(pcb_path)
    gpts = gerber_points(man / 'gerber/main-Edge_Cuts.gm1')
    tx, ty, outline_dev = fit_and_verify(outline, gpts)

    rev6 = load_rev6_map() if kind == 'main' else {}
    bom_rows, unmapped, excluded = [], [], []
    orderable = set()
    for r in native_bom:
        comment, refs = r['Comment'], split_refs(r['Designator'])
        if comment.startswith('NPTH') or comment.startswith('PCB_PAD') \
                or comment == 'TestPoint':
            excluded.append((comment, refs)); continue
        if comment.startswith('FH12'):
            bom_rows.append([comment, r['Designator'],
                             footprints[refs[0]]['fpid'], 'C-HIROSE-FH12-14S'])
            orderable.update(refs); continue
        if kind == 'main':
            got = [rev6.get(d) for d in refs]
            if any(g is None for g in got):
                unmapped.extend(d for d, g in zip(refs, got) if g is None)
                continue
            mpn, lcsc = got[0]
            if any(g != got[0] for g in got):
                unmapped.extend(refs); continue
            bom_rows.append([mpn, r['Designator'],
                             footprints[refs[0]]['fpid'], lcsc])
            orderable.update(refs)
        else:
            lcsc = WING_MAP.get(comment)
            if lcsc is None:
                unmapped.extend(refs); continue
            bom_rows.append([comment, r['Designator'],
                             footprints[refs[0]]['fpid'], lcsc])
            orderable.update(refs)

    with open(man / 'BOM-jlcpcb.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
        w.writerows(bom_rows)

    cpl_rows, cpl_dev, missing = [], 0.0, []
    native_by_ref = {r['Ref'].strip('"'): r for r in native_cpl}
    for ref in sorted(orderable):
        r = native_by_ref.get(ref)
        fp = footprints.get(ref)
        if r is None or fp is None:
            missing.append(ref); continue
        gx, gy = float(r['PosX']) + tx, float(r['PosY']) + ty
        ex, ey = fp['x'] + tx, -fp['y'] + ty
        cpl_dev = max(cpl_dev, math.hypot(gx - ex, gy - ey))
        cpl_rows.append([ref, f'{gx:.6f}mm', f'{gy:.6f}mm',
                         r['Side'].strip().lower(), f"{float(r['Rot']):.6f}"])
    with open(man / 'CPL-jlcpcb-gerber-frame.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
        w.writerows(cpl_rows)

    return dict(board=board_dir.name, bom_rows_total=len(native_bom),
                bom_rows_written=len(bom_rows),
                orderable_designators=len(orderable),
                unmapped=unmapped, excluded=[c for c, _ in excluded],
                missing_cpl=missing, frame_offset=[tx, ty],
                outline_max_dev_mm=outline_dev, cpl_max_dev_mm=cpl_dev,
                cpl_rows=len(cpl_rows))

if __name__ == '__main__':
    jobs = [('main-rev8', I263 / 'main-rev8',
             I263 / 'inspection/final/main.kicad_pcb', 'main')]
    for name in ('wing-rev5-17mm-left', 'wing-rev5-17mm-right',
                 'wing-rev5-16mm-left', 'wing-rev5-16mm-right'):
        jobs.append((name, I263 / name, I263 / name / 'main.kicad_pcb', 'wing'))
    results = []
    for _, bdir, pcb, kind in jobs:
        res = convert(bdir, pcb, kind)
        results.append(res)
        print(json.dumps(res, ensure_ascii=False))
    (OUT / 'conversion-results.json').write_text(
        json.dumps(results, indent=1, ensure_ascii=False))
