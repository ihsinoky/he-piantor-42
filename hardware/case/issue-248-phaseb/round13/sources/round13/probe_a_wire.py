import sys, json
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0,HERE)
from common import *
from audit_repair import load_round9, common_shape, shape_volume
i=int(sys.argv[1])
D=read(HERE/'routes-round9.json'); B,A=D['before'],D['after']
zf=A[i][3][2]; G=A[i][5]; ep=A[i][6]; fx=28.85-1.25*i
pts=[B[i][0],B[i][1],[fx,-18.0,5.1],[fx,-7.0,zf],[fx+10.0,8.0,zf],G,ep]
path=rounded(pts)
d0=np.array(pts[1])-np.array(pts[0])
w=sweep(Face(Wire.make_circle(.5,Plane(origin=Vector(*pts[0]),z_dir=Vector(*map(float,d0))))),path=path)
idx,by_name=load_round9(17)
wb=bounds(w); hits={}
for fn,f in by_name.items():
    if fn.startswith('Wire'): continue
    fb=bounds(f)
    if any(min(wb[1][k],fb[1][k])-max(wb[0][k],fb[0][k])<=-1e-7 for k in range(3)): continue
    try:
        c=common_shape(w,f); v=shape_volume(c) if c is not None else 0.0
    except Exception as e:
        v=-1; hits[fn]='ERR '+str(e)[:60]
    if v and v>1e-6: hits[fn]=round(v,4)
print('WIRE',i+1,'len',round(path.length,2),'HITS',json.dumps(hits),flush=True)
json.dump(hits,open(f'/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round13/probe_a_w{i+1:02d}.json','w'))
