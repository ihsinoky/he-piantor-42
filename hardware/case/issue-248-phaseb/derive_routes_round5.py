from pathlib import Path
import json,math
p=Path(__file__).resolve().parent;d=json.loads((p/'tuning-round/17mm/measurements.json').read_text())['wings'][1]
# Reconstruct separated lanes analytically. Pin index comes exclusively from
# the independently verified native correspondence, not the inherited order.
pinmap=json.loads((p/'pinmap-round4.json').read_text());right=[w for w in pinmap['wires'] if w['side']=='right']
fitted=json.loads((p/'round3/17mm/measurements.json').read_text())['wings'][1]['analytic_segments'][0]
centre=(fitted['before'][-1][0]+fitted['after'][0][0])/2
before=[];after=[]
for i,w in enumerate(right):
 lane=13-i
 pack=[((c-(count-1)/2)*1.01,(row-1.5)*math.sqrt(3)/2*1.01) for row,count in enumerate((4,3,4,3)) for c in range(count)]
 dx,dz=pack[lane];z=4.1+dz;x=w['wing_endpoint_mm'][0]
 a=[[x,-34.95,5.75],[x,-31.8,5.75],[x,-28.8,5.1],[x,-24.3,5.1],[centre-6.55+dx,-13.5,z],[centre-6.55+dx,10.55,z]]
 upper=[((j-2)*1.05,-.91) for j in range(5)]+[((j-2)*1.05+.525,0) for j in range(5)]+[((j-1.5)*1.05,.91) for j in range(4)]
 off,uz=upper[i];ep=w['main_endpoint_mm'];angle=math.radians(120)
 ap=[ep[0]+7*math.sin(angle),ep[1]+7*math.cos(angle),10.65]
 b=[[centre+6.55-dx,10.55,z],[centre+6.55-dx,-9,z],[5+off,-18,z],[5+off,-7,10.5+uz],[17+off,8,10.5+uz],ap,ep]
 before.append(a);after.append(b)
out=dict(before=before,after=after,centre_x_mm=centre,turn_centre_y_mm=17.1,turn_tangent_offset_mm=6.55,service_travel_mm=15.1,provenance='Analytic reconstruction of separated Wing corridor and low horizontal concentric reserve from tuning-round/17mm/measurements.json, with reserve centre re-derived from the frozen round-3 assembly turn endpoints; every strand reassigned from immutable round-4 native pin map; upper fan follows corrected Main cavity order. Stored/released datum is Y17.1/Y2.0; arc tangent is 6.55 mm north of that datum.')
(p/'routes-round5.json').write_text(json.dumps(out,indent=2)+'\n')
