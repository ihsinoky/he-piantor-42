"""A4 north-strip trim to approved straight start line. 2D only; keeps A–A3 unchanged."""
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
keys=[]; decks=[]; strips=[]; margins=[]
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
# Retain fixed decks, inner margins and all assumed caps / wells; trim strips below.
for side in ['left','right']:
 t=d['wing_transforms'][side];half=box(-300,-300,0,300) if side=='left' else box(0,-300,300,300)
 deck=Polygon(next(p['deck_outline_xy_mm'] for p in d['plates'] if p['side']==side));decks.append(deck)
 rows=list(csv.DictReader((base/f'plate-package/apertures-{side}-local.csv').open()))
 def rowline(row,offset):
  r=sorted([r for r in rows if f'_R{row}_' in r['key']],key=lambda r:float(r['x_mm']))
  points=[(float(k['x_mm']),float(k['y_mm'])+offset) for k in r]
  return [(-300,points[0][1]),*points,(300,points[-1][1])]
 def northmask(points):return xf(Polygon([*points,(300,300),(-300,300)]),t).intersection(half)
 strips.append(deck.intersection(northmask(rowline(0,9))))
 inner=box(24.055555556,-300,300,300) if side=='left' else box(-300,-300,-24.055555556,300)
 margins.append(deck.intersection(xf(inner,t)))
 for r in rows:
  x,y,a=map(float,[r['x_mm'],r['y_mm'],r['rotation_ccw_deg']])
  keys.append({'key':r['key'],'cap':xf(translate(rotate(box(-8,-8,8,8),a),x,y),t),'well':xf(translate(rotate(box(-9,-9,9,9),a),x,y),t)})
# Assembly-Y extrema of the SAME assumed 16 mm swept cap envelopes used in A/A2.
refs=[]
for side,prefix in [('left','L'),('right','R')]:
 for row,label,fn in [(1,'start',min),(2,'toe',max)]:
  k=next(k for k in keys if k['key']==f'{prefix}_R{row}_C5')
  pt=fn(list(k['cap'].exterior.coords)[:-1],key=lambda p:p[1])
  refs.append({'side':side,'key':k['key'],'line':label,'assembly_xy':list(pt),
   'local_corner_xy':[(25.055555556 if row==1 else 41.055555556)*(1 if side=='left' else -1),27 if row==1 else -6]})
START=refs[0]['assembly_xy'][1];TOE=refs[1]['assembly_xy'][1];RUNY=TOE-START
for r in refs:assert abs(r['assembly_xy'][1]-(START if r['line']=='start' else TOE))<1e-9
assert abs(refs[0]['assembly_xy'][0]+refs[2]['assembly_xy'][0])<1e-9
assert abs(refs[1]['assembly_xy'][0]+refs[3]['assembly_xy'][0])<1e-9
wells=unary_union([k['well'] for k in keys])
foot=shape(m['cover_outline']).union(box(-10,-18,10,18)).union(unary_union(margins))
start=box(-300,-300,300,START);toe=box(-300,-300,300,TOE)
plateau=foot.intersection(start).difference(wells)
slope=foot.intersection(toe).difference(start).difference(wells)
low=foot.difference(toe).difference(wells)
strips=[s.difference(wells) for s in strips]
original_strips=list(strips)
trimmed=[s.intersection(slope) for s in original_strips]
# Remove exactly the slope footprint; preserve any south material outside it.
strips=[s.difference(slope) for s in original_strips]
trim_checks=[]
for side,before,after,cut in zip(['left','right'],original_strips,strips,trimmed):
 south_outside=before.difference(start).difference(foot)
 assert after.symmetric_difference(before.difference(cut)).area<1e-9
 assert after.intersection(slope).area==0
 assert south_outside.difference(after).area<1e-9
 seam=after.intersection(slope).intersection(LineString([(-300,START),(300,START)]))
 assert seam.length>0
 trim_checks.append({'side':side,'before_area_mm2':before.area,'after_area_mm2':after.area,
  'trimmed_area_mm2':cut.area,'trim_bounds':cut.bounds,
  'retained_south_outside_slope_footprint_mm2':south_outside.area,
  'south_material_remaining_mm2':after.difference(start).area,
  'start_line_shared_edge_mm':seam.length})
