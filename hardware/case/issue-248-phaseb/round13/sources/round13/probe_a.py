import sys, json
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0,HERE)
from common import *
from audit_repair import load_round9, common_shape, shape_volume
D=read(HERE/'routes-round9.json'); B,A=D['before'],D['after']
def build(i):
    zf=A[i][3][2]; G=A[i][5]; ep=A[i][6]; fx=28.85-1.25*i
    return [B[i][0],B[i][1],[fx,-18.0,5.1],[fx,-7.0,zf],[fx+10.0,8.0,zf],G,ep]
idx,by_name=load_round9(17)
fixed={n:s for n,s in by_name.items() if not n.startswith('Wire')}
wires={}
for i in range(14):
    pts=build(i)
    path=rounded(pts)
    d0=np.array(pts[1])-np.array(pts[0])
    q=sweep(Face(Wire.make_circle(.5,Plane(origin=Vector(*pts[0]),z_dir=Vector(*map(float,d0))))),path=path)
    wires[f'A-right-{i+1:02d}']=q
    print('built',i+1,'len',round(path.length,2),flush=True)
# positive control: wire vs itself must return its own volume
_ctrl=common_shape(wires['A-right-01'],wires['A-right-01']); print('CONTROL self-common volume',round(shape_volume(_ctrl),2),flush=True)
hits={}
for wn,w in wires.items():
    for fn,f in fixed.items():
        try:
            c=common_shape(w, f)
            v=shape_volume(c) if c is not None else 0.0
        except Exception as e:
            v=-1; print('ERR',wn,fn,e,flush=True)
        if v and v>1e-6: hits.setdefault(wn,{})[fn]=round(v,4)
print('WIRE-FIXED HITS:',json.dumps(hits),flush=True)
# fitted wire-wire for the 4 screen pairs (pins 10-11,11-12,12-13,13-14 -> idx 9-10,10-11,11-12,12-13)
ww={}
names=list(wires)
for x,y in ((9,10),(10,11),(11,12),(12,13)):
    a,b=names[x],names[y]
    try:
        c=common_shape(wires[a],wires[b]); v=shape_volume(c) if c is not None else 0.0
    except Exception as e: v=-1; print('ERR WW',a,b,e,flush=True)
    ww[f'{a} x {b}']=round(v,4)
print('FITTED SCREEN-PAIR VOLUMES:',json.dumps(ww),flush=True)
json.dump({'wire_fixed':hits,'fitted_pairs':ww},open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round13/probe_a.json','w'),indent=1)
