"""Actual OCCT worst-point sections from study-b1.py; system matplotlib."""
import os,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;RUN=HERE.parents[2]/'.issue248-runtime'
os.environ.update(TMPDIR=str(RUN),MPLCONFIGDIR=str(RUN/'mpl'),XDG_CACHE_HOME=str(RUN/'cache'),MPLBACKEND='Agg')
import matplotlib.pyplot as plt
rows=json.loads((HERE/'b1/sections-b1.json').read_text())
fig,axes=plt.subplots(1,2,figsize=(15,6))
for ax,(ref,s) in zip(axes,rows.items()):
 for key,color,ls,label in [('roof','#986623','-','Unmodified B0 roof, 2.00 mm skin'),('header','#224b92','-','Header drawing bound'),('plug_latch_bound','#b24d7e','--','Seated plug + latch drawing bound')]:
  for i,e in enumerate(s[key]):ax.plot([v[0] for v in e],[v[1] for v in e],color=color,ls=ls,lw=1.8,label=label if i==0 else None)
 x,y,z=s['worst_point_mm']
 ax.plot(y,z,'o',color='#bd2525',ms=5)
 ax.annotate('',xy=(y,11.55),xytext=(y,z),arrowprops=dict(arrowstyle='<->',color='#bd2525',lw=2))
 ax.annotate('1.350000 mm interference',xy=(y,12.1),xytext=(38,15),arrowprops=dict(arrowstyle='->',color='#bd2525'),color='#bd2525',fontsize=9)
 ax.axhline(13.2,color='#19815a',ls=':',label='Required closed ceiling Z13.20')
 ax.axhline(15.2,color='#19815a',ls='--',label='Required 2 mm skin top Z15.20')
 ax.set(xlim=(29,54),ylim=(8,18),aspect='equal',xlabel='Assembly Y south (mm)',ylabel='Provisional Z (mm)',title=f'{ref} | worst plateau section X{x:.6f}\nGap -1.350000 mm; required rise +1.650000 mm')
 ax.grid(alpha=.2);ax.legend(fontsize=7,loc='upper right')
fig.suptitle('B1 JST drawing-bounded mated GH / unchanged B0 roof',fontsize=14)
fig.text(.5,.025,'Undimensioned latch steps/cavities remain within drawing bounds; plotted boxes are not detailed mouldings. All Z provisional on q=1.50.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.06,1,.93));fig.savefig(HERE/'b1/section-gh-worst-b1.png',dpi=180)