raised=unary_union([plateau,slope,*strips]);strip_union=unary_union(strips)
strip_overlap=slope.intersection(strip_union)
assert strip_overlap.area==0
assert all(s.difference(start).area==0 for s in strips)  # no outlying south material in these inputs
assert abs(sum(c['trimmed_area_mm2'] for c in trim_checks)-27.229550903038)<1e-8
def roof(x,y):return TOP-(TOP-PLATE)*min(1,max(0,(y-START)/RUNY))
def old_roof(x,y):
 s=27.943753028777888-abs(x)/math.sqrt(3);e=67.20357133367244-abs(x)/math.sqrt(3)
 return TOP-(TOP-PLATE)*min(1,max(0,(y-s)/(e-s)))
checks=[]
for p in idx:
 if p['name'].startswith('Main-GH-') or p['name'] in ['cover-screw-2','cover-screw-3','cover-Main-spacer-2','cover-Main-spacer-3']:
  lo,hi=p['bounds'];x=lo[0] if abs(lo[0])>abs(hi[0]) else hi[0];y=hi[1];z=hi[2]-8.65
  xybox=box(lo[0],lo[1],hi[0],hi[1])
  assert xybox.intersection(strip_union).area<1e-6
  threshold=START+(TOP-SKIN-z-GAP)*RUNY/(TOP-PLATE)
  area=xybox.intersection(box(-300,threshold,300,300)).area
  # Exact area of the A2 failing portion, using its two mirrored linear facets.
  old_limit=67.20357133367244-(z+GAP+SKIN-PLATE)*39.25981830489455/(TOP-PLATE)
  old_bad=unary_union([Polygon([(0,old_limit),(300,old_limit-300/math.sqrt(3)),(300,300),(0,300)]),Polygon([(0,old_limit),(-300,old_limit-300/math.sqrt(3)),(-300,300),(0,300)])])
  checks.append({'name':p['name'],'xy_bounds':[lo[:2],hi[:2]],'obstacle_top_z':z,'limiting_xy':[x,y],
   'projection_outside_foot_mm2':xybox.difference(foot).area,'roof_z':roof(x,y),'underside_z':roof(x,y)-SKIN,'raw_gap':roof(x,y)-SKIN-z,'required_gap':GAP,
   'a2_raw_gap':old_roof(x,y)-SKIN-z,'a4_projected_area_below_required_gap_mm2':area,
   'a2_projected_area_below_required_gap_mm2':xybox.intersection(old_bad).area,
   'a4_failing_area_inside_foot_mm2':xybox.intersection(box(-300,threshold,300,300)).intersection(foot).area,
   'a2_failing_area_inside_foot_mm2':xybox.intersection(old_bad).intersection(foot).area,
   'pocket_ceiling_z':z+GAP,'pocket_depth_required':max(0,z+GAP-(roof(x,y)-SKIN)),
   'remaining_skin':roof(x,y)-(z+GAP),'verdict':'FAIL'})
fly=[]
for x,y,z in m['fly']['path_samples_mm']:
 z-=2.65
 rmin=min(roof(xx,yy) for xx in [x-1,x+1] for yy in [y-1,y+1])
 old_min=min(old_roof(xx,yy) for xx in [x-1,x+1] for yy in [y-1,y+1])
 fly.append({'x':x,'y':y,'axis_z':z,'gap':rmin-SKIN-(z+1),'a2_gap':old_min-SKIN-(z+1)})
fmin=min(fly,key=lambda p:p['gap'])
assert abs(RUNY-(33*math.sqrt(3)/2+8))<1e-9
assert abs(roof(0,START)-TOP)<1e-9 and abs(roof(0,TOE)-PLATE)<1e-9
assert all(abs(c['raw_gap']-c['a2_raw_gap'])<1e-9 for c in checks)
assert abs(m['fly']['connected_length_mm']-170)<1e-8
assert len(keys)==42
assert all(k['cap'].distance(raised)>=.999999 for k in keys)
assert slope.intersection(decks[0]).area>0 and slope.intersection(decks[1]).area>0
assert slope.intersection(box(-5,15,5,25)).area>0
assert slope.intersection(wells).area<1e-7
assert plateau.intersection(slope).area<1e-7
line_checks=[]
for label,y in [('start',START),('toe',TOE)]:
 line=LineString([(-160,y),(160,y)]).intersection(foot)
 for k in keys:
  overlap=line.intersection(k['well'])
  if overlap.length>1e-7:line_checks.append({'line':label,'key':k['key'],'well_chord_mm':overlap.length,'cap_chord_mm':line.intersection(k['cap']).length})
