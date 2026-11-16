"""Stage 0 supplement: full tray Y-intervals at tab-zone X samples ->
pocket wall thickness to the outer silhouette, Z bands 5.0 and 7.95."""
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
    for side in ('left','right'):
        tray=bodies[f'tray-{side}']; wing=bodies[f'wing_{side}']
        rows=[]
        xs=[-40,-32,-24,-16] if side=='left' else [16,24,32,40]
        for x in xs:
            wiv=y_intervals(wing,x,7.95); edge=min(a for a,b in wiv)
            tiv=y_intervals(tray,x,7.95)
            tiv5=y_intervals(tray,x,5.0)
            rows.append(dict(x=x, edge=round(edge,2),
                             tray795=[[a,b] for a,b in tiv if b<=edge+0.01],
                             tray50=[[a,b] for a,b in tiv5 if b<=edge+0.01]))
        out[f'{pitch}{side}']=rows
print(json.dumps(out, indent=1))
