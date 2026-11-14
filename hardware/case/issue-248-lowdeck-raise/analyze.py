"""Phase A envelopes only; no production solids. Run from repository root."""
import os, sys, json, csv, math, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RUN = ROOT / '.issue248-runtime'
os.environ['MPLCONFIGDIR'] = str(RUN / 'mpl')
os.environ['TMPDIR'] = str(RUN)
os.environ['XDG_CACHE_HOME'] = str(RUN / 'cache')
os.environ['MPLBACKEND'] = 'Agg'
sys.path.insert(0, str(RUN / 'pydeps'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch, Rectangle
from shapely.geometry import Polygon, box, shape, mapping
from shapely.affinity import affine_transform, rotate, translate
from shapely.ops import unary_union

def read(p): return json.loads((ROOT / p).read_text())
base = 'hardware/case/issue-232-final/17mm'
adopted = 'hardware/case/issue-246-delta6-tuning/packed/delta-6/17mm'
d = read(base + '/dimensions.json')
m = read(adopted + '/measurements.json')
plate = 2 + 4.85 + .5 + 1.2 + 3.5 + 1.5
top = plate + 11.1 + 3.5 - 5 + 1.5
def roof(y): return top if y <= 8 else max(plate, top - (y-8)*(top-plate)/61.7)
def xf(g,t):
    a=t['matrix']; return affine_transform(g,[a[0][0],a[0][1],a[1][0],a[1][1],*t['translation']])
keys=[]; north=[]; decks=[]
for side in ['left','right']:
    t=d['wing_transforms'][side]
    rows=list(csv.DictReader((ROOT/base/f'plate-package/apertures-{side}-local.csv').open()))
    r0=sorted([r for r in rows if '_R0_' in r['key']],key=lambda r:float(r['x_mm']))
    # Follow staggered north row, rather than using a global horizontal band.
    line=[(float(r['x_mm']),float(r['y_mm'])+9) for r in r0]
    capline=[(-300,line[0][1]),*line,(300,line[-1][1]),(300,300),(-300,300)]
    deck=Polygon(next(p['deck_outline_xy_mm'] for p in d['plates'] if p['side']==side));decks.append(deck)
    for r in rows:
        x,y,a=map(float,[r['x_mm'],r['y_mm'],r['rotation_ccw_deg']])
        cap=xf(translate(rotate(box(-8,-8,8,8),a),x,y),t)
        well=xf(translate(rotate(box(-9,-9,9,9),a),x,y),t)
        center=xf(box(x-.0001,y-.0001,x+.0001,y+.0001),t).centroid
        keys.append(dict(key=r['key'],center=[center.x,center.y],cap=cap,well=well))
    north.append(deck.intersection(xf(Polygon(capline),t)))
wells=unary_union([k['well'] for k in keys])
central=shape(m['cover_outline']).union(box(-10,-18,10,18)).difference(wells)
north=[g.difference(wells) for g in north]
regions={'central':mapping(central),'north_left':mapping(north[0]),'north_right':mapping(north[1])}
(HERE/'raised-regions.geojson').write_text(json.dumps(regions,indent=2)+'\n')
table={
 'units':'mm; assembly X right, Y south, Z up; floor underside Z0; feet excluded',
 'status':'Phase A conditional envelope; no CAD/physical gate claimed',
 'stack':{'floor_top':2,'gh_nominal':4.35,'gh_allowance':.5,'floor_gap':.5,'pcb_underside':7.35,'pcb_thickness':1.2,'pcb_top':8.55,'spacer':3.5,'plate_thickness':1.5,'plate_bottom':12.05,'plate_top':plate,'post_bottom':1.2,'post_height':6.15},
 'bounds':[{'item':'Hall + floor + gap + upper stack','plate_min':12.1},{'item':'MUX','plate_min':10.1},{'item':'capacitor','plate_min':9.7},{'item':'mated GH including allowance (binding)','plate_min':plate},{'item':'retained M2x12, 5.5 engagement, 1.2 residual boss root','plate_min':12.9}],
 'references':[{'design':'D-041 Delta6','plate_top':22.2,'underside':16},{'design':'issue232 Delta0','plate_top':16.2,'underside':10},{'design':'issue248 conditional minimum','plate_top':plate,'underside':7.35}],
 'keytop':{'pcb_to_housing_top':11.1,'stem_above_housing':3.5,'pcb_to_plate_top':5,'cap_top_above_stem_tip_assumed':1.5,'cap_offset_assumption_range':[.5,2.5],'relative_nominal':top-plate,'absolute_nominal':top,'offset_uncertainty_budget':1.75,'travel_nominal':3.5,'travel_max':3.7,'pressed_top_nominal':top-3.5},
 'slope':{'start_y':8,'toe_y':69.7,'run':61.7,'rise':top-plate,'angle_deg':math.degrees(math.atan((top-plate)/61.7))},
 'clearance':{'assumed_max_cap_square':16,'well_square':18,'nominal_radial':1,'radial_budget':.5,'residual_radial':.5,'required':.3,'switch_max_width_budget':15.8,'switch_radial':1.1,'skirt_bottom_full_press_required_above_plate':.4,'cap_measurement_available':False},
 'route_baseline':[{'side':w['side'],'longest':w['longest_conductor_mm'],'margin':200-w['longest_conductor_mm'],'reserve':min(w['per_conductor_reserve_mm'])} for w in m['wings']],
 'slope_checks':[{'y':y,'roof':roof(y),'underside_2mm_shell':roof(y)-2} for y in [8,22.1,30.315,51.86,61.12,64.4,67.9,69.7]],
 'print_envelopes_including_5mm_brim':[{'part':'tray-left or north-left insert upper bound','xy':[159.021,156.069]},{'part':'tray-right or north-right insert upper bound','xy':[152.021,156.069]},{'part':'central shell allocation','xy':[100,150]}],
 'cost_assumptions':{'currency':'USD, planning only, no quote, excludes trays and existing plates','printed_material_grams':[60,140],'filament_usd_per_kg':[20,30],'printed_material_cost':[1.2,4.2],'printed_hardware':[2,6],'printed_shop_allowance':[20,60],'machined_set_one_off':[120,400],'machined_set_batch10_each':[45,140]},
 'keys':[{'key':k['key'],'center_xy':k['center'],'cap_well_radial_nominal':k['cap'].distance(unary_union([central,*north]))} for k in keys]
}
assert abs(plate-13.55)<1e-8 and len(keys)==42
assert all(k['cap'].distance(unary_union([central,*north]))>=.999999 for k in keys)
assert all(max(r['xy'])<=220 for r in table['print_envelopes_including_5mm_brim'])
(HERE/'tables.json').write_text(json.dumps(table,indent=2)+'\n')
def drawpoly(ax,g,**kw):
    if g.is_empty:return
    for p in ([g] if g.geom_type=='Polygon' else g.geoms):
        ax.add_patch(Patch(list(p.exterior.coords),**kw))
        for ring in p.interiors:ax.add_patch(Patch(list(ring.coords),fc='white',ec='none'))
def save(fig,name):
    fig.tight_layout()
    for ext in ['png','svg']:
        target=HERE/f'{name}.{ext}'
        fig.savefig(target,dpi=170)
        if ext=='svg':target.write_text('\n'.join(line.rstrip() for line in target.read_text().splitlines())+'\n')
    plt.close(fig)
fig,ax=plt.subplots(figsize=(12,8))
for deck in decks:drawpoly(ax,deck,fc='#eee9df',ec='#777')
drawpoly(ax,central,fc='#e0a35a',ec='#805022',alpha=.85)
for g in north:drawpoly(ax,g,fc='#83b6ce',ec='#31586d')
for k in keys:
    drawpoly(ax,k['well'],fc='none',ec='#9b7373',lw=.5)
    drawpoly(ax,k['cap'],fc='white',ec='#666',lw=.5)
    if '_R1_' in k['key']:ax.plot(*k['center'],'.',color='#8a3e8c',ms=3)
for y,label in [(8,'Slope starts Y8 (second-row band)'),(69.7,'Toe Y69.7')]:
    ax.axhline(y,color='#7d3b73',ls='--',lw=.8);ax.text(-145,y-2,label,fontsize=8)
ax.plot([0,0],[-55,80],'k-.',lw=.8);ax.text(1,-57,'A-A centre')
ax.text(-140,83,'Orange: central raise/slope; blue: north raises; pale: low deck/palm\nDashed wells 18 square; assumed swept caps 16 square. R1 centres purple.',fontsize=9)
ax.set(xlim=(-153,153),ylim=(96,-72),aspect='equal',xlabel='Assembly X (mm)',ylabel='Assembly Y south (mm)',title='Issue 248 Phase A | 17 mm pitch | proposed raised regions\nTop Z24.65 provisional; deck Z13.55 conditional; no production CAD')
k=next(k for k in keys if k['key']=='L_R0_C3')
cx,cy=k['center']; ax.plot([cx-10,cx+10],[cy+17.32,cy-17.32],'k-.',lw=.8); ax.text(cx+10,cy-18,'B-B',fontsize=8)
ax.grid(alpha=.15);save(fig,'plan')
fig,axs=plt.subplots(3,1,figsize=(12,11))
ax=axs[0]
ys=[-56,8,69.7,69.7];zs=[top,top,plate,plate]
ax.fill_between(ys,[z-2 for z in zs],zs,color='#e0a35a',label='Proposed 2 mm removable shell (schematic)')
ax.add_patch(Rectangle((-56,0),125.7,2,fc='#aaa'))
ax.add_patch(Rectangle((2.268,7.35),65.632,1.2,fc='#83b6ce',label='Main board at centre X0'))
ax.plot([9.268,9.268],[8.55,10.65],color='black',lw=4)
ax.axhline(plate,color='#888',ls=':',lw=.7);ax.text(-54,plate+.3,'Wing plate Z13.55 (reference)',fontsize=8)
ax.text(-53,4,'Floor top Z2; Fly/north USB seat to be remade',fontsize=9)
ax.text(-45,18,'Central mass: GH rises / separate Fly storage\nNo inference of cable clearance from this section',fontsize=9)
ax.set(title='A-A | longitudinal centre section X0 (shell and board envelope)',xlim=(-60,82),ylim=(-1,29))
ax=axs[1]
# Local longitudinal section through L_R0_C3, north is positive local Y.
ax.add_patch(Rectangle((-20,12.05),40,1.5,fc='#bbb',label='1.50 aluminium plate'))
ax.add_patch(Rectangle((-20,7.35),40,1.2,fc='#83b6ce',label='Wing PCB'))
ax.add_patch(Rectangle((9,plate),11,top-plate,fc='#83b6ce',alpha=.6,label='North raise; begins +9 from key centre'))
ax.add_patch(Rectangle((-8,plate+.4),16,top-(plate+.4),fill=False,ec='#555',ls='--',label='Combined assumed swept cap envelope'))
ax.plot([-8,8],[top,top],color='#555');ax.plot([-8,8],[top-3.7,top-3.7],color='#b64a3a')
ax.annotate('1.0 nominal / >=0.5 budgeted gap',xy=(8.5,18),xytext=(-18,27),fontsize=9,arrowprops={'arrowstyle':'->'})
ax.annotate('Vertical extraction after cap removal;\nremove raised shell for clip-tool access',xy=(0,26),xytext=(-18,2),fontsize=8,arrowprops={'arrowstyle':'->'})
ax.set(title='B-B | Wing north margin: local longitudinal cut through a north-row key',xlim=(-21,22),ylim=(0,30))
ax=axs[2]
yy=[8,22.1,30.315,51.86,61.12,64.4,67.9,69.7]
ax.plot(yy,[roof(y) for y in yy],color='#805022',lw=2,label='Slope top')
ax.plot(yy,[roof(y)-2 for y in yy],color='#805022',ls='--',label='2 mm shell underside')
ax.add_patch(Rectangle((30.315,8.55),51.86-30.315,4.55,fc='#83b6ce',label='Main GH conservative YZ projection; off-centre'))
ax.plot([2.268,67.9],[8.55,8.55],color='blue',label='Main PCB top')
ax.plot([64.4],[10.65],'ko',label='Main screw top after lowering')
ax.text(10,16,'Drop 11.10 over 61.7 mm = 10.20 deg\nStart Y8; toe Y69.7; roof checked against component maxima',fontsize=9)
ax.set(title='C-C | central south slope detail, with off-axis obstacle projections',xlim=(0,80),ylim=(7,27))
for ax in axs:
    ax.set(xlabel='Assembly Y south (mm)' if ax!=axs[1] else 'Local distance north from key centre (mm)',ylabel='Z (mm)');ax.grid(alpha=.2);ax.legend(fontsize=7,loc='upper right')
save(fig,'sections')
inputs=[ROOT/base/'plate-package/apertures-left-local.csv',ROOT/base/'plate-package/apertures-right-local.csv',ROOT/'hardware/kicad/qualification/issue-235-wing-round2/wing-rev4-17mm-left/definition.json',ROOT/'hardware/kicad/qualification/issue-235-wing-round2/wing-rev4-17mm-right/definition.json',ROOT/adopted/'gates.json',ROOT/adopted/'service.json',ROOT/adopted/'metrology.json',ROOT/base/'dimensions.json',ROOT/adopted/'measurements.json',ROOT/adopted/'assembly-index.json',ROOT/'docs/decisions.md',ROOT/'hardware/kicad/qualification/issue-194-wing-rev2/sources/jade-pro.pdf']
(HERE/'sources'/'input-sha256.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},indent=2)+'\n')
print(f'42 cap/raise distance screens >=1 mm; stack {plate:.2f}; keytop {top:.2f}; bed allocations fit. Not a full CAD audit.')
