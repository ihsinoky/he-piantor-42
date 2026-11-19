import json, math
off = json.load(open('official-pads.json'))
tb = json.load(open('tb-pads.json'))
xs=[v[0] for v in off.values()]; ys=[v[1] for v in off.values()]
cx,cy=(min(xs)+max(xs))/2,(min(ys)+max(ys))/2
O=[(v[0]-cx, v[1]-cy) for v in off.values()]
T=[(p[0],p[1]) for p in tb]
def tf(p,n):
    x,y=p
    return {'id':(x,y),'rot90':(-y,x),'rot180':(-x,-y),'rot270':(y,-x),'flipx':(-x,y),'flipy':(x,-y),'flipxy':(y,x),'flipx_rot90':(-y,-x)}[n]
for n in ['id','rot90','rot180','rot270','flipx','flipy','flipxy','flipx_rot90']:
    Tt=[tf(p,n) for p in T]
    errs=[min(math.hypot(o[0]-t[0],o[1]-t[1]) for t in Tt) for o in O]
    print(f'{n:12s} official->TB max {max(errs):.3f} within0.05 {sum(1 for e in errs if e<0.05)}/78')
