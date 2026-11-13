"""Dimensioned drawings from delivered measurement data; all scratch in runtime."""
import json,os,math
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.issue242-runtime/mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle,Circle

def save(fig,name):
 for ext in ('svg','png'):fig.savefig(HERE/f'{name}.{ext}',dpi=190,bbox_inches='tight')
 plt.close(fig)
def main():
 ds=[json.loads((HERE/f'{p}mm/measurements.json').read_text()) for p in (16,17)]
 fig,axes=plt.subplots(1,2,figsize=(12,10))
 for ax,d in zip(axes,ds):
  ax.add_patch(Polygon(d['cover_outline']['coordinates'][0],fc='#ededed',ec='#555'))
  b=json.loads((HERE.parent/f'issue-228-final/{d["pitch_mm"]}mm/dimensions.json').read_text())['boards']
  for k in ('main','wing_left','wing_right'):
   ax.add_patch(Polygon(b[k],fc='#bfcc8d' if k=='main' else '#dabda0',ec='#886644',alpha=.45))
  for i,w in enumerate(d['wings']):
   ps=w['lower_waypoints_mm'];ax.plot([p[0] for p in ps],[p[1] for p in ps],lw=3,c='#298c45',label='Dedicated lower U / OD5, Z5' if i==0 else None)
   for row in w['upper_samples_mm']:ax.plot([p[0] for p in row],[p[1] for p in row],lw=.5,c='#b64e21')
   x=(-1 if i==0 else 1)*15
   ax.annotate('16 mm leg change\n= 32 mm extra cable',(x,38),(x-15 if i==0 else x+3,46),fontsize=7,arrowprops=dict(arrowstyle='->'))
  ps=d['fly']['path_samples_mm'];ax.plot([p[0] for p in ps],[p[1] for p in ps],lw=1.8,c='#167abd',label='One connected Fly / 170 mm')
  for x,y in d['retention_sites_mm']:ax.add_patch(Circle((x,y),4,fc='none',ec='#703d93',lw=1.5));ax.plot(x,y,'+',c='#703d93')
  for r in d['splice_relocations']:
   x,y=r['old_xy'];ax.plot(x,y,'rx',ms=6)
   x,y=r['new_xy'];ax.add_patch(Circle((x,y),3.5,fc='none',ec='red',lw=1));ax.plot(x,y,'r.',ms=4)
  ax.set(xlim=(-44,44),ylim=(-57,73),aspect='equal',title=f'{d["pitch_mm"]} mm pitch — STUDY, see full audit',xlabel='X / mm',ylabel='Y / mm');ax.invert_yaxis();ax.grid(alpha=.2);ax.legend(fontsize=7,loc='upper right')
 fig.suptitle('Issue 242 | flush Z16.20 lid | new case channels and under-Main service U\nPurple: north pillars / south Main spacers; red: moved splice sites; orange: fourteen rising conductors')
 save(fig,'top-view')
 fig,axes=plt.subplots(1,2,figsize=(13,5))
 ax=axes[0]
 ax.add_patch(Rectangle((-3,10),13,1.2,fc='#a2b473'))
 ax.add_patch(Rectangle((-1.6,11.2),7.15,4.55,fc='#d9ad9f',ec='#884a35'))
 ax.add_patch(Rectangle((-1.9,15.95),7.75,.25,fc='#999'))
 ax.add_patch(Rectangle((-3,14.7),1.1,1.5,fc='#999'));ax.add_patch(Rectangle((5.85,14.7),4.15,1.5,fc='#999'))
 for z,label in [(16.2,'Flush top Z16.20'),(15.95,'GH pocket ceiling Z15.95 / skin 0.25'),(15.75,'GH ref + mounting allowance Z15.75'),(14.7,'Nominal underside Z14.70'),(11.2,'Fixed Main top Z11.20')]:ax.axhline(z,c='#777',lw=.5,ls='--');ax.text(10.5,z,label,fontsize=7,va='center')
 ax.set(xlim=(-3,24),ylim=(9.5,17.2),xlabel='GH local normal / mm',ylabel='Z / mm',title='A–A: underside-only pocket, aluminium candidate')
 ax=axes[1]
 ax.add_patch(Rectangle((-6,0),12,2,fc='#d7b892',ec='#846'))
 ax.add_patch(Rectangle((-4,2),8,12.7,fc='#d7b892',ec='#846'))
 ax.add_patch(Rectangle((-4.01,11.4),6.42,1.7,fc='white',ec='#846'))
 ax.add_patch(Rectangle((-2.31,11.5),4.62,1.6,fc='#a8a8a8',ec='#333'))
 ax.add_patch(Rectangle((-1.1,10),2.2,4.7,fc='white'))
 ax.add_patch(Rectangle((-5,14.7),10,1.5,fc='#bbb',ec='#666'))
 ax.add_patch(Rectangle((-.8,10.2),1.6,5,fc='#666'))
 ax.add_patch(Polygon([(-.8,15.2),(.8,15.2),(2,16.2),(-2,16.2)],fc='#666'))
 ax.annotate('M2 x 6 countersunk\n4 mm head flush',(0,15.8),(5,17),fontsize=8,arrowprops=dict(arrowstyle='->'))
 ax.annotate('M2 nut AF4 / t1.6\nside loading slot 4.2 x 1.7',(1.9,12.3),(5,11),fontsize=8,arrowprops=dict(arrowstyle='->'))
 ax.annotate('1.6 mm roof ligament\nno adhesive / no heat insert',(3.2,13.8),(5,6),fontsize=8,arrowprops=dict(arrowstyle='->'))
 ax.annotate('Integral OD8 pillar\nrooted in 2 mm floor',(3,5),(-9,4),fontsize=8,arrowprops=dict(arrowstyle='->'))
 ax.set(xlim=(-10,16),ylim=(-1,19),xlabel='Pillar local X / mm',ylabel='Z / mm',title='B–B: north captive nut / floor load path (south uses Main spacers)')
 save(fig,'sections')
 # Every conductor profile, projected in YZ, shows the fixed-board crossing.
 fig,ax=plt.subplots(figsize=(11,5))
 d=ds[-1];w=d['wings'][0]
 for r in w['upper_samples_mm']:ax.plot([p[1] for p in r],[p[2] for p in r],c='#b64e21',lw=1)
 ax.add_patch(Rectangle((6,10),40,1.2,fc='#dbc69b',alpha=.5,label='Wing PCB Z10–11.2 (projection only)'))
 ps=w['lower_waypoints_mm'];ax.plot([p[1] for p in ps],[p[2] for p in ps],c='#298c45',lw=4,label='Lower U centreline')
 ax.axhline(16.2,c='black',label='Flush cover top');ax.axhline(14.7,c='#777',ls='--',label='Nominal lid underside')
 ax.set(xlim=(-30,53),ylim=(0,18),xlabel='Y / mm',ylabel='Z / mm',title='C–C: route YZ projection — not a clearance certificate');ax.grid(alpha=.2);ax.legend(fontsize=8)
 save(fig,'route-projection')
 fig,axes=plt.subplots(2,2,figsize=(13,8))
 for j,pitch in enumerate((16,17)):
  contacts=json.loads((HERE/f'{pitch}mm/binding-sections.json').read_text())
  for i,r in enumerate(contacts):
   ax=axes[j,i]
   for name,curves in r['section_edges_XZ_mm'].items():
    for k,curve in enumerate(curves):ax.plot([p[0] for p in curve],[p[1] for p in curve],c='#276d36' if name=='Wing PCB' else '#c1481f',lw=1.6,label=name if k==0 else None)
   b=r['overlap_bounds_mm'];ax.add_patch(Rectangle((b[0][0],b[0][2]),b[1][0]-b[0][0],b[1][2]-b[0][2],fc='#dd5242',alpha=.2))
   x=r['section_center_X_mm'];ax.set(xlim=(x-5,x+5),ylim=(8.8,13.4),aspect='equal',xlabel='X / mm',ylabel='Z / mm',title=f"{pitch}mm {r['side']}: Y={r['section_Y_mm']:.3f}; overlap {r['overlap_mm3']:.6f} mm³")
   ax.grid(alpha=.2);ax.legend(fontsize=8)
 fig.suptitle('C–C: true constant-Y sections through measured cable / fixed Wing PCB penetration')
 save(fig,'section-routing')
if __name__=='__main__':main()
