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
 source_dimensions=read(HERE.parent/f'issue-232-final/{pitch}mm/dimensions.json')
 with (out/'manufacturing/BOM-PROVISIONAL.csv').open('w') as f:
  writer=csv.writer(f);writer.writerow(['part','quantity','material_or_acceptance_spec','status'])
  for p in m['parts']:writer.writerow([p['filename'],1,'PETG; see STEP and drawing',P['status']])
  writer.writerow(['north shell screw',2,'M2x4 under head; head at most OD3.6 x1.0; nominal envelope, supplier qualification pending',P['status']])
  writer.writerow(['north shell insert',2,'M2; OD3.2 x4.0; pilot OD2.8; pull-out qualification pending',P['status']])
 posts=[dict(p,top_z_mm=p['top_z_mm']-2.65,status=P['status']) for p in source_dimensions['posts']]
 for side in ('left','right'):
  with (out/'manufacturing'/f'post-positions-{side}-PROVISIONAL.csv').open('w') as f:
   fields=['id','x_mm','y_mm','base_z_mm','top_z_mm','status'];writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
   for p in posts:
    if p['side']==side:writer.writerow(dict(id=p['id'],x_mm=p['xy_mm'][0],y_mm=p['xy_mm'][1],base_z_mm=1.2,top_z_mm=p['top_z_mm'],status=P['status']))
 save(out/'manufacturing/dimension-register.json',dict(status=P['status'],units='mm',parameters=P,parts=m['parts'],posts=posts,splice_relocations=read(out/'measurements.json')['splice_relocations'],instructions=dict(material='PETG; remade support posts and splices retain source fits',nominal_shell_wall_and_normal_roof_mm=2,source_plate='D-038 aluminium 1.50 mm nominal, 1.45–1.51 finished; 14.00–14.04 apertures; unchanged manufacturing geometry',print='0.4 nozzle / 0.2 layer starting point; 5 wall lines; support roofs as required; remove supports through open underside; inspect dimensions',retention=read(out/'measurements.json')['retention'])))
if __name__=='__main__':run(int(sys.argv[1]))
