"""Render OCCT section edges from study-b0.py, using system Matplotlib."""
import os,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];RUN=ROOT/'.issue248-runtime'
os.environ.update(TMPDIR=str(RUN),MPLCONFIGDIR=str(RUN/'mpl'),XDG_CACHE_HOME=str(RUN/'cache'),MPLBACKEND='Agg')
import matplotlib.pyplot as plt
data=json.loads((HERE/'b0/sections-b0.json').read_text())
for name,s in data.items():
 fig,ax=plt.subplots(figsize=(12,6))
 for key,c,lw,ls in [('roof','#b17426',2,'-'),('obstacle','#335eb0',1.5,'-'),('reservation','#999999',1,':')]:
  for i,edge in enumerate(s[key]):
   ax.plot([p[0] for p in edge],[p[1] for p in edge],color=c,lw=lw,ls=ls,label=({'roof':'A4 roof, 2.00 mm vertical skin','obstacle':s['label'],'reservation':'GH reservation ONLY, not detailed housing/plug'}[key]) if i==0 else None)
 if name=='fly':
  y=56;ax.annotate('',xy=(y,11.55),xytext=(y,12.95),arrowprops=dict(arrowstyle='<->',color='#bb2020',lw=2))
  ax.annotate('1.40 mm interference',xy=(y,12.25),xytext=(43,15),color='#bb2020',arrowprops=dict(arrowstyle='->',color='#bb2020'))
  ax.set(xlim=(26,64),ylim=(9.5,20))
  desc='Exact solid raw vertical gap -1.400000 mm; outer-surface gap +0.600000 mm'
 else:
  p=s['result']['worst']['witness_mm'];q=s['result']['worst']['roof_witness_mm']
  ax.plot([p[1],q[1]],[p[2],q[2]],color='#bb2020',lw=2,marker='o',ms=3)
  ax.text(p[1]-1,p[2]-1,f"Wire gap {s['result']['solid_distance_mm']:.6f} mm\nEuclidean minimum",ha='right',color='#bb2020')
  ax.set(xlim=(25,51),ylim=(8,19))
  desc='Exact terminal wire section; GH housing/plug exact clearance UNRESOLVED'
 ax.set(aspect='equal',xlabel='Assembly Y south (mm)',ylabel='Provisional Z (mm)',title=f"B0 {name.upper()} | exact OCCT section at X{s['x_mm']:.6f}\n{desc}")
 ax.legend(fontsize=7,loc='upper right');ax.grid(alpha=.2)
 fig.text(.5,.02,'STUDY ONLY — all Z provisional on Junana q=1.50; no Phase B or production CAD',ha='center',fontsize=9)
 fig.tight_layout(rect=(0,.04,1,1));fig.savefig(HERE/f'b0/section-{name}-b0.png',dpi=180);plt.close(fig)