deck_ends=[]
for side,margin in zip(['left','right'],margins):
 boundary=margin.boundary.intersection(slope.buffer(1e-8)).difference(wells)
 # Interior-margin footprint terminates against adjacent low Wing deck here.
 deck_ends.append({'side':side,'band_margin_boundary_length_mm':boundary.length,
  'boundary_y_range':list(boundary.bounds[1::2]) if not boundary.is_empty else [],
  'maximum_band_rise_at_boundary_mm':max(roof(x,y)-PLATE for g in getattr(boundary,'geoms',[boundary]) for x,y in g.coords)})
# B-B retains A2 left local X45. Axis s is southward Wing-local distance.
a=math.sqrt(3)/2;t=d['wing_transforms']['left'];BLOCAL=(t['translation'][1]+.5*45-START)/a
BRUN=RUNY/a;BANGLE=math.degrees(math.atan((TOP-PLATE)/BRUN))
regions={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'name':n,'status':'A4 2D only; provisional q=1.50','role':'removed strip material; slope remains' if n.startswith('trimmed_') else 'current surface footprint'},'geometry':mapping(g)} for n,g in [('plateau',plateau),('slope',slope),('low_south',low),('north_left',strips[0]),('north_right',strips[1]),('trimmed_left',trimmed[0]),('trimmed_right',trimmed[1])]]}
(HERE/'raised-regions-a4.geojson').write_text(json.dumps(regions,indent=2)+'\n')
T={'status':'A4 2D strip trim only; ALL Z provisional, unmeasured Junana q=1.50','units':'mm; assembly Y south, Wing-local Y north',
 'plate_top':PLATE,'plateau_top':TOP,'roof_skin_vertical':SKIN,'required_gap':GAP,
 'cap_end_references':refs,'start_y':START,'toe_y':TOE,'center_run_y':RUNY,'center_angle_deg':math.degrees(math.atan((TOP-PLATE)/RUNY)),
 'c5_assembly_y_run':RUNY,'c5_assembly_y_angle_deg':math.degrees(math.atan((TOP-PLATE)/RUNY)),
 'c5_local_x_abs':33.055555556,
 'c5_local_start_y':(t['translation'][1]+.5*33.055555556-START)/a,
 'c5_local_toe_y':(t['translation'][1]+.5*33.055555556-TOE)/a,
 'wing_local_south_section_run':BRUN,'wing_local_south_section_angle_deg':BANGLE,
 'B_B_local_x':45,'B_B_start_local_y':BLOCAL,'B_B_toe_local_y':BLOCAL-BRUN,
 'main_checks':checks,'fly':{'length':m['fly']['connected_length_mm'],'radius':1,'raw_sample_translation_z':-2.65,'assembly_translation_z':-8.65,
 'min_gap':fmin,'samples':len(fly),'a4_samples_below_030':sum(p['gap']<GAP for p in fly),'a2_samples_below_030':sum(p['a2_gap']<GAP for p in fly),
 'verdict':'FAIL; unchanged from A3; no reroute'},
 'north_strip_trim':trim_checks,
 'north_strip_conflict':{'overlap_area_mm2':strip_overlap.area,'shared_boundary_bounds':strip_overlap.bounds,
 'maximum_height_disagreement_mm':TOP-roof(0,strip_overlap.bounds[3]) if not strip_overlap.is_empty else 0},
 'line_well_intersections':line_checks,'deck_band_ends':deck_ends,
 'cap_well_screen':{'count':42,'cap_square':16,'well_square':18,'nominal_gap_min':min(k['cap'].distance(raised) for k in keys),'budgeted_residual':.5,'required':.3},
 'interpretations':['Toe: maximum assembly Y corner of assumed 16 mm R2/C5 cap; no pitch-cell edge',
 'Start: minimum assembly Y corner of assumed 16 mm R1/C5 cap; PO-approved A4 trim boundary',
 'Both lines X-parallel; footprint and rotated 18 mm wells unchanged; north strips trimmed only by slope intersection',
 'North strips meet slope exactly at start line, equal Z24.65; no overlapping surface area',
 'All conservative screens use nominal band roof, full GH/hardware AABBs, Fly per-sample radius-one XY square; 2 mm vertical skin and 0.30 gap unchanged']}
