from common import *
import pcbnew as p
b=p.LoadBoard(str(R/'hardware/kicad/qualification/issue-155-main-mounting-stage2/inspection/final/main.kicad_pcb'))
for f in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
 v=f.GetPosition();print(f.GetReference(),f.GetValue(),p.ToMM(v.x),p.ToMM(v.y),f.GetOrientationDegrees(),[(a.GetNumber(),a.GetNetname(),p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y),p.ToMM(a.GetSize().x),p.ToMM(a.GetSize().y)) for a in f.Pads()] if f.GetReference() in ['U5','C18','C19','J2'] else '')
for d in b.GetDrawings():
 if d.GetLayer()==p.Edge_Cuts:print('EDGE',d.GetShape(),p.ToMM(d.GetStart().x),p.ToMM(d.GetStart().y),p.ToMM(d.GetEnd().x),p.ToMM(d.GetEnd().y))
