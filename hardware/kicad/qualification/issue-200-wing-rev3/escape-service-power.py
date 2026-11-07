"""Exact radial, staggered 0.30mm power escapes for a boxed service MUX.
No rule relaxation. escape-pad.py checks all native pads and records copper
rip-up; qualify.py must reconnect every affected net and prove acceptance.
"""
from pathlib import Path
import pcbnew as p
import subprocess,sys,json,math
E=Path(__file__).resolve().parent;name=sys.argv[1];w=E/name
for pin,distance in [('14',2.1),('13',1.3)]:
 b=p.LoadBoard(str(w/'main.kicad_pcb'));f=next(f for f in b.GetFootprints() if f.GetReference()=='U_MUX_B');a=next(a for a in f.Pads() if a.GetNumber()==pin)
 # Local +X row; use the true native top-view rotation.
 theta=math.radians(f.GetOrientationDegrees());x=a.GetPosition().x/1e6+distance*math.cos(theta);y=a.GetPosition().y/1e6-distance*math.sin(theta)
 subprocess.run([sys.executable,str(E/'escape-pad.py'),name,'U_MUX_B',pin,str(x),str(y)],check=True)
(w/'service-power-escape-complete.json').write_text(json.dumps(dict(mux='U_MUX_B',pins=['14','13'],power_width_mm=.3,stagger_mm=.8))+'\n')