prior=json.loads((HERE/'tables-a3.json').read_text())
for field in ['plate_top','plateau_top','roof_skin_vertical','required_gap','start_y','toe_y','center_run_y','center_angle_deg','cap_end_references']:
 assert T[field]==prior[field],field
for new,old in zip(T['main_checks'],prior['main_checks']):
 for field in ['raw_gap','underside_z','remaining_skin']:
  assert new[field]==old[field],(new['name'],field)
assert T['fly']['min_gap']==prior['fly']['min_gap']
assert T['north_strip_conflict']['maximum_height_disagreement_mm']==0
assert T['fly']['a4_samples_below_030']==prior['fly']['a3_samples_below_030']
prior_regions=json.loads((HERE/'raised-regions-a3.geojson').read_text())
for feature in prior_regions['features']:
 name=feature['properties']['name']
 if name in ['plateau','slope','low_south']:
  assert shape(feature['geometry']).symmetric_difference({'plateau':plateau,'slope':slope,'low_south':low}[name]).area==0,name
assert all(raised.intersection(k['well']).area<1e-7 for k in keys)
(HERE/'tables-a4.json').write_text(json.dumps(T,indent=2)+'\n')

def save(fig,name):
 fig.tight_layout(rect=(0,0,1,.94))
 for ext in ['png','svg']:
  target=HERE/f'{name}.{ext}';fig.savefig(target,dpi=180)
  if ext=='svg':target.write_text('\n'.join(line.rstrip() for line in target.read_text().splitlines())+'\n')
 plt.close(fig)
colors={'plateau':'#8ebed0','slope':'#e9ad61','strip':'#92bda0','low':'#eee9df'}
fig,axs=plt.subplots(1,2,figsize=(18,10),gridspec_kw={'width_ratios':[1.5,1]})
for ax in axs:
 for deck in decks:draw(ax,deck,fc=colors['low'],ec='#999',lw=.6)
 draw(ax,low,fc=colors['low'],ec='#999',lw=.5)
 for g,c in [(plateau,'plateau'),(slope,'slope'),*[(s,'strip') for s in strips]]:draw(ax,g,fc=colors[c],ec='#555',lw=.5)
 for cut in trimmed:draw(ax,cut,fc='none',ec='#b32626',ls=':',lw=.9)
 for k in keys:
  draw(ax,k['well'],fc='none',ec='#ba7979',lw=.65,ls=':');draw(ax,k['cap'],fc='white',ec='#666',lw=.5)
  if '_C5' in k['key'] or '_T' in k['key']:
   p=k['cap'].centroid;ax.text(p.x,p.y,k['key'].split('_',1)[1],fontsize=6,ha='center',va='center')
 for label,y,color in [('start',START,'#a02060'),('toe',TOE,'#394fb2')]:
  # Full straight reference line remains visible through wells, which are still removed.
  ax.plot([-68,68],[y,y],color=color,lw=1.3,ls='--')
  for r in refs:
   if r['line']==label:ax.plot(*r['assembly_xy'],'o',ms=4,color=color)
 ax.plot([0,0],[-56,75],'k-.',lw=.8)
 for p in checks:
  lo,hi=p['xy_bounds'];ax.add_patch(Rectangle(lo,hi[0]-lo[0],hi[1]-lo[1],fill=False,ec='#b32626',lw=.8,ls=':'))
 path=np.array(m['fly']['path_samples_mm']);ax.plot(path[:,0],path[:,1],color='#7560a6',lw=.7,alpha=.65)
 ax.set(aspect='equal',xlabel='Assembly X (mm)',ylabel='Assembly Y south (mm)');ax.grid(alpha=.12)
