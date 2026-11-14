"""A2 alignment envelopes only. No CAD; leaves every Phase A artifact untouched."""
import os, sys, json, csv, math, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
RUN=ROOT/'.issue248-runtime'
for k,v in {'MPLCONFIGDIR':RUN/'mpl','TMPDIR':RUN,'XDG_CACHE_HOME':RUN/'cache','MPLBACKEND':'Agg'}.items(): os.environ[k]=str(v)
sys.path.insert(0,str(RUN/'pydeps'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch, Rectangle, Patch as LegendPatch
from shapely.geometry import Polygon, box, Point, LineString, mapping, shape
from shapely.affinity import affine_transform, rotate, translate
from shapely.ops import unary_union
base=ROOT/'hardware/case/issue-232-final/17mm'
adopted=ROOT/'hardware/case/issue-246-delta6-tuning/packed/delta-6/17mm'
d=json.loads((base/'dimensions.json').read_text()); m=json.loads((adopted/'measurements.json').read_text())
idx=json.loads((adopted/'assembly-index.json').read_text())
PLATE=13.55; TOP=24.65; SKIN=2.; GAP=.30
keys=[]; decks=[]; strips=[]; margins=[]; start_masks=[]; toe_masks=[]; edge_lines=[]
def xf(g,t):
 a=t['matrix'];return affine_transform(g,[a[0][0],a[0][1],a[1][0],a[1][1],*t['translation']])
def draw(ax,g,**kw):
 if g.is_empty:return
 if g.geom_type=='Polygon':
  ax.add_patch(Patch(list(g.exterior.coords),**kw))
  for ring in g.interiors:ax.add_patch(Patch(list(ring.coords),fc='white',ec='none'))
 elif hasattr(g,'geoms'):
  for p in g.geoms:draw(ax,p,**kw)
def lines(ax,g,**kw):
 if g.is_empty:return
 if hasattr(g,'geoms'):
  for p in g.geoms:lines(ax,p,**kw)
 else:
  x,y=g.xy; ax.plot(x,y,**kw)
# Row edges are pitch-cell edges, +/-8.5; cap edge alternative is documented.
for side in ['left','right']:
 t=d['wing_transforms'][side];half=box(-300,-300,0,300) if side=='left' else box(0,-300,300,300)
 deck=Polygon(next(p['deck_outline_xy_mm'] for p in d['plates'] if p['side']==side));decks.append(deck)
 rows=list(csv.DictReader((base/f'plate-package/apertures-{side}-local.csv').open()))
 def rowline(row,offset):
  r=sorted([r for r in rows if f'_R{row}_' in r['key']],key=lambda r:float(r['x_mm']))
  points=[(float(k['x_mm']),float(k['y_mm'])+offset) for k in r]
  return [(-300,points[0][1]),*points,(300,points[-1][1])]
 def northmask(points):return xf(Polygon([*points,(300,300),(-300,300)]),t).intersection(half)
 s=rowline(1,8.5);e=rowline(2,-8.5)
 start_masks.append(northmask(s));toe_masks.append(northmask(e))
 edge_lines.append((xf(LineString(s),t).intersection(half),xf(LineString(e),t).intersection(half)))
 strips.append(deck.intersection(northmask(rowline(0,9))))
 inner=box(24.055555556,-300,300,300) if side=='left' else box(-300,-300,-24.055555556,300)
 margins.append(deck.intersection(xf(inner,t)))
 for r in rows:
  x,y,a=map(float,[r['x_mm'],r['y_mm'],r['rotation_ccw_deg']])
  keys.append({'key':r['key'],'cap':xf(translate(rotate(box(-8,-8,8,8),a),x,y),t),'well':xf(translate(rotate(box(-9,-9,9,9),a),x,y),t)})
wells=unary_union([k['well'] for k in keys]);foot=shape(m['cover_outline']).union(box(-10,-18,10,18)).union(unary_union(margins))
start=unary_union(start_masks);toe=unary_union(toe_masks)
plateau=foot.intersection(start).difference(wells)
slope=foot.intersection(toe).difference(start).difference(wells)
low=foot.difference(toe).difference(wells)
strips=[s.difference(wells) for s in strips]
raised=unary_union([plateau,slope,*strips])
# In the central margin only the inward extension of C5 applies. Edges meet at X0.
a=math.sqrt(3)/2; tx=81.24620297879808; ty=12.790500673763258
START=ty+tx/math.sqrt(3)-27.5/a
TOE=ty+tx/math.sqrt(3)-(-6.5)/a
RUNY=TOE-START
# X0 cut run is longer than Wing-local normal run; surface inclination is 18.08 deg.
def edge_y(x):return START-abs(x)/math.sqrt(3),TOE-abs(x)/math.sqrt(3)
def roof(x,y):
 s,e=edge_y(x);return TOP-(TOP-PLATE)*min(1,max(0,(y-s)/(e-s)))
# Conservative complete assembly AABBs projected against the actual A2 height field.
checks=[]
for p in idx:
 if p['name'].startswith('Main-GH-') or p['name'] in ['screw-main-H2','screw-main-H3','cover-screw-2','cover-screw-3','cover-Main-spacer-2','cover-Main-spacer-3']:
  lo,hi=p['bounds'];x=lo[0] if abs(lo[0])>abs(hi[0]) else hi[0];y=hi[1];z=hi[2]-8.65
  checks.append({'name':p['name'],'xy_bounds':[lo[:2],hi[:2]],'obstacle_top_z':z,'limiting_xy':[x,y],'roof_z':roof(x,y),'underside_z':roof(x,y)-SKIN,'raw_gap':roof(x,y)-SKIN-z,'required_gap':GAP,'pocket_ceiling_z':z+GAP,'pocket_depth_required':max(0,z+GAP-(roof(x,y)-SKIN)),'remaining_skin':roof(x,y)-(z+GAP)})
# South screw solids may use shared names in baseline; preserve explicit washer/head extents.
if not any('screw-main' in p['name'] for p in checks):
 for x in [-31.89268220121,31.892682201217]:
  z=10.65;y=66.10 # head radius 1.70 about Y64.4
  checks.append({'name':'reference-only-restored-Main-screw-'+str(round(x,2)),'xy_bounds':[[x-1.7,62.7],[x+1.7,66.1]],'obstacle_top_z':z,'limiting_xy':[x,y],'roof_z':roof(x,y),'underside_z':roof(x,y)-2,'raw_gap':roof(x,y)-2-z,'required_gap':GAP})
# Saved paths are pre-Delta; +6 then -8.65 = -2.65. Radius 1, conservative vertical roof screen.
fly=[]
for x,y,z in m['fly']['path_samples_mm']:
 z=z-2.65
 # Account for lowest roof over the entire radius-one XY disk by Lipschitz bound;
 # conservative square corners also cover the disk, including centre ridge.
 rmin=min(roof(xx,yy) for xx in [x-1,x+1] for yy in [y-1,y+1])
 fly.append({'x':x,'y':y,'axis_z':z,'gap':rmin-2-(z+1)})
fmin=min(fly,key=lambda p:p['gap'])
assert len(keys)==42
assert all(k['cap'].distance(raised)>=.999999 for k in keys)
assert abs(RUNY*a-34)<1e-8
assert slope.intersection(decks[0]).area>0 and slope.intersection(decks[1]).area>0
assert slope.intersection(box(-5,35,5,45)).area>0
assert not slope.intersection(wells).area>1e-7
regions={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'name':n,'status':'A2 2D only; provisional q=1.50'},'geometry':mapping(g)} for n,g in [('plateau',plateau),('slope',slope),('low_south',low),('north_left',strips[0]),('north_right',strips[1])]]}
(HERE/'raised-regions-a2.geojson').write_text(json.dumps(regions,indent=2)+'\n')
T={'status':'A2 2D alignment only; all Z provisional, unmeasured Junana q=1.50','units':'mm, assembly Y south, Z up; Wing-local Y north','plate_top':PLATE,'plateau_top':TOP,'roof_skin_vertical':SKIN,'required_gap':GAP,'normal_run':34,'normal_angle_deg':math.degrees(math.atan(11.1/34)),'center_start_y':START,'center_toe_y':TOE,'center_run_y':RUNY,'center_section_angle_deg':math.degrees(math.atan(11.1/RUNY)),'central_edge_formula':'Y_start=27.9425559397-|X|/sqrt(3); Y_toe=67.2023742446-|X|/sqrt(3); use computed values above','main_checks':checks,'fly':{'length':m['fly']['connected_length_mm'],'raw_sample_translation_z':-2.65,'assembly_translation_z':-8.65,'radius':1,'minimum_conservative_vertical_gap':fmin,'min_gap':fmin['gap'],'pocket_depth_for_030_gap':-fmin['gap']+.3,'remaining_skin_at_low_toe':13.55-(12.95+.3),'verdict':'FAIL unchanged route under nominal 2 mm roof; redress required; no reroute performed'},'cap_well_screen':{'count':42,'cap_square':16,'well_square':18,'nominal_gap_min':min(k['cap'].distance(raised) for k in keys),'budgeted_residual':.5,'required':.3},'interpretations':['pitch-cell edges +/-8.5, not measured cap rim','staggered row polyline extended from C5 through centre bay, mirrored join at X0','inner Wing margin starts 9 mm outward of C5 centres; wells remove all keys','nominal skin is 2 mm vertical; no thin-skin structural acceptance']}
# Use exact computed edge equations in the saved table.
T['central_edge_formula']=f'Y_start={START:.12f}-abs(X)/sqrt(3); Y_toe={TOE:.12f}-abs(X)/sqrt(3)'
(HERE/'tables-a2.json').write_text(json.dumps(T,indent=2)+'\n')

