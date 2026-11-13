"""Diagnostic top view and YZ routing projection; exact audit controls fit verdict."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
H=Path(__file__).resolve().parent;R=H.parents[2]
def read(p):return json.loads(p.read_text())
for folder in sorted(H.glob('delta-*')):
 for p in sorted(folder.glob('*mm')):
  if not (p/'audit.json').exists():continue
  d=read(p/'measurements.json');a=read(p/'audit.json');delta=d['delta_mm'];pitch=d['pitch_mm']
  verdict='PASS' if a['interference_zero'] else 'REJECTED'
  boards=read(R/f'hardware/case/issue-198-final/{pitch}mm/dimensions.json')['boards']
  fig,ax=plt.subplots(figsize=(12,9))
  for n in ['wing_left','wing_right','main']:
   ax.add_patch(Patch(boards[n],fc='#c3d9c6',ec='#536f57',alpha=.65));xy=boards[n];ax.text(sum(v[0] for v in xy)/len(xy),sum(v[1] for v in xy)/len(xy),n,fontsize=9)
  cp=d['cover_outline']; polygons=cp['coordinates'] if cp['type']=='MultiPolygon' else [cp['coordinates']]
  for k,polygon in enumerate(polygons):
   x,y=zip(*polygon[0]);ax.plot(x,y,'k--',lw=1,label='Flush cover edge' if k==0 else None)
  for w,c in zip(d['wings'],['#c96724','#245caa']):
   pts=w['lower_waypoints_mm'];ax.plot([v[0] for v in pts],[v[1] for v in pts],color=c,lw=5,alpha=.45,label=f"{w['side']} OD5 U; 32 mm reserve")
   for row in w['upper_samples_mm']:ax.plot([v[0] for v in row],[v[1] for v in row],color=c,lw=.5)
  f=d['fly']['path_samples_mm'];ax.plot([v[0] for v in f],[v[1] for v in f],color='#8f42b5',lw=2,label='Connected Fly 170 mm')
  for x,y in d['retention_sites_mm']:ax.plot(x,y,'ko',ms=4)
  ax.set(xlim=(-150,150),ylim=(85,-75),xlabel='X (mm)',ylabel='Y (mm)',aspect='equal',title=f'Issue 244 / Delta {delta:g} mm / pitch {pitch} mm / {verdict}\nTop projection: overlap in this view does not establish a 3D collision')
  ax.legend(loc='lower right',fontsize=8);ax.grid(alpha=.15);fig.tight_layout()
  for ext in ['svg','png']:fig.savefig(p/f'top-view.{ext}',dpi=160)
  plt.close(fig)
  fig,(ax,bx)=plt.subplots(2,1,figsize=(12,9),gridspec_kw={'height_ratios':[3,1]})
  for z,label in [(0,'Floor'),(2,'Nominal floor top'),(10+delta,'PCB underside'),(11.2+delta,'PCB top'),(16.2+delta,'Flush Wing deck + cover')]:
   ax.axhline(z,color='gray',lw=.7);ax.text(72,z+.1,label,fontsize=8)
  for w,c in zip(d['wings'],['#c96724','#245caa']):
   for row in w['upper_samples_mm']:ax.plot([v[1] for v in row],[v[2]+delta for v in row],color=c,lw=.7)
   pts=w['lower_waypoints_mm'];ax.plot([v[1] for v in pts],[v[2]+delta for v in pts],color=c,lw=5,alpha=.4)
  ax.plot([v[1] for v in f],[v[2]+delta for v in f],color='#8f42b5',lw=2,label='Fly OD2')
  contacts=read(p/'collision-map.json') if (p/'collision-map.json').exists() else []
  for r in contacts:
   lo,hi=r['overlap_bounds_mm'];ax.add_patch(plt.Rectangle((lo[1],lo[2]),hi[1]-lo[1],hi[2]-lo[2],fc='red',alpha=.2))
  ax.set(xlim=(-60,85),ylim=(-1,19+delta),xlabel='Y (mm)',ylabel='Z (mm)',title=f'Delta {delta:g} / {verdict}: YZ projection of cable centerlines; red = exact contact bounds\nThis is a projection, not an X-constant clearance section. Tube radii are not drawn.')
  ax.grid(alpha=.2)
  bx.axis('off');bx.text(.02,.8,f'GH section: top {16.2+delta:.2f}; pocket ceiling {15.95+delta:.2f}; skin 0.25 mm\nFly: stored axis {14.6+delta:.2f}; ceiling {15.8+delta:.2f}; skin 0.40 mm\nNorth: OD8 pillar to {14.7+delta:.2f}; AF4 x 1.6 nut; M2x6 flush screw\nSouth: 3 mm POM spacer; Main washer top {11.7+delta:.2f}; M2x10 screw\nExact unexpected contacts: {len(a["unexpected_interferences"])}; Boolean errors: {len(a["boolean_errors"])}',va='top',transform=bx.transAxes)
  fig.tight_layout()
  for ext in ['svg','png']:fig.savefig(p/f'sections.{ext}',dpi=160)
  plt.close(fig)
