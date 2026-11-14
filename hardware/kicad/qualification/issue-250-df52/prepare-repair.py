"""Expose footprint keepouts as board keepouts to the router, without relaxing them."""
from pathlib import Path
import sys,math,json,shutil
import pcbnew as p
E=Path(__file__).resolve().parent;T=E.parents[3]/'.issue250-runtime'
for name in sys.argv[1:]:
 w=E/name;b=p.LoadBoard(str(w/'main.kicad_pcb'));held=[]
 for f in b.GetFootprints():
  if f.GetReference() not in ('J2','J3','J_WING'):continue
  for area in f.Zones():
   z=p.ZONE(b);z.SetLayerSet(area.GetLayerSet());z.SetIsRuleArea(True);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowCopperPour(True);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False)
   poly=z.Outline();poly.NewOutline();o=area.Outline().Outline(0)
   # KiCad's footprint zone outline points are already in board coordinates.
   for i in range(o.PointCount()):v=o.CPoint(i);poly.Append(v.x,v.y)
   b.Add(z)
 if name=='main':
  for t in b.GetTracks():
   if t.GetNetname()=='MUX_OUT_B':held.append(t);b.Remove(t)
 p.SaveBoard(str(T/(name+'-repair-input.kicad_pcb')),b);shutil.copyfile(w/'main.kicad_pro',T/(name+'-repair-input.kicad_pro'))