def save(fig,name):
 fig.tight_layout(rect=(0,0,1,.955))
 for ext in ['png','svg']:
  target=HERE/f'{name}.{ext}';fig.savefig(target,dpi=180)
  if ext=='svg':target.write_text('\n'.join(line.rstrip() for line in target.read_text().splitlines())+'\n')
 plt.close(fig)
colors={'plateau':'#8ebed0','slope':'#e9ad61','strip':'#92bda0','low':'#eee9df'}
fig,axs=plt.subplots(1,2,figsize=(16,9),gridspec_kw={'width_ratios':[1.45,1]})
for ax in axs:
 for deck in decks:draw(ax,deck,fc=colors['low'],ec='#999',lw=.6)
 draw(ax,low,fc=colors['low'],ec='#999',lw=.5)
 for g,c in [(plateau,'plateau'),(slope,'slope'),*[(s,'strip') for s in strips]]:draw(ax,g,fc=colors[c],ec='#555',lw=.5)
 for k in keys:
  draw(ax,k['well'],fc='none',ec='#ba7979',lw=.65,ls=':');draw(ax,k['cap'],fc='white',ec='#666',lw=.5)
  if ax==axs[0] and ('_R1_' in k['key'] or '_R2_' in k['key']):
   p=k['cap'].centroid;ax.text(p.x,p.y,'R2' if '_R1_' in k['key'] else 'R3',fontsize=5,ha='center',va='center')
 for s,e in edge_lines:
  lines(ax,s.intersection(foot),color='#a02060',lw=1.6,ls='--')
  lines(ax,e.intersection(foot),color='#394fb2',lw=1.6,ls='--')
 ax.plot([0,0],[-56,75],'k-.',lw=.8)
 # Main obstacle XY reservation boxes, overlaid without altering the drawn external surface.
 for p in checks:
  if 'GH' in p['name']:
   lo,hi=p['xy_bounds'];ax.add_patch(Rectangle(lo,hi[0]-lo[0],hi[1]-lo[1],fill=False,ec='#b32626',lw=1,ls=':'))
 ax.set(aspect='equal',xlabel='Assembly X (mm)',ylabel='Assembly Y south (mm)');ax.grid(alpha=.12)
