"""Read-only nominal geometry survey of the accepted #121 board; stdlib only.

Run from any directory: python3 <this file> > measurements.json
Never saves a board, fills a zone, routes, or generates manufacturing data.
"""
from pathlib import Path
import collections
import hashlib
import json
import math
import re

ROOT = Path(__file__).resolve().parents[4]
PCB = 'hardware/kicad/qualification/issue-121-full-auto-conditions/evidence/inspection/main-cell1/krt/main.kicad_pcb'
BASE = Path(__file__).resolve().parent

def parse(path):
    stack = []
    root = None
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', path.read_text()):
        if token == '(':
            node = []
            if stack:
                stack[-1].append(node)
            else:
                root = node
            stack.append(node)
        elif token == ')':
            stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    assert not stack
    return root

def children(a, key):
    return [v for v in a if isinstance(v, list) and v and v[0] == key]

def child(a, key):
    return children(a, key)[0]

def pair(a, key):
    return list(map(float, child(a, key)[1:3]))

def rot(x, y, degrees):
    a = math.radians(degrees)
    return x*math.cos(a)+y*math.sin(a), -x*math.sin(a)+y*math.cos(a)

def segment_distance(x, y, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    t = max(0, min(1, ((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy))) if dx or dy else 0
    return math.hypot(x-a[0]-t*dx, y-a[1]-t*dy)

def rect_distance(x, y, box):
    return math.hypot(max(box[0]-x, 0, x-box[2]), max(box[1]-y, 0, y-box[3]))

def polygon_distance(x, y, points):
    inside = False
    for a,b in zip(points, points[1:]+points[:1]):
        if (a[1]>y)!=(b[1]>y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
            inside = not inside
    return 0 if inside else min(segment_distance(x,y,a,b) for a,b in zip(points,points[1:]+points[:1]))

def distance(x, y, item):
    if item['kind'] == 'track':
        return max(0, segment_distance(x, y, item['a'], item['b'])-item['width']/2)
    if item['kind'] == 'via':
        return max(0, math.dist((x,y), item['xy'])-item['diameter']/2)
    x, y = rot(x-item['xy'][0], y-item['xy'][1], -item['angle'])
    w, h = item['size']
    if item['shape'] == 'rect':
        return math.hypot(max(abs(x)-w/2, 0), max(abs(y)-h/2, 0))
    if item['shape'] == 'circle':
        assert w == h
        return max(0, math.hypot(x,y)-w/2)
    if item['shape'] == 'oval':
        return max(0, math.hypot(max(abs(x)-max(w-h,0)/2,0), max(abs(y)-max(h-w,0)/2,0))-min(w,h)/2)
    raise AssertionError(item['shape'])

def inventory():
    root = parse(ROOT / PCB)
    nets = {n[1]: n[2] for n in children(root, 'net')}
    pads, tracks, vias, fps = [], [], [], []
    for fp in children(root, 'footprint'):
        props = {p[1]:p[2] for p in children(fp, 'property')}
        ref = props['Reference']
        at = child(fp, 'at')
        fx, fy = map(float, at[1:3])
        angle = float(at[3]) if len(at)>3 else 0
        corners = []
        for p in children(fp, 'pad'):
            local = pair(p, 'at')
            dx, dy = rot(*local, angle)
            pat = child(p, 'at')
            pa = float(pat[3]) if len(pat)>3 else 0
            # KiCad stores pad orientation in board coordinates (also verified natively).
            size = pair(p, 'size')
            layers = child(p, 'layers')[1:]
            net = children(p,'net')
            record = dict(kind='pad', ref=ref, pad=p[1], uuid=child(p,'uuid')[1],
                xy=[fx+dx,fy+dy], angle=pa, size=size, shape=p[3], attribute=p[2],
                layers=layers, net=net[0][2] if net else '')
            if children(p, 'drill'):
                record['drill'] = child(p,'drill')[1:]
            pads.append(record)
            for cx in (-size[0]/2,size[0]/2):
                for cy in (-size[1]/2,size[1]/2):
                    rx,ry = rot(cx,cy,pa)
                    corners.append((record['xy'][0]+rx, record['xy'][1]+ry))
        box = [min(p[0] for p in corners), min(p[1] for p in corners),
               max(p[0] for p in corners), max(p[1] for p in corners)]
        fps.append(dict(ref=ref, value=props.get('Value'), xy=[fx,fy], angle=angle,
            layer=child(fp,'layer')[1], pad_hull_box=box,
            graphics_count=sum(len(children(fp,k)) for k in ('fp_line','fp_rect','fp_circle','fp_poly','fp_arc')),
            proposed_body_reservation_box=[box[0]-.5,box[1]-.5,box[2]+.5,box[3]+.5]))
    for t in children(root,'segment'):
        tracks.append(dict(kind='track',uuid=child(t,'uuid')[1],a=pair(t,'start'),b=pair(t,'end'),
            width=float(child(t,'width')[1]),layer=child(t,'layer')[1],net=nets[child(t,'net')[1]]))
    assert not children(root,'arc'), 'Arc tracks need an explicit distance implementation'
    for v in children(root,'via'):
        vias.append(dict(kind='via',uuid=child(v,'uuid')[1],xy=pair(v,'at'),diameter=float(child(v,'size')[1]),
            drill=float(child(v,'drill')[1]),layers=child(v,'layers')[1:],net=nets[child(v,'net')[1]]))
    edges = [g for g in children(root,'gr_line') if child(g,'layer')[1]=='Edge.Cuts']
    points = [pair(g,k) for g in edges for k in ('start','end')]
    bounds = [min(p[0] for p in points), min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]
    assert bounds == [76,78,124,122] and len(edges)==4
    assert len(pads)==199 and len(tracks)==540 and len(vias)==66
    assert all(v['diameter']==.6 and v['drill']==.3 for v in vias)
    assert len(fps)==49 and all(f['graphics_count']==0 for f in fps)
    # Courtyards were transferred as board graphics, not as footprint graphics.
    lines=[g for g in children(root,'gr_line') if child(g,'layer')[1]=='F.CrtYd']
    adj=collections.defaultdict(set)
    for g in lines:
        a,b=tuple(pair(g,'start')),tuple(pair(g,'end'))
        adj[a].add(b)
        adj[b].add(a)
    assert len(lines)==188 and all(len(v)==2 for v in adj.values())
    seen=set()
    courts=[]
    for start in sorted(adj):
        if start in seen: continue
        points=[start]
        previous=None
        current=start
        while True:
            nxt=next(p for p in sorted(adj[current]) if p!=previous)
            if nxt==start: break
            points.append(nxt)
            previous,current=current,nxt
        seen.update(points)
        owners=[f['ref'] for f in fps if polygon_distance(*f['xy'],points)<1e-9]
        assert len(owners)==1,owners
        courts.append(dict(ref=owners[0],points=[list(p) for p in points],stroke=.05))
    assert len(courts)==40
    assert set(f['ref'] for f in fps)-set(c['ref'] for c in courts)=={'J1','J2','U1','U3','Y1','TP1','TP2','TP3','TP4'}
    copper_graphics=[g for g in root if isinstance(g,list) and g and g[0].startswith('gr_') and child(g,'layer')[1].endswith('.Cu')]
    assert not copper_graphics
    return dict(bounds=bounds,thickness=float(child(child(root,'general'),'thickness')[1]),
        footprints=fps,pads=pads,tracks=tracks,vias=vias,board_graphic_courtyards=courts,
        zones=[dict(uuid=child(z,'uuid')[1],net=child(z,'net_name')[1],layer=child(z,'layer')[1],
                    filled_polygon_count=len(children(z,'filled_polygon'))) for z in children(root,'zone')])

def survey(inv):
    copper_pads = [p for p in inv['pads'] if p['attribute']!='np_thru_hole']
    # Provisional connector service reservations: design allocations, not certified body outlines.
    services = [dict(ref='J1-service',box=[79.5,76,90.5,86.5]),
                dict(ref='J2-service',box=[97,114.5,123,122])]
    def body_nearest(x,y):
        boxes = [(f['ref']+'-pad-hull+0.5',f['proposed_body_reservation_box']) for f in inv['footprints']]
        boxes += [(s['ref'],s['box']) for s in services]
        distances=[(rect_distance(x,y,box),ref) for ref,box in boxes]
        distances += [(max(0,polygon_distance(x,y,c['points'])-c['stroke']/2),c['ref']+'-actual-courtyard') for c in inv['board_graphic_courtyards']]
        return min(distances)
    def analyze(label,x,y,outline=None):
        bounds=outline or inv['bounds']
        groups={'pads':copper_pads,'tracks':inv['tracks'],'vias':inv['vias']}
        row=dict(label=label,xy=[x,y],local_xy=[x-bounds[0],y-bounds[1]],outline=bounds,
                 edge_center_distance=min(x-bounds[0],y-bounds[1],bounds[2]-x,bounds[3]-y))
        row['hole_edge_ligament']=row['edge_center_distance']-1.1
        row['keepout_to_edge']=row['edge_center_distance']-2.5
        row['head_4_5_to_edge']=row['edge_center_distance']-2.25
        row['groups']={}
        for name,items in groups.items():
            measured=sorted([(distance(x,y,i),i) for i in items],key=lambda p:(p[0],p[1]['uuid']))
            d,i=measured[0]
            row['groups'][name]=dict(nearest=i,center_to_copper=d,keepout_gap=d-2.5,hole_gap=d-1.1,
                keepout_hits=[dict(item=j,center_to_copper=d,keepout_gap=d-2.5) for d,j in measured if d<2.5-1e-9],
                hole_hits=[j['uuid'] for d,j in measured if d<1.1-1e-9])
        d,ref=body_nearest(x,y)
        row['body_reservation_nearest']=dict(ref=ref,center_distance=d,keepout_gap=d-2.5)
        row['pad_track_via_clear']=all(not g['keepout_hits'] for g in row['groups'].values())
        row['provisional_body_clear']=d>=2.5
        row['nearest_nonplane_copper_gap']=min(g['keepout_gap'] for g in row['groups'].values())
        cd,ref=min((max(0,polygon_distance(x,y,c['points'])-c['stroke']/2),c['ref']) for c in inv['board_graphic_courtyards'])
        row['actual_courtyard_nearest']=dict(ref=ref,center_distance=cd,keepout_gap=cd-2.5)
        drills=[]
        for p in inv['pads']:
            if 'drill' not in p: continue
            d=p['drill']
            size=list(map(float,d[1:3])) if d[0]=='oval' else [float(d[0])]*2
            drills.append(dict(kind='pad',shape='oval' if d[0]=='oval' else 'circle',size=size,angle=p['angle'],xy=p['xy'],ref=p['ref'],uuid=p['uuid']))
        for v in inv['vias']:
            drills.append(dict(kind='pad',shape='circle',size=[v['drill']]*2,angle=0,xy=v['xy'],ref='via',uuid=v['uuid']))
        dd,di=min(((distance(x,y,d),d) for d in drills),key=lambda p:(p[0],p[1]['uuid']))
        row['nearest_existing_drill']=dict(item=di,proposed_drill_edge_gap=dd-1.1)
        return row
    candidates=[('NW-corner',79,81),('NE-corner',121,81),('SW-corner',79,119),('SE-corner',121,119),
                ('W-upper',79,92),('E-middle',121,98),('N-inner',96,81),('E-lower',121,112),
                ('W-middle',79,100),('S-middle',94,119),('W-narrow',79,93.5),
                ('S-inner',105,111),('S-inner-alt',104,112),('S-clear-narrow',101.5,110.5),('S-proposed',102,111.5),
                ('extension-NW',73,81),('extension-NE',127,81),('extension-SW',73,119),('extension-SE',127,119)]
    rows=[analyze(n,x,y,[70,78,130,122] if n.startswith('extension') else None) for n,x,y in candidates]
    scan=[]
    # Whole-board 0.5 mm lattice, 3 mm edge setback. Not a continuous existence proof.
    for ix in range(158,243):
        x=ix/2
        for iy in range(162,239):
            y=iy/2
            edge=min(x-76,y-78,124-x,122-y)
            d,ref=body_nearest(x,y)
            if d<2.5: continue
            ds=[min(distance(x,y,i) for i in items) for items in (copper_pads,inv['tracks'],inv['vias'])]
            scan.append(dict(x=x,y=y,edge=edge,pad_gap=ds[0]-2.5,track_gap=ds[1]-2.5,via_gap=ds[2]-2.5,
                             clear=min(ds)>=2.5))
    return dict(candidates=rows,body_reservation_note='Actual 40 board-graphic courtyard polygons plus every pad bounding box expanded by 0.5 mm each side and provisional connector service boxes. No certified 3D models; 5 mounted components lack courtyard polygons.',
        services=services,scan=dict(step=.5,edge_setback=3,total_lattice_points=85*77,component_screened_points=len(scan),
            clear_points=sum(r['clear'] for r in scan),points=scan))

def main():
    inv=inventory()
    result=dict(units='mm',frame='KiCad absolute, top view, X right, Y down; local origin = evaluated outline top left: retained (76,78), extended (70,78)',
        input=dict(path=PCB,sha256=hashlib.sha256((ROOT/PCB).read_bytes()).hexdigest()),inventory=inv,survey=survey(inv))
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
