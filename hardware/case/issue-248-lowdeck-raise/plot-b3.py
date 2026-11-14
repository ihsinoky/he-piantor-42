"""B3 engineering section PNGs; dimensions from computed envelopes."""
import os,json
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'b3';R=H.parents[2]/'.issue248-runtime'
os.environ.update(TMPDIR=str(R),MPLCONFIGDIR=str(R/'mpl'),XDG_CACHE_HOME=str(R/'cache'),MPLBACKEND='Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon
D=json.loads((O/'clearances-b3.json').read_text());P=json.loads((O/'plot-b3.json').read_text())
for key,d in D['families'].items():
 E=d['dimensions_mm']['height'];B=d['B_mm'];depth=d['dimensions_mm']['depth'];gap=d['main']['J2']['vertical_gap_mm']
 f,axs=plt.subplots(1,3,figsize=(17,6),gridspec_kw={'width_ratios':[1,1,1.2]})
 a=axs[0]
 for x,y,w,h,color,label in [(-4,0,17,2,'#9e835f','Floor 2.00'),(-4,B,17,1.2,'#256c62','Wing PCB 1.20'),(-depth/2,B-E,depth,E,'#2765a5',f'Seated {E:.2f}'),(depth/2,B-E,6.6,E,'#a45075','First XY dress, full Z band')]:a.add_patch(Rectangle((x,y),w,h,facecolor=color,alpha=.6,label=label))
 a.add_patch(Rectangle((-depth/2,B-E-.5),depth+6.6,.5,fill=False,hatch='///',edgecolor='#bb5a28',label='0.50 allowance'))
 a.annotate('',xy=(11.4,2),xytext=(11.4,B-E-.5),arrowprops=dict(arrowstyle='<->'))
 a.text(11.8,2.15,f'{B-E-.5-2:.2f}',rotation=90)
 a.text(-3.8,8.45,'B 6.70 | plate top Z12.90\nTie/root binds; Hall bound 5.90',fontsize=9)
 a.set(xlim=(-4,14),ylim=(-.2,9.5),aspect='equal',xlabel='Exit v (mm)',ylabel='Assembly Z (mm)',title='Wing underside section');a.legend(loc='lower right',fontsize=7);a.grid(alpha=.15)
 a=axs[1]
 a.add_patch(Rectangle((-3,6.7),12,1.2,color='#256c62',alpha=.6,label='Main PCB'))
 a.add_patch(Rectangle((-depth/2,7.9),depth,E,color='#2765a5',alpha=.6,label='Seated bound'))
 a.add_patch(Rectangle((depth/2,7.9),5,E,fill=False,edgecolor='#a45075',label='XY first dress'))
 a.add_patch(Rectangle((-4,11.55),14,2,color='#9e835f',alpha=.6,label='B0 low-south roof'))
 a.annotate('',xy=(7,7.9+E),xytext=(7,11.55),arrowprops=dict(arrowstyle='<->'))
 a.text(-3.8,14.1,f'B0 exact vertical gap: +{gap:.2f} mm\nAfter allowance: +{gap-.5:.2f} mm',fontsize=10)
 a.set(xlim=(-4,10),ylim=(6,15.2),aspect='equal',xlabel='Projected exit direction (mm)',title='Main worst roof support section');a.legend(fontsize=7,loc='lower right');a.grid(alpha=.15)
 a=axs[2];q=P[key]['wing']['left']
 for part,c,alpha in [('outline','#256c62',0),('body','#2765a5',.5),('dress','#a45075',.15)]:a.add_patch(Polygon(q[part],closed=True,facecolor=c if alpha else 'none',edgecolor=c,alpha=alpha if alpha else 1,label=part))
 a.set(xlim=(-45,-10),ylim=(-50,-23),aspect='equal',xlabel='Assembly X (mm)',ylabel='Assembly Y south (mm)',title='Left Wing local plan');a.invert_yaxis();a.legend(fontsize=8);a.grid(alpha=.15)
 f.suptitle(f'B3 {key.upper()} 14-way | occupied envelope screen | all roof Z provisional on q=1.50',fontsize=13)
 f.text(.5,.02,'Drawing reference seated dimensions + retained 0.50 allowance. First dress: 2 mm / R5 30deg XY / 2 mm (engineering assumptions). No complete harness or service-motion proof.',ha='center',fontsize=8)
 f.tight_layout(rect=(0,.06,1,.94));f.savefig(O/(key+'-sections-b3.png'),dpi=170);plt.close(f)