axs[0].set(xlim=(-153,153),ylim=(89,-72),title='Whole plan | fixed Main Rev.7 / Wing Rev.4 / aluminium plates')
axs[1].set(xlim=(-69,69),ylim=(81,-60),title='Detail | straight X-parallel cap-end references')
ax=axs[1]
ax.annotate(f'START Y{START:.3f}: R1/C5 northmost cap corners\nPO-approved strip trim boundary',xy=(0,START),xytext=(-65,-21),fontsize=8,color='#a02060',arrowprops={'arrowstyle':'->','color':'#a02060'})
ax.annotate(f'TOE Y{TOE:.3f}: R2/C5 southmost cap corners\nPO binding; 16 mm assumed cap, NOT pitch cell',xy=(0,TOE),xytext=(-66,73),fontsize=8,color='#394fb2',arrowprops={'arrowstyle':'->','color':'#394fb2'})
ax.text(4,-48,'A-A X0',fontsize=8)
ax.plot([-6,-6],[START-2,START+4],color='k',ls='-.',lw=1.5);ax.text(-16,START+8,'E (X−6)',fontsize=8)
ax.annotate('Strips trimmed to start: 13.614776 mm² each\nDotted outlines show removed material; overlap ZERO',xy=(-6,3.5),xytext=(-65,-36),fontsize=8,color='#b32626',arrowprops={'arrowstyle':'->','color':'#b32626'})
axs[0].legend(handles=[LegendPatch(fc=colors['plateau'],label='Plateau north of start: Z24.65'),LegendPatch(fc=colors['slope'],label='Straight-line slope band'),LegendPatch(fc=colors['strip'],label='Trimmed north strips: Z24.65'),LegendPatch(fc='none',ec='#b32626',ls=':',label='Removed strip material (slope remains)'),LegendPatch(fc=colors['low'],label='Low deck / south of toe: Z13.55'),LegendPatch(fc='white',ec='#ba7979',label='18 mm wells / assumed 16 mm caps')],loc='lower left',fontsize=8)
fig.suptitle(f'Issue 248 A4 — 2D strip trim ONLY | ALL Z provisional: unmeasured Junana q=1.50\nStart Y{START:.3f} / toe Y{TOE:.3f} / assembly-Y run {RUNY:.3f} mm / {T["center_angle_deg"]:.2f}°; wells cut unchanged',fontsize=13)
save(fig,'plan-a4')

