"""Per-part engineering projections and parameter/dimension register; no hidden CAD edits."""
from common import *
from html import escape
def drawing(q,n,path):
 b=bounds(q);size=[b[1][i]-b[0][i] for i in range(3)]
 paths=[]
 for e in q.edges():
  try:paths.append([[v.X,v.Y,v.Z] for v in e.positions([i/12 for i in range(13)])])
  except Exception:pass
 def project(a,axis):return (a[0]-b[0][0],a[axis]-b[0][axis])
 width=max(120,size[0])+20; height=max(40,size[1])+max(25,size[2])+65
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',f'<rect width="{width}" height="{height}" fill="white"/>',f'<text x="5" y="6" font-size="3">{escape(n)} / mm / PROVISIONAL plateau Z{TOP:.2f}, Junana q=1.50</text>']
 for axis,yoff,label in [(1,15,'TOP XY'),(2,max(40,size[1])+30,'SIDE XZ')]:
  svg.append(f'<text x="5" y="{yoff-2}" font-size="3">{label}</text>')
  for pts in paths:
   xy=[project(a,axis) for a in pts]
   svg.append('<polyline fill="none" stroke="#17344c" stroke-width="0.12" points="'+' '.join(f'{x+10:.4f},{y+yoff:.4f}' for x,y in xy)+'"/>')
 svg.append(f'<text x="5" y="{height-15}" font-size="3">XYZ {size[0]:.3f} x {size[1]:.3f} x {size[2]:.3f}; 5 mm brim on every XY side.</text>')
 svg.append(f'<text x="5" y="{height-10}" font-size="2.7">PETG; nominal shell walls / normal roof 2.00; slope start Y{START:.6f}, toe Y{TOE:.6f}.</text>')
 svg.append(f'<text x="5" y="{height-5}" font-size="2.7">Assembly coordinates retained in STEP. STEP governs detail; inspect gate table before manufacture.</text></svg>')
 path.write_text('\n'.join(svg))
def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch);m=read(out/'manufacturing.json');groups={}
 for n,k,s in raw:groups.setdefault(n,[]).append(s)
 for p in m['parts']:
  ss=groups[p['name']];q=ss[0] if len(ss)==1 else Compound(children=ss)
  drawing(q,p['name'],out/'manufacturing'/(p['filename']+'.svg'))
 # Numerical drawing register supplies explicit absolute datums for every print.
 save(out/'manufacturing/dimension-register.json',dict(status=P['status'],units='mm',parameters=P,parts=m['parts'],instructions=dict(material='PETG; remade support posts and splices retain source fits',nominal_shell_wall_and_normal_roof_mm=2,source_plate='D-038 aluminium 1.50 mm; 14.00–14.04 apertures; unchanged manufacturing geometry',print='0.4 nozzle / 0.2 layer starting point; 5 wall lines; support roofs as required; remove supports through open underside; inspect dimensions',retention=read(out/'measurements.json')['retention'])))
if __name__=='__main__':run(int(sys.argv[1]))
