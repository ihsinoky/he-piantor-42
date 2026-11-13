import json
from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
E=Path(__file__).resolve().parent;d=json.loads((E/'drawings/plot-data.json').read_text());fig,ax=plt.subplots(figsize=(11,10));colors={'F.Cu':'#b44','B.Cu':'#4665aa','In1.Cu':'#aaa','In2.Cu':'#c98622'}
for t in d['tracks']:
 x,y=zip(*t['xy']);ax.plot(x,y,c=colors.get(t['layer'],'#aaa'),lw=max(.25,t['width']*2),alpha=.6)
for e in d['edges']:ax.plot(*zip(*e),c='black',lw=1.8)
for p in d['pads']:
 x,y=p['xy'];ax.plot(x,y,'o',ms=3,c='black')
 if p['number']=='1' or p['ref'].startswith('H'):ax.text(x+.3,y+.3,p['ref']+'.'+p['number'],fontsize=8)
ax.set(aspect='equal',xlabel='KiCad X / mm',ylabel='KiCad Y / mm',title='Issue 240 Main Rev.7 study — native routed copper');ax.invert_yaxis();ax.grid(alpha=.15)
for ext in ['svg','png']:fig.savefig(E/f'drawings/top-view.{ext}',dpi=200,bbox_inches='tight')
