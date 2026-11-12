"""PO gate drawing from measured outline vertices; system matplotlib."""
from pathlib import Path
import json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
E=Path(__file__).resolve().parent
p=json.loads((E/'geometry-plan.json').read_text());s=json.loads((E/'inspection/final/snapshot.json').read_text());fig,axs=plt.subplots(1,4,figsize=(18,6),gridspec_kw={'width_ratios':[2.2,1,1,1]})
for ax in axs:
 for label,key,color,style in [('Rev.5','rev5_polygon_mm','#d27731','--'),('Rev.6','rev6_polygon_mm','#137b89','-')]:
  vs=p[key]+p[key][:1];ax.plot([v[0] for v in vs],[v[1] for v in vs],style,color=color,label=label,lw=2)
 for c in s['components']:
  if c['ref'] in ['H1','H2','H3']:
   x,y=c['position'];ax.add_patch(Circle((x,y),1.1,fill=False,color='#444444',lw=1));ax.add_patch(Circle((x,y),2.5,fill=False,color='#777777',ls=':',lw=1))
 ax.set_aspect('equal');ax.grid(alpha=.15);ax.set_xlabel('KiCad X (mm)')
axs[0].set_title('Main Rev.6: all three tips removed');axs[0].set_ylabel('KiCad Y (mm)');axs[0].set_ylim(141,69);axs[0].legend(loc='upper right')
for ax,v in zip(axs[1:],p['vertices']):
 x,y=v['original_xy_mm'];ax.set_xlim(x-8,x+8);ax.set_ylim(y+8,y-8);ax.set_title(f"Vertex {v['vertex']}: 60° → 120° / 120°")
 a,b=v['face_endpoints_mm'];ax.annotate('4 mm face',xy=((a[0]+b[0])/2,(a[1]+b[1])/2),xytext=(x-7,y+6),arrowprops={'arrowstyle':'->'},fontsize=9)
fig.suptitle('4 mm along each original side • 3.464 mm tip depth • holes and full Ø5 mm supports preserved',fontsize=13)
fig.tight_layout();fig.savefig(E/'outline-comparison.png',dpi=180)
