"""Bind each strand to the same numbered Wing/Main cavity, from native pads."""
from common import *
import sexpdata as sx
def rows(a,k):return [r for r in a if isinstance(r,list) and r and str(r[0])==k]
def pads(path,ref):
 doc=sx.loads(path.read_text())
 fp=next(f for f in rows(doc,'footprint') if any(p[1:3]==['Reference',ref] for p in rows(f,'property')))
 return {int(p[1]):dict(at=rows(p,'at')[0][1:3],net=rows(p,'net')[0][-1]) for p in rows(fp,'pad') if str(p[1]).isdigit() and 1<=int(p[1])<=14}
def run():
 from routes import segments
 mainfile=ROOT/'hardware/kicad/qualification/issue-240-main-rev7/inspection/final/main.kicad_pcb'
 wingdir=ROOT/'hardware/kicad/qualification/issue-235-wing-round2'
 main={side:pads(mainfile,ref) for side,ref in [('left','J2'),('right','J3')]};result=[]
 for side,sgn in [('left',-1),('right',1)]:
  wing=pads(wingdir/f'wing-rev4-17mm-{side}/routed.kicad_pcb','J_WING')
  for i in range(14):
   pin=i+1;a,b,r,mid=segments(sgn,i)
   wx=(-18.875-i*1.25) if side=='left' else (35.125-i*1.25)
   angle=sgn*math.radians(120);u=float(main[side][pin]['at'][0])
   expected=np.array([sgn*17.102146+u*math.cos(angle)+5.55*math.sin(angle),42.075001-u*math.sin(angle)+5.55*math.cos(angle),10.65])
   error=max(np.linalg.norm(np.array(a[0])-[wx,-34.95,5.75]),np.linalg.norm(np.array(b[-1])-expected))
   mn=main[side][pin]['net'];wn=wing[pin]['net']
   net_ok=mn==wn or (side=='right' and pin==7 and mn=='MUX_EN1' and wn=='WING_EN')
   result.append(dict(side=side,wire=pin,wing_pin=pin,main_pin=pin,wing_net=wn,main_net=mn,wing_endpoint_mm=a[0],main_endpoint_mm=b[-1],maximum_endpoint_error_mm=error,passed=error<1e-6 and net_ok))
 assert all(r['passed'] for r in result)
 save(HERE/'pinmap-round4.json',dict(passed=True,electrical_contract='D-024 / #235: each harness cavity 1→1 through 14→14; J3 pin7 is independent Main EN1 to Wing WING_EN',wing_coordinate_source='hardware/kicad/qualification/issue-235-wing-round2/REPORT.md line17 and connector/placement.json: right pin1 X35.125; left pin1 X-18.875',main_coordinate_source='native J2/J3 pad X=-8.125..8.125, B1 declared assembly poses, outlet local v=5.55',routes_sha256=sha(HERE/'routes-round4.json'),wires=result))
 print('28 native pad/physical outlet correspondences PASS',flush=True)
if __name__=='__main__':run()
