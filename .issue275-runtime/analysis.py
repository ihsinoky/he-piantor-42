import json, math, re

# ---------- load board segments/vias (own mini parse of the sexpr) ----------
PATH = "hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb"
text = open(PATH).read()
def tokenize(s):
    toks, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c in ' \t\r\n': i += 1
        elif c in '()': toks.append(c); i += 1
        elif c == '"':
            j = i+1; buf = []
            while j < n and s[j] != '"':
                if s[j] == '\\' and j+1 < n: buf.append(s[j+1]); j += 2
                else: buf.append(s[j]); j += 1
            toks.append(('str', ''.join(buf))); i = j+1
        else:
            j = i
            while j < n and s[j] not in ' \t\r\n()': j += 1
            toks.append(s[i:j]); i = j
    return toks
def parse(toks):
    stack = [[]]
    for t in toks:
        if t == '(': stack.append([])
        elif t == ')':
            node = stack.pop(); stack[-1].append(node)
        else: stack[-1].append(t)
    return stack[0][0]
tree = parse(tokenize(text))
def head(n): return n[0] if isinstance(n, list) and n else None
def find_all(n, name): return [c for c in n if isinstance(c, list) and head(c) == name]
def find1(n, name):
    for c in n:
        if isinstance(c, list) and head(c) == name: return c
    return None
def unwrap(v): return v[1] if isinstance(v, tuple) else v
def xy(n, name):
    c = find1(n, name); return (float(c[1]), float(c[2])) if c else None

NETS = {}
for n in find_all(tree, 'net'):
    NETS[int(n[1])] = unwrap(n[2])

segs = []
for s in find_all(tree, 'segment'):
    a, b = xy(s, 'start'), xy(s, 'end')
    w = float(find1(s, 'width')[1]); lay = unwrap(find1(s, 'layer')[1])
    net = NETS.get(int(find1(s, 'net')[1]), '?')
    segs.append((a, b, w, lay, net))
vias = []
for v in find_all(tree, 'via'):
    p = xy(v, 'at'); sz = float(find1(v, 'size')[1])
    net = NETS.get(int(find1(v, 'net')[1]), '?')
    vias.append((p, sz, net))
print('segments', len(segs), 'vias', len(vias))

# ---------- FH12 pad local geometry from extract ----------
d = json.load(open('.issue275-runtime/extract.json'))
def fp(ref): return next(x for x in d['footprints'] if x['ref'] == ref)
def rot2d(x, y, deg):
    r = math.radians(deg)
    return (x*math.cos(r)-y*math.sin(r), x*math.sin(r)+y*math.cos(r))
j2, j3 = fp('J2'), fp('J3')
# local pad offsets for J2 (its own frame), reused for any pose (same footprint)
locals_ = []
for p in j2['pads']:
    lx, ly = p['abs'][0]-j2['at'][0], p['abs'][1]-j2['at'][1]
    ux, uy = rot2d(lx, ly, -j2['rot'])
    locals_.append((p['num'], ux, uy))
def pads_at(centre, rot):
    out = {}
    for num, ux, uy in locals_:
        rx, ry = rot2d(ux, uy, rot)
        out[num] = (centre[0]+rx, centre[1]+ry)
    return out

AXIS = 100.0
def mirror(centre, rot): return ((2*AXIS-centre[0], centre[1]), -rot)
J2P, J3P = (tuple(j2['at']), j2['rot']), (tuple(j3['at']), j3['rot'])
cands = {
 'a_mirror_J2': {'J2': J2P, 'J3': mirror(*J2P)},
 'b_mirror_J3': {'J2': mirror(*J3P), 'J3': J3P},
 'c_middle': {
   'J2': (((J2P[0][0]+mirror(*J3P)[0][0])/2, (J2P[0][1]+mirror(*J3P)[0][1])/2), (J2P[1]-mirror(*J3P)[1])/2*-1),
   'J3': (((J3P[0][0]+mirror(*J2P)[0][0])/2, (J3P[0][1]+mirror(*J2P)[0][1])/2), -(J2P[1]-mirror(*J3P)[1])/2*-1)},
}
# fix c rotations explicitly: J2 +40.5, J3 -40.5
cands['c_middle']['J2'] = (cands['c_middle']['J2'][0], 40.5)
cands['c_middle']['J3'] = (cands['c_middle']['J3'][0], -40.5)

def seg_pt_dist(a, b, p):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx-ax, by-ay
    L2 = dx*dx+dy*dy
    t = 0 if L2 == 0 else max(0, min(1, ((px-ax)*dx+(py-ay)*dy)/L2))
    qx, qy = ax+t*dx, ay+t*dy
    return math.hypot(px-qx, py-qy)

PAD_R = 0.75  # bounding radius of the FH12 signal land (1.30 long) for threat sweep
res = {}
for cname, cand in cands.items():
    entry = {}
    for site, cur in (('J2', J2P), ('J3', J3P)):
        newc, newr = cand[site]
        old_pads = pads_at(*cur); new_pads = pads_at(newc, newr)
        disp = max(math.hypot(new_pads[k][0]-old_pads[k][0], new_pads[k][1]-old_pads[k][1]) for k in old_pads)
        # copper threat: segments/vias (other nets excluded by net match to site nets)
        site_nets = {p['net'][1] for p in fp(site)['pads'] if p['net']}
        threats = []
        for (a, b, w, lay, net) in segs:
            if net in site_nets: continue
            dold = min(seg_pt_dist(a, b, p) for p in old_pads.values()) - w/2
            dnew = min(seg_pt_dist(a, b, p) for p in new_pads.values()) - w/2
            if dnew < 0.30 and dold >= 0.30:
                threats.append(('seg', net, lay, round(dnew, 3)))
        for (p, sz, net) in vias:
            if net in site_nets: continue
            dold = min(math.hypot(p[0]-q[0], p[1]-q[1]) for q in old_pads.values()) - sz/2
            dnew = min(math.hypot(p[0]-q[0], p[1]-q[1]) for q in new_pads.values()) - sz/2
            if dnew < 0.30 and dold >= 0.30:
                threats.append(('via', net, '', round(dnew, 3)))
        entry[site] = {'new_centre': [round(newc[0], 4), round(newc[1], 4)], 'new_rot': newr,
                       'centre_shift': round(math.hypot(newc[0]-cur[0][0], newc[1]-cur[0][1]), 4),
                       'max_pad_disp': round(disp, 3), 'new_threats': threats}
    res[cname] = entry
json.dump(res, open('.issue275-runtime/candidates.json', 'w'), indent=1)
for cname, e in res.items():
    for site, v in e.items():
        print(cname, site, 'centre', v['new_centre'], 'rot', v['new_rot'],
              'shift', v['centre_shift'], 'maxpaddisp', v['max_pad_disp'], 'threats', v['new_threats'])
