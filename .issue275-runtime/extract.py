import json, math, re, sys

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

def head(node): return node[0] if isinstance(node, list) and node else None
def find_all(node, name):
    return [c for c in node if isinstance(c, list) and head(c) == name]
def find1(node, name):
    for c in node:
        if isinstance(c, list) and head(c) == name: return c
    return None
def val(node, name):
    c = find1(node, name)
    if not c: return None
    v = c[1]
    return v[1] if isinstance(v, tuple) else v
def xy(node, name):
    c = find1(node, name)
    return (float(c[1]), float(c[2])) if c else None

def rot2d(x, y, deg):
    r = math.radians(deg)
    return (x*math.cos(r)-y*math.sin(r), x*math.sin(r)+y*math.cos(r))

fps = []
for fp in find_all(tree, 'footprint'):
    name = fp[1][1] if isinstance(fp[1], tuple) else fp[1]
    at = find1(fp, 'at')
    fx, fy = float(at[1]), float(at[2])
    frot = float(at[3]) if len(at) > 3 else 0.0
    layer = val(fp, 'layer')
    ref = None
    for pr in find_all(fp, 'property'):
        if pr[1] == ('str','Reference') or (len(pr)>1 and pr[1]=='Reference'):
            ref = pr[2][1] if isinstance(pr[2], tuple) else pr[2]
    pads = []
    for pad in find_all(fp, 'pad'):
        pnum = pad[1][1] if isinstance(pad[1], tuple) else pad[1]
        pat = find1(pad, 'at')
        px, py = float(pat[1]), float(pat[2])
        prot = float(pat[3]) if len(pat) > 3 else 0.0
        rx, ry = rot2d(px, py, frot)
        drill = find1(pad, 'drill')
        net = find1(pad, 'net')
        pads.append({'num': pnum, 'abs': [fx+rx, fy+ry], 'rot': prot+frot,
                     'drill': float(drill[1]) if drill else None,
                     'net': net[2] if net and len(net)>2 else None,
                     'type': pad[2], 'shape': pad[3]})
    fps.append({'ref': ref, 'name': name, 'at': [fx, fy], 'rot': frot,
                'layer': layer, 'pads': pads})

edges = []
for gname in ('gr_line','gr_arc','gr_circle','gr_rect','gr_poly'):
    for g in find_all(tree, gname):
        if val(g, 'layer') != 'Edge.Cuts': continue
        e = {'kind': gname}
        for k in ('start','mid','end','center'):
            p = xy(g, k)
            if p: e[k] = list(p)
        edges.append(e)

out = {'footprints': fps, 'edges': edges}
json.dump(out, open('.issue275-runtime/extract.json','w'), indent=1)
for r in ('J2','J3','J4','H1','H2','H3'):
    f = next((x for x in fps if x['ref']==r), None)
    if f: print(r, f['name'][:40], 'at', f['at'], 'rot', f['rot'], f['layer'], 'pads', len(f['pads']))
print('total footprints', len(fps), 'edge elements', len(edges))
