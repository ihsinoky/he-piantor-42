"""B2 engineering section and plan; no generative images."""
import os,json,math
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]/'.issue248-runtime';O=H/'b2'
os.environ.update(TMPDIR=str(R),MPLCONFIGDIR=str(R/'mpl'),XDG_CACHE_HOME=str(R/'cache'),MPLBACKEND='Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon
D=json.loads((O/'clearances-b2.json').read_text());P=json.loads((O/'plot-b2.json').read_text())
fig,axs=plt.subplots(1,2,figsize=(14,6),gridspec_kw={'width_ratios':[1.1,1]})
a=axs[0]
a.add_patch(Rectangle((-4,0),20,2,color='#9e835f',alpha=.6,label='Retained floor 2.00'))
a.add_patch(Rectangle((-4,6.7),20,1.2,color='#256c62',alpha=.7,label='Wing PCB 1.20'))
a.add_patch(Rectangle((-1.6,5.05),4.83,1.65,color='#2765a5',alpha=.7,label='Mated 1.65 reference bound'))
a.add_patch(Rectangle((3.23,5.05),6.5820508076,1.65,fill=False,edgecolor='#a45075',lw=2,label='Exit + first XY bend, full Z band'))
a.add_patch(Rectangle((-1.6,4.55),11.4120508076,.5,fill=False,hatch='///',edgecolor='#bb5a28',label='Retained 0.50 assembly allowance'))
a.add_patch(Rectangle((-1.6,4.05),11.4120508076,.5,fill=False,edgecolor='#555555',ls=':',label='Retained 0.50 required free gap'))
a.annotate('',xy=(11,2),xytext=(11,4.55),arrowprops=dict(arrowstyle='<->'))
a.text(11.4,3.25,'2.55 mm\nresidual floor gap',fontsize=9)
a.text(-3.8,8.35,'B = 6.70; PCB top = 7.90\nPlate top = 12.90 (stack +6.20)',fontsize=11)
a.text(-3.8,2.35,'Hall bottom Z3.30; floor gap 1.30\nTie tip Z1.20: screw/root constraint binds',fontsize=9)
a.set(xlim=(-4,16),ylim=(-.4,9.5),aspect='equal',xlabel='Local exit direction v (mm)',ylabel='Provisional assembly Z (mm)',title='Wing underside projected envelope section')
a.legend(loc='lower right',fontsize=7);a.grid(alpha=.15)
a=axs[1]
for idx,color in [('A','#2765a5'),('B','#a45075')]:
 q=P['wing']['left'][idx]
 # Show in assembly XY to make pose auditable.
 a.add_patch(Polygon(q['dress'],closed=True,facecolor=color,alpha=.18,edgecolor=color,label=idx+' first bend bound'))
 a.add_patch(Polygon(q['body'],closed=True,fill=False,edgecolor=color,lw=2,label=idx+' mated bound'))
outline=P['wing']['left']['outline'];a.plot(*zip(*outline),color='#256c62',lw=1,label='Rev4 board edge')
centers=[D['wing']['left'][i]['pose'] for i in ['A','B']];cx=sum(p['x'] for p in centers)/2;cy=sum(p['y'] for p in centers)/2
# Reference centreline arcs; dimensioned shape remains a rectangular conservative bound.
for p,sign in zip(centers,[-1,1]):
 for i in range(7):
  pts=[((i-3)*1.2,3.23),((i-3)*1.2,5.23)]
  pts += [((i-3)*1.2+sign*5*(1-math.cos(math.radians(t))),5.23+5*math.sin(math.radians(t))) for t in range(1,31)]
  x,y=pts[-1];pts.append((x+sign, y+math.sqrt(3)))
  pts=[(p['x']+u*p['u'][0]+v*p['v'][0],p['y']+u*p['u'][1]+v*p['v'][1]) for u,v in pts]
  a.plot(*zip(*pts),lw=.7,color='#444444')
a.set(xlim=(cx-19,cx+19),ylim=(cy-17,cy+12),aspect='equal',xlabel='Assembly X (mm)',ylabel='Assembly Y south (mm)',title='Left Wing J_WING zone: proposed pair')
a.invert_yaxis();a.legend(fontsize=7,loc='lower right');a.grid(alpha=.15)
fig.suptitle('B2 Pico-EZmate 7+7 feasibility | 10.2 x 4.83 x 1.65 mm mated bounds',fontsize=13)
fig.text(.5,.015,'Molex 781710001-SD sh2: horizontal wire exit, vertical mating. Dress: engineering assumption R5 / 30deg / 2mm straights. All roof Z provisional q=1.50.',ha='center',fontsize=8)
fig.tight_layout(rect=(0,.10,1,.93));fig.savefig(O/'wing-underside-fit-b2.png',dpi=180)
# Both Main pairs in native assembly XY, explicitly no routing qualification.
f,ax=plt.subplots(figsize=(9,9));outline=P['boards']['main'];ax.plot(*zip(*(outline+[outline[0]])),color='#256c62',label='Main board outline')
for ref,q in P['main'].items():
 ax.add_patch(Polygon(q['dress'],closed=True,facecolor='#2765a5',alpha=.16,edgecolor='#2765a5'))
 ax.add_patch(Polygon(q['body'],closed=True,fill=False,edgecolor='#a45075'))
 p=D['main'][ref]['pose'];ax.text(p['x'],p['y'],ref,fontsize=9)
ax.set(aspect='equal',xlabel='Assembly X mm',ylabel='Assembly Y south mm',title='Main J2/J3 zone envelope placement; copper not changed');ax.invert_yaxis();ax.grid(alpha=.2);ax.legend();f.tight_layout();f.savefig(O/'main-placement-b2.png',dpi=160)
