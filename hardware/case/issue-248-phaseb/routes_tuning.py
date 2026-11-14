"""Separated Wing corridor fan, exact offset spine, and connected Main fan."""
from common import *
from transport import offset_path

def pack(i):
 p=[]
 for row,count in enumerate((4,3,4,3)):
  for col in range(count):p.append((((count-1)/2-col)*1.08,(row-1.5)*math.sqrt(3)/2*1.08))
 return p[i]
def route(i,south=22.1,slot=None):
 if slot is None:slot=i
 dx,dz=pack(slot)
 spine=[[8.4,-13,3.95],[8.4,south,3.95],[24.4,south,3.95],[24.4,-5,3.95],[12,-21,3.95],[4,-7,14.8],[17,8,14.8],[23,17,14.8]]
 middle,start,end,radii,slack=offset_path(spine,dx,dz)
 x=27+(i-6.5)*1.25
 col=slot if slot<4 else slot-4 if slot<7 else slot-7 if slot<11 else slot-11
 entry=[[x,-34.95,5.75],[x,-33.6,5.75],[x,-27.5+col*1.08,start[2]],[start[0],-24+col*1.08, start[2]],list(start)]
 before=rounded(entry)
 u=(i-6.5)*1.25;a=math.radians(120)
 ep=np.array([17.102146+u*math.cos(a)+5.55*math.sin(a),42.075001-u*math.sin(a)+5.55*math.cos(a),10.65])
 ap=ep+np.array([7*math.sin(a),7*math.cos(a),0])
 tangent=np.array([6.,9,0]);tangent/=np.linalg.norm(tangent)
 exit=[list(end),list(end+tangent*7),list(ap),list(ep)]
 after=rounded(exit)
 path=Wire([*before.edges(),*middle.edges(),*after.edges()])
 return path,dict(entry=entry,spine=spine,exit=exit,offset_mm=[dx,dz],minimum_radius_mm=min(5,*radii),minimum_straight_slack_mm=slack)
if __name__=='__main__':
 from scipy.spatial import cKDTree
 paths=[];samples=[]
 for i in range(14):
  try:
   p,m=route(i);paths.append(p);samples.append(np.array([tuple(v) for v in p.positions([j/1000 for j in range(1001)])]));print(i,p.length,flush=True)
  except Exception as e:print(i,repr(e),flush=True);raise
 for i in range(14):
  for j in range(i):
   dd,ii=cKDTree(samples[j]).query(samples[i]);k=dd.argmin()
   if dd[k]<1.01:print('NEAR',i,j,dd[k],samples[i][k],samples[j][ii[k]],flush=True)