axs[0].set(xlim=(-153,153),ylim=(87,-72),title='Whole plan | retained aluminium plates / 42 wells')
axs[1].set(xlim=(-62,62),ylim=(83,-58),title='Central margin detail | spans bay AND Wing inner areas')
ax=axs[1]
ax.annotate(f'Start: row-2 TOP pitch edge\nX0: Y{START:.2f}',xy=(0,START),xytext=(-59,9),fontsize=8,color='#a02060',arrowprops={'arrowstyle':'->','color':'#a02060'})
ax.annotate(f'Toe: row-3 BOTTOM pitch edge\nX0: Y{TOE:.2f}',xy=(0,TOE),xytext=(-58,78),fontsize=8,color='#394fb2',arrowprops={'arrowstyle':'->','color':'#394fb2'})
# B-B: left local X45, local Y -12..33, stays in the keyless inner margin.
t=d['wing_transforms']['left'];bb=xf(LineString([(45,33),(45,-12)]),t);lines(ax,bb,color='k',ls='-.',lw=1);p=bb.centroid;ax.text(p.x-5,p.y,'B-B',fontsize=8)
ax.text(2,-51,'A-A X0',fontsize=8)
axs[0].legend(handles=[LegendPatch(fc=colors['plateau'],label='Plateau: provisional Z24.65'),LegendPatch(fc=colors['slope'],label='Slope: row-2 top to row-3 bottom'),LegendPatch(fc=colors['strip'],label='North strips: provisional Z24.65'),LegendPatch(fc=colors['low'],label='Low deck / south of toe: provisional Z13.55'),LegendPatch(fc='white',ec='#ba7979',label='18 mm wells / assumed 16 mm swept caps')],loc='lower left',fontsize=8)
fig.suptitle('Issue 248 A2 — 2D alignment only | all Z provisional: unmeasured Junana q=1.50\n34 mm normal run / 11.10 drop / 18.08° surface; mirrored row-edge extensions meet at X0',fontsize=12)
save(fig,'plan-a2')
fig,axs=plt.subplots(5,1,figsize=(14,19))
yy=np.linspace(-56,74,650)
ax=axs[0];rr=np.array([roof(0,y) for y in yy]);ax.fill_between(yy,rr-2,rr,color=colors['slope'],label='Nominal 2 mm vertical roof')
ax.add_patch(Rectangle((-56,0),130,2,fc='#aaa'));ax.add_patch(Rectangle((2.267949,7.35),65.632051,1.2,fc='#8ebed0',label='Main Rev.7 PCB, actual X0 section'))
ax.plot([9.267949]*2,[8.55,10.65],color='k',lw=3)
for y,name in [(START,'start'),(TOE,'toe')]:ax.axvline(y,color='#777',ls=':',lw=.8);ax.text(y+.6,25.6,f'{name} Y{y:.2f}',fontsize=8)
ax.text(-52,17,f'Plateau Z24.65 → low Z13.55\nX0 run {RUNY:.2f}; apparent section angle {T["center_section_angle_deg"]:.2f}°\nSurface normal angle 18.08°',fontsize=9)
ax.set(title='A-A | centre X0: new short slope; no off-axis GH assumed on this cut',xlim=(-58,76),ylim=(-1,29))
ax=axs[1];ss=np.linspace(-5,42,200);rr=TOP-11.1*np.clip(ss/34,0,1)
ax.fill_between(ss,np.maximum(rr-2,PLATE),rr,color=colors['slope'],label='Raise over Wing inner margin (no key at local X45)')
ax.add_patch(Rectangle((-5,12.05),47,1.5,fc='#bbb',label='Fixed D-038 aluminium, nominal 1.50'))
ax.add_patch(Rectangle((-5,7.35),47,1.2,fc='#8ebed0',label='Wing Rev.4 PCB'))
ax.annotate('',xy=(0,27),xytext=(34,27),arrowprops={'arrowstyle':'<->'});ax.text(17,27.5,'34.00 mm normal run / 18.08°',ha='center',fontsize=9)
ax.text(0,16,'Row-2 top\nlocal Y27.50',fontsize=8);ax.text(34,16,'Row-3 bottom\nlocal Y−6.50',fontsize=8,ha='center')
ax.text(5,3,'B-B left local X45; axis south s=27.5−local Y.\nLast 6.13 mm: underside meets plate, wedge tapers to zero; edge unqualified.',fontsize=9)
ax.set(title='B-B | slope over a Wing inner margin; section normal to row edges',xlim=(-5,43),ylim=(0,30))
ax=axs[2];gh=checks[0];x=abs(gh['limiting_xy'][0]);yy=np.linspace(20,72,350);rr=np.array([roof(x,y) for y in yy]);ax.plot(yy,rr,color='#805022',lw=2,label=f'Roof top at |X|={x:.3f} (GH limiting projection)');ax.plot(yy,rr-2,color='#805022',ls='--',label='Nominal 2 mm underside')
lo,hi=gh['xy_bounds'];ax.add_patch(Rectangle((lo[1],8.55),hi[1]-lo[1],4.55,fc='#8ebed0',label='GH AABB projection Z13.10; both sides mirrored'))
ax.plot([lo[1]-.3,hi[1]+.3],[13.4]*2,color='#b32626',lw=2,label='Pocket ceiling Z13.40 = GH top +0.30')
ax.plot([62.7,66.1],[10.65]*2,'k-',lw=3,label='Restored bare Main screw REFERENCE Z10.65; not adopted cover hardware')
ax.plot([62.4,66.4],[13.55]*2,color='#b32626',lw=3,label='Actual adopted cover screw head Z13.55: needs access opening')
ax.plot([62.15,66.65],[12.05]*2,color='#a46290',lw=3,label='Actual adopted south spacer Z12.05: conflicts by 0.50')
pocket_y=np.linspace(lo[1]-.3,hi[1]+.3,200);pocket_under=np.array([roof(x,y)-2 for y in pocket_y])
ax.fill_between(pocket_y,pocket_under,13.4,where=pocket_under<13.4,interpolate=True,facecolor='none',edgecolor='#b32626',hatch='////',lw=.5)
ax.plot([61,70],[11.55]*2,color='#777',ls=':',label='South low underside Z11.55; bare screw reference gap 0.90')
ax.text(21,22,'GH pocket: XY box +0.30 per side; 17.167 ×22.145 each\nDepth max 1.85; skin only 0.15 at projected south corner: NOT accepted\n2 mm closed roof needs local top Z15.40 (+1.85 over low surface)',fontsize=9)
ax.annotate('GH raw gap −1.55\nRequired +0.30',xy=(hi[1],11.55),xytext=(54,17),fontsize=9,arrowprops={'arrowstyle':'->'})
ax.set(title='C | off-axis Main obstacle projections: pocket concept exposes insufficient closed-roof thickness',xlim=(20,73),ylim=(7.5,27))
ax=axs[3];yy=np.linspace(8,72,350);rr=np.array([roof(-14.6,y) for y in yy]);ax.plot(yy,rr,color='#805022',lw=2,label='Roof top at X−14.6');ax.plot(yy,rr-2,color='#805022',ls='--',label='Nominal underside')
ax.fill_between([25,61.120415],[10.95]*2,[12.95]*2,color='#a7a0ce',label='Fly south storage projection: OD2, axis Z11.95')
ax.plot([50,63],[13.25]*2,color='#b32626',label='Cable pocket ceiling Z13.25 for +0.30 gap')
ax.text(9,22,'Existing 170 mm route: minimum conservative roof gap −1.40\nPocket depth 1.70 → remaining skin 0.30: NOT accepted\nRedress south loop northward; keep 170 mm / R≥5 / service & USB gates.',fontsize=9,bbox={'facecolor':'white','alpha':.9,'edgecolor':'none'})
ax.set(title='D | Fly cable projection: translated baseline route FAILS nominal roof; no new route certified',xlim=(8,73),ylim=(8,27))
ax=axs[4]
# South hardware concept, transverse section at Y64.4, coordinates relative to H2/H3.
for l,r in [(-7,-2.55),(2.55,7)]:ax.add_patch(Rectangle((l,11.55),r-l,2,fc=colors['slope']))
for l,r in [(-2.55,-2.30),(2.30,2.55)]:ax.add_patch(Rectangle((l,12.35),r-l,1.2,fc=colors['slope']))
ax.add_patch(Rectangle((-2.25,9.05),4.5,3,fc='#a46290',label='Unchanged POM spacer: Ø4.50 ×3.00; top Z12.05'))
ax.add_patch(Rectangle((-4,8.55),8,.5,fc='#aaa',label='Main washer top Z9.05'))
ax.add_patch(Rectangle((-7,7.35),14,1.2,fc='#8ebed0',label='Main PCB (not changed)'))
ax.add_patch(Patch([(-.8,12.55),(.8,12.55),(2,13.55),(-2,13.55)],fc='#555',label='Existing Ø4 head flush Z13.55; seating must be redesigned'))
ax.plot([-.8,-.8],[5,12.55],'k-',lw=2);ax.plot([.8,.8],[5,12.55],'k-',lw=2)
ax.annotate('',xy=(-2.3,15.4),xytext=(2.3,15.4),arrowprops={'arrowstyle':'<->'});ax.text(0,15.7,'Ø4.60 head/access opening (0.30 radial)',ha='center',fontsize=8)
ax.annotate('Ø5.10 pocket / ceiling Z12.35\n0.80 removal; 1.20 residual skin',xy=(2.5,12.35),xytext=(3,18),fontsize=8,arrowprops={'arrowstyle':'->'})
ax.text(-6.8,20.1,'Y64.40, X±31.892683: dimensioned escape concept only.\nOpen head clearance removes bearing seat: fastener retention NOT resolved.\nShorter spacer alternative 2.20 mm clears nominal roof, but removes its support.',fontsize=8)
ax.set(title='E | actual adopted south fasteners: openings/pocket concept; no retention approval',xlim=(-7.5,10),ylim=(4,23))
for i,ax in enumerate(axs):
 ax.set(xlabel='Southward normal distance s (mm)' if i==1 else ('Distance from south screw axis X (mm)' if i==4 else 'Assembly Y south (mm)'),ylabel='Provisional Z (mm)');ax.grid(alpha=.15);ax.legend(fontsize=6.4,loc='lower left' if i>=2 else 'upper right')
fig.suptitle('Issue 248 A2 — sections / obstacle concepts only; no production CAD\nALL Z provisional under unmeasured Junana q=1.50; 0.30 clearance retained; pockets are not structural approvals',fontsize=12)
save(fig,'sections-a2')
print(json.dumps({'start':START,'toe':TOE,'main':checks,'fly_min':fmin,'cap_gap':T['cap_well_screen']},indent=2))
