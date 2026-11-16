"""Stage 0: free north space measurement from #248 fitted bodies.
For each pitch/side: ray-sample in -Y at several Z bands; at each X find
wing PCB north edge Y and nearest tray material north of it -> gap.
Also dump connector-related body names/bounds."""
import sys, json
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlib18 as F
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.gp import gp_Pnt

from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
def bounds2(shape):
    b=Bnd_Box(); BRepBndLib.Add_s(shape,b,True)
    return ((b.GetXMin(),b.GetYMin(),b.GetZMin()),(b.GetXMax(),b.GetYMax(),b.GetZMax()))

from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
def _vol(shape):
    g=GProp_GProps(); BRepGProp.VolumeProperties_s(shape,g)
    return g.Mass()
def solids(shape):
    if shape is None or shape.IsNull(): return []
    out=[]; ex=TopExp_Explorer(shape, TopAbs_SOLID)
    while ex.More(): out.append(ex.Current()); ex.Next()
    out=[s for s in out if _vol(s) > 1e-6]
    return out if out else ([shape] if _vol(shape) > 1e-6 else [])

def W(s):
    return s.wrapped if hasattr(s,'wrapped') else s

def y_intervals(shape, x, z, y0=-75.0, y1=5.0):
    shape=W(shape)
    box = BRepPrimAPI_MakeBox(gp_Pnt(x-0.02, y0, z-0.05), gp_Pnt(x+0.02, y1, z+0.05)).Shape()
    com = BRepAlgoAPI_Common(shape, box); com.Build()
    ivs=[]
    for s in solids(com.Shape()):
        bb=bounds2(s); ivs.append((round(bb[0][1],3), round(bb[1][1],3)))
    return sorted(ivs)

out={}
for pitch in (17,16):
    bodies=dict(F.bodies_of(pitch))
    names=list(bodies)
    conn=[n for n in names if ('WING' in n or 'GH' in n or 'plug' in n.lower())]
    out[str(pitch)+'mm']={'conn_names':conn,
                'conn_bounds':{n:[[round(v,2) for v in pt] for pt in bounds2(W(bodies[n]))] for n in conn}}
    for side in ('left','right'):
        wing=bodies[f'wing_{side}']; tray=bodies[f'tray-{side}']
        wb=bounds2(W(wing))
        res={}
        for z in (5.0, 7.95, 11.0):
            rows=[]
            x=wb[0][0]+2.0
            while x < wb[1][0]-1.0:
                wiv=y_intervals(wing,x,z)
                if wiv:
                    edge=min(a for a,b in wiv)
                    tiv=y_intervals(tray,x,z)
                    north=[iv for iv in tiv if iv[1] <= edge+0.01]
                    wall=max((b for a,b in north), default=None)
                    gap=round(edge-wall,3) if wall is not None else None
                    rows.append((round(x,1), round(edge,2), gap))
                x+=4.0
            res[f'z{z}']=rows
        out[str(pitch)+'mm'][side]=res
print(json.dumps(out))
