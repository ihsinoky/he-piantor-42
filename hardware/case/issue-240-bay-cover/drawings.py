"""Render measured study data. Run with system Python + matplotlib."""
import os,json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle,Circle
HERE=Path(__file__).resolve().parent

def save(fig,name):
 for ext in ['svg','png']:fig.savefig(HERE/f'{name}.{ext}',dpi=180,bbox_inches='tight')
 plt.close(fig)
def main():
 ds=[json.loads((HERE/f'{p}mm/measurements.json').read_text()) for p in [16,17]]
 fig,axs=plt.subplots(1,2,figsize=(12,10))
 for ax,d in zip(axs,ds):
  poly=d['cover_outline']['coordinates'][0];ax.add_patch(Polygon(poly,facecolor='#eeeeee',edgecolor='#444444',lw=1))
  mainxy=json.loads((HERE.parent/f'issue-228-final/{d["pitch_mm"]}mm/dimensions.json').read_text())['boards']['main']
  ax.add_patch(Polygon(mainxy,facecolor='#ead6ad',edgecolor='#a77',alpha=.5))
  ax.add_patch(Circle((-5,-8),2,facecolor='#b11',edgecolor='#b11',alpha=.8));ax.annotate('binding screw',(-5,-8),(-39,-4),fontsize=7,arrowprops=dict(arrowstyle='->',lw=.6))
  for gh in d['gh_placement']:
   a=math.radians(gh['orientation_deg']);x,y=gh['origin_mm'];xy=[(x+u*math.cos(a)+v*math.sin(a),y-u*math.sin(a)+v*math.cos(a)) for u,v in [(-10.375,-1.6),(10.375,-1.6),(10.375,5.55),(-10.375,5.55)]]
   ax.add_patch(Polygon(xy,facecolor='#e99',edgecolor='#a33',alpha=.7))
  ps=d['fly']['path_samples_mm'];ax.plot([p[0] for p in ps],[p[1] for p in ps],color='#1675b8',lw=2,label='Fly: connected 170 mm')
  for i,w in enumerate(d['wings']):
   for key in ['lower_waypoints_mm','upper_waypoints_mm']:
    ps=w[key];ax.plot([p[0] for p in ps],[p[1] for p in ps],color='#248a46',lw=2,ls='--',label='Wing: 160 mm waypoints' if i==0 and key.startswith('lower') else None)
  ax.set(xlim=(-44,44),ylim=(-57,72),aspect='equal',title=f'{d["pitch_mm"]} mm — {d["unexpected_interferences"]} observed contacts (lower bound)',xlabel='X / mm',ylabel='Y / mm');ax.invert_yaxis();ax.grid(alpha=.25);ax.legend(fontsize=8)
 fig.suptitle('Issue 240: evaluated closed-top assembly — rejected routing is shown explicitly')
 save(fig,'top-view')
 fig,ax=plt.subplots(figsize=(10,4))
 ax.add_patch(Rectangle((-3,10),13,1.2,facecolor='#d4b578'))
 ax.add_patch(Rectangle((-1.6,11.2),7.15,4.35,facecolor='#e5aaaa',edgecolor='#993333'))
 ax.add_patch(Rectangle((-3,14.7),1,1.5,facecolor='#aaa'))
 ax.add_patch(Rectangle((-2,15.95),8.5,.25,facecolor='#aaa'))
 ax.add_patch(Rectangle((6.5,14.7),3.5,1.5,facecolor='#aaa'))
 ax.plot([-1.6,5.55],[15.75,15.75],ls='--',color='#933',label='4.35 ref +0.20 mounting allowance')
 ax.plot([5.55,9],[12.8,12.8],color='#287',lw=2,label='Horizontal exit axis: Z12.80 planning datum')
 for z,lab in [(16.2,'top16.20'),(15.95,'pocket ceiling15.95 / skin0.25'),(14.7,'uniform underside14.70'),(11.2,'Main top11.20')]:ax.axhline(z,color='k',alpha=.2);ax.text(10.2,z,lab,va='center',fontsize=8)
 ax.set(xlim=(-3,15),ylim=(9.6,17),xlabel='Connector local normal / mm',ylabel='Assembly Z / mm',title='GH section: 0.85 mm nominal clash; 1.25 mm pocket includes allowances')
 ax.legend(fontsize=8,loc='lower right');save(fig,'section-gh')
 fig,ax=plt.subplots(figsize=(12,4))
 data=json.loads((HERE.parent/'issue-238-bay-study/section-x0.json').read_text())
 for r in data:
  if r['part']=='cable-rack':continue
  p=r['yz_mm'];ax.plot([v[0] for v in p],[v[1] for v in p],color='#777',lw=.6)
 for d in ds[-1:]:
  p=d['fly']['path_samples_mm'];ax.plot([v[1] for v in p],[v[2] for v in p],color='#1675b8',lw=1,label='Fly YZ projection (not an X=0 section)')
 ax.axhline(16.2,color='black',label='Cover top16.20');ax.axhline(14.7,color='#999',ls='--',label='Uniform underside14.70');ax.axhline(15.8,color='#168',ls=':',label='Fly pocket ceiling15.80 / skin0.40')
 ax.set(xlim=(-58,72),ylim=(-4,18),xlabel='Y / mm',ylabel='Z / mm',title='Retained X=0 BRep section, rack removed; proposed Fly projection');ax.legend(fontsize=7);ax.grid(alpha=.2);save(fig,'section-bay')
if __name__=='__main__':main()