fig,axs=plt.subplots(4,1,figsize=(15,17))
yy=np.linspace(-56,74,650);ax=axs[0];rr=np.array([roof(0,y) for y in yy])
ax.fill_between(yy,rr-2,rr,color=colors['slope'],label='Nominal 2 mm vertical skin')
ax.add_patch(Rectangle((-56,0),130,2,fc='#aaa',label='Retained 2 mm floor'))
ax.add_patch(Rectangle((2.267949,7.35),65.632051,1.2,fc='#8ebed0',label='Main Rev.7 PCB, X0 section'))
ax.plot([9.267949]*2,[8.55,10.65],color='k',lw=3)
for y,name in [(START,'start'),(TOE,'toe')]:ax.axvline(y,color='#777',ls=':',lw=.8);ax.text(y+.6,25.6,f'{name} Y{y:.3f}',fontsize=8)
ax.text(-53,15.5,f'Plateau Z24.65 → plate-level Z13.55\nCentre run {RUNY:.3f} mm / angle {T["center_angle_deg"]:.3f}°\nSame assembly-Y run / angle at all C5 reference X cuts',fontsize=9)
ax.set(title='A-A | centre X0: one planar slope between two straight horizontal plan lines',xlim=(-58,76),ylim=(-1,29))
ax=axs[1]; detail_x=-6.0
edge_cut=LineString([(detail_x,START-2),(detail_x,START+4)])
assert edge_cut.intersection(strips[0]).length>1.99
assert edge_cut.intersection(slope).length>3.99
assert edge_cut.intersection(wells).is_empty
ss=np.linspace(START-2,START+4,300);rr=np.array([roof(detail_x,y) for y in ss])
ax.fill_between(ss,rr-SKIN,rr,color=colors['slope'],alpha=.5,label='Nominal 2 mm vertical roof skin')
ax.plot([START-2,START],[TOP,TOP],color='#418455',lw=4,label='Trimmed left north strip: Z24.65 to start')
sy=np.linspace(START,START+4,150)
ax.plot(sy,[roof(detail_x,y) for y in sy],color='#ad6b23',lw=3,label='Slope takes over at start')
old_cut=edge_cut.intersection(trimmed[0])
old_end=old_cut.bounds[3]
ax.plot([START,old_end],[TOP,TOP],color='#b32626',ls=':',lw=2,label='A3 plateau extension removed (reference only)')
ax.axvline(START,color='#a02060',ls='--',lw=1)
ax.plot(START,TOP,'o',color='#222',ms=5)
ax.annotate(f'Shared start Y{START:.6f}, Z24.65\nZero area overlap / zero Z mismatch',xy=(START,TOP),xytext=(START+.55,TOP+.65),fontsize=9,arrowprops={'arrowstyle':'->'})
ax.text(START-1.85,TOP-3.35,'Edge detail at assembly X−6 (no well crossing).\nSame join mirrored at X+6; wells remain cut elsewhere.\nJoin / retention construction still requires Phase B qualification.',fontsize=9)
ax.set(title='E | strip-edge detail: plateau ends exactly where the unchanged slope begins',xlim=(START-2,START+4),ylim=(TOP-4,TOP+1.7))
ax=axs[2];gh=checks[0];x=gh['limiting_xy'][0];yy=np.linspace(-1,72,450);rr=np.array([roof(x,y) for y in yy])
ax.plot(yy,rr,color='#805022',lw=2,label=f'Band top at |X|={abs(x):.3f}');ax.plot(yy,rr-2,color='#805022',ls='--',label='Nominal 2 mm underside')
lo,hi=gh['xy_bounds'];ax.add_patch(Rectangle((lo[1],8.55),hi[1]-lo[1],4.55,fc='#8ebed0',label='Full GH projected AABB, top Z13.10 (both sides)'))
py=np.linspace(lo[1]-.3,hi[1]+.3,250);pu=np.array([roof(x,y)-2 for y in py]);ax.fill_between(py,pu,13.4,where=pu<13.4,interpolate=True,fc='none',ec='#b32626',hatch='////',lw=.5)
ax.plot([lo[1]-.3,hi[1]+.3],[13.4]*2,color='#b32626',lw=1.4,label='Unaccepted pocket ceiling Z13.40 (+0.30 gap)')
ax.plot([62.4,66.4],[13.55]*2,color='#b32626',lw=3,label='Adopted #246 cover head top Z13.55: raw gap −2.00')
ax.plot([62.15,66.65],[12.05]*2,color='#a46290',lw=3,label='Adopted #246 spacer top Z12.05: raw gap −0.50')
ax.text(1,21,'Main GH: gap −1.55, FAIL (unchanged from A3)\nPocket XY 17.167 ×22.145 (+0.30/side); depth 1.85 → skin 0.15: NOT accepted\nClosed 2 mm roof +0.30 gap needs top ≥15.40 at GH\nSouth hardware unchanged FAIL; head needs opening / retention redesign',fontsize=9,bbox={'facecolor':'white','alpha':.9,'edgecolor':'none'})
ax.annotate('GH gap −1.55\nrequired +0.30',xy=(hi[1],11.55),xytext=(53,17),fontsize=9,arrowprops={'arrowstyle':'->'})
ax.set(title='C | Main obstacle detail: conservative projected envelopes; no pocket / opening adopted',xlim=(-1,73),ylim=(7.5,27))
ax=axs[3];yy=np.linspace(-1,72,450);rr=np.array([roof(-14.6,y) for y in yy]);ax.plot(yy,rr,color='#805022',lw=2,label='Band top (independent of X)');ax.plot(yy,rr-2,color='#805022',ls='--',label='Nominal underside')
ax.fill_between([25,61.120415],[10.95]*2,[12.95]*2,color='#a7a0ce',label='Fly south storage projection: OD2, axis Z11.95')
ax.plot([38,63],[13.25]*2,color='#b32626',label='Unaccepted pocket ceiling Z13.25 for +0.30 gap')
ax.text(1,21,f'Existing 170 mm route: minimum gap −1.40, FAIL\nBelow +0.30: A4 {T["fly"]["a4_samples_below_030"]} / A2 {T["fly"]["a2_samples_below_030"]} of {len(fly)} samples; unchanged from A3\nPocket depth 1.70 → only 0.30 skin: NOT accepted\nNo reroute; retain exactly 170 / R≥5 / service and USB gates',fontsize=9,bbox={'facecolor':'white','alpha':.9,'edgecolor':'none'})
ax.set(title='D | Fly 170 south storage: full translated sampled OD2 envelope screen',xlim=(-1,73),ylim=(8,27))
for i,ax in enumerate(axs):
 ax.set(xlabel='Assembly Y south (mm)',ylabel='Provisional Z (mm)');ax.grid(alpha=.15);ax.legend(fontsize=7,loc='upper right' if i<2 else 'lower left')
fig.suptitle('Issue 248 A4 — sections / conflict screens ONLY | no production CAD or Phase B\nALL Z provisional q=1.50; 2 mm skin and +0.30 free gap retained; no new assembly PASS',fontsize=13)
save(fig,'sections-a4')
print(json.dumps(T,indent=2))
