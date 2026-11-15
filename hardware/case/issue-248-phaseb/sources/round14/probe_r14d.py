"""Fitted check of v4: worst strand pairs + all strands vs fixed bodies (17mm right)."""
import json, sys
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
from common import tube
from audit_repair import load_round9, common_shape, shape_volume, solid_distance
from design_r14 import design_points

HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json')); B,A=D['before'],D['after']
idx,by_name=load_round9('17')
wires={}
for i in range(14):
    pts=[tuple(p) for p in design_points(B,A,i)]
    solid,path=tube(pts,0.5)
    wires[i]=solid
    print(f'wire {i+1} len {path.length:.2f}',flush=True)
for (i,j) in ((0,2),(2,4),(0,1),(1,3),(4,6)):
    v=shape_volume(common_shape(wires[i],wires[j]))
    d=solid_distance(wires[i],wires[j]) if v<=1e-9 else 0.0
    print(f'pair {i+1}-{j+1}: common {v:.4f} distance {d:.3f}',flush=True)
print('--- fixed bodies ---',flush=True)
for name,shp in by_name.items():
    if name.startswith('Wire'): continue
    hits=[]
    for i in range(14):
        v=shape_volume(common_shape(wires[i],shp))
        if v>1e-4: hits.append((i+1,round(v,4)))
    if hits: print(f'{name}: {hits}',flush=True)
print('DONE',flush=True)
