"""SVG study drawings from measured polygons, path samples and BRep sections."""
import json,math,html
from pathlib import Path
from shapely.geometry import Polygon,shape
HERE=Path(__file__).resolve().parent
R=HERE.parents[2]
class SVG:
 def __init__(self,w,h,title):
  self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="#fff"/><style>text{{font-family:DejaVu Sans,sans-serif;fill:#253347}} .dim{{stroke:#ba3349;stroke-width:1.5}} </style>',f'<text x="35" y="42" font-size="25" font-weight="bold">{html.escape(title)}</text>']
 def text(self,x,y,t,size=16,color='#253347'):
  self.s.append(f'<text x="{x}" y="{y}" font-size="{size}" style="fill:{color}">{html.escape(t)}</text>')
 def line(self,pts,color='#253347',width=1,dash=''):
  self.s.append(f'<polyline points="'+ ' '.join(f'{x:.3f},{y:.3f}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>')
 def poly(self,g,tf,fill,stroke='#586c80',width=1):
  if g.is_empty:return
  if g.geom_type!='Polygon':
   for q in g.geoms:self.poly(q,tf,fill,stroke,width)
   return
  rings=[g.exterior,*g.interiors];d=' '.join('M '+' L '.join(f'{x:.3f},{y:.3f}' for x,y in [tf(*p) for p in ring.coords])+' Z' for ring in rings)
  self.s.append(f'<path d="{d}" fill="{fill}" fill-rule="evenodd" stroke="{stroke}" stroke-width="{width}"/>')
 def rect(self,x,y,w,h,fill,stroke='none'):
  self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>')
 def save(self,name):
  (HERE/name).write_text('\n'.join(self.s+['</svg>'])+'\n')
  import cairosvg
  cairosvg.svg2png(url=str(HERE/name),write_to=str((HERE/name).with_suffix('.png')))

def draw(results,inventory):
 from shapely.geometry import box,Point
 d=json.loads((HERE.parent/'issue-228-final/17mm/dimensions.json').read_text())
 d232=json.loads((HERE.parent/'issue-232-final/17mm/dimensions.json').read_text())
 od=json.loads((HERE.parent/'issue-228-final/17mm/outline-check.json').read_text())
 main=Polygon(d['boards']['main']);outer=Polygon(od['outer_xy_mm']);res=results[1]
 fig=SVG(1600,1020,'Issue 238 | Flush Z16.2 bay cover — INFEASIBLE with current Main GH plugs')
 fig.text(35,78,'Top view: native case silhouette and #232 deck outlines. Blue outline is a study proposal, not fabrication geometry.')
 tf=lambda x,y:(530+x*3.15,350+y*3.15)
 fig.poly(outer,tf,'#edf0f4')
 for p in d232['plates']:fig.poly(Polygon(p['blank_outline_xy_mm']),tf,'#d6dee7')
 fig.poly(shape(res['cover_outline']),tf,'#b9e3f1','#1686ad',2)
 for name,g in d['boards'].items():
  if name=='main':fig.poly(Polygon(g),tf,'#f7e1ac','#ad903c')
 for r in results:
  if r['pitch_mm']==16:fig.poly(shape(r['cover_outline']),tf,'none','#9259af',1.3)
 fig.text(80,650,'Grey: retained Wing decks/rim silhouette (17 mm); purple line: 16 mm cover boundary.')
 fig.text(80,680,'Cover/rim seam 0.20 mm nominal; top step 0.00 at Z16.20. USB keepout remains open at nose.')
 fig.text(80,710,'Cover would need its own internal supports: existing inner deck edges have no shared cover ledge.')
 fig.text(80,740,'Two hidden edge catches plus captive underside M2 screws are a concept only; no support layout is qualified.')
 fig.text(80,790,'Fixed blockers (both pitches):',20)
 fig.text(80,822,'• GH housings top Z18.50; R5/OD1 exit turn reaches at least Z24.00.')
 fig.text(80,850,'• Retained rack top Z22.20; uniform 1.5 mm roof also hits Fly shell (Z14.90) and tray material.')
 fig.text(80,878,'• Large empty volume does not remove the mandatory upward exit at J2/J3.')
 ztf=lambda x,y:(1315+x*5,400+y*5)
 fig.text(1100,110,'Bay zoom (17 mm)',20)
 fig.poly(shape(res['cover_outline']),ztf,'#e0f2f8','#1686ad',2)
 fig.poly(main,ztf,'#f8eed5','#ad903c')
 # Native component plan envelopes, not inherited all-5mm height reservations.
 for c in json.loads((R/'hardware/kicad/qualification/issue-235-wing-round2/main-native-obstacles.json').read_text()):
  fig.poly(shape(c['geometry']),ztf,'#eaa0a6' if c['ref'] in ('J2','J3') else '#dde3cb','#955158' if c['ref'] in ('J2','J3') else '#9b9f86',.6)
 for h in d232['mounts']:
  if h['board']=='main':fig.poly(Point(*h['xy']).buffer(2.25),ztf,'#78899b')
 fig.poly(box(-32,-26.5,32,-11.5),ztf,'none','#ba3349',1.5)
 pts=json.loads((HERE/'17mm-fly-path.json').read_text())
 for a,b in zip(pts,pts[1:]):fig.line([ztf(a[0],a[1]),ztf(b[0],b[1])],'#147d65' if a[2]>10 else '#316cce',1.6)
 fig.text(1100,805,'Fly 170 mm candidate: blue lower / green upper.',14)
 fig.text(1100,830,'R5; Ø2 envelope. Measured collisions in JSON.',14)
 fig.text(1100,855,'Candidate status: '+('isolated fit' if res['fly_trial']['passed'] else 'REJECTED'),16)
 fig.text(1100,885,'Main top Z11.2 / underside Z10 / floor Z2',14)
 fig.text(1100,910,'All XY in mm; north up, positive Y south.',14)
 fig.save('top-view.svg')
 # Local GH vertical section; rotate this local plane with the native J2/J3 row.
 fig=SVG(1400,825,'Section A–A | Main BM14B + GHR-14V-S, normal to the connector row')
 fig.text(35,78,'JST assembly layout: 7.30 mm rigid mated stack; vertical wire exit. Same obstruction at both ports and pitches.')
 sf=lambda u,z:(330+u*19,610-z*19)
 def rect(u0,z0,u1,z1,color):
  x,y=sf(u0,z1);fig.rect(x,y,(u1-u0)*19,(z1-z0)*19,color)
 rect(-12,0,20,2,'#aab4bf');rect(-10,10,15,11.2,'#69a87f');rect(-12,14.7,20,16.2,'#b9e3f1')
 rect(-2.125,11.2,2.125,15.45,'#616e7c');rect(-1.9,12.8,1.9,18.5,'#e6a2aa')
 bend=[(5-5*math.cos(t),18.5+5*math.sin(t)) for t in [i*math.pi/2/100 for i in range(101)]]+[(12,23.5)]
 fig.line([sf(*p) for p in bend],'#bf6343',19)
 for z,t in [(2,'Z2 floor'),(10,'Z10 Main underside'),(11.2,'Z11.2 Main top'),(14.7,'Z14.7 lid underside'),(16.2,'Z16.2 REQUIRED top'),(18.5,'Z18.5 mated housing top'),(24,'Z24.0 wire top (minimum R5 turn)')]:
  y=sf(0,z)[1];fig.line([sf(-12,z),sf(20,z)],'#aab4bf',.6,'3 4');fig.text(760,y+5,t,16)
 fig.text(35,700,'R5 bend: inherited #232 design minimum.',16)
 fig.text(35,730,'Ø1 wire; zero straight length is optimistic.',16)
 fig.text(35,760,'No vendor minimum bend is invented here.',16)
 fig.text(760,700,'Rigid shortfall: 2.30 mm even for zero roof.',17,'#ba3349')
 fig.text(760,730,'With 1.50 roof: 3.80 mm rigid / 9.30 mm bent.',17,'#ba3349')
 fig.text(35,805,'Diagram uses manufacturer dimensions; internal mating overlap is schematic. Solder/tolerance allowance +0.20 is additional.',14)
 fig.save('section-gh.svg')
 # Exact BRep longitudinal section, plus the defective shell external envelope and measured USB envelope.
 fig=SVG(1440,720,'Section B–B | Longitudinal bay at X=0 (17 mm; same Z datums at 16 mm)')
 fig.text(35,80,'Solid edges: exact retained BRep intersections sampled ≤0.1 mm. Dashed rectangles: named external envelopes/projections.')
 sf=lambda y,z:(100+(y+60)*9,500-z*14)
 sections=json.loads((HERE/'section-x0.json').read_text()) if (HERE/'section-x0.json').exists() else []
 for s in sections:
  fig.line([sf(*p) for p in s['yz_mm']],'#245e3e' if s['part']=='main' else '#b34f5b' if s['part']=='cable-rack' else '#77889a',1)
 # Roof nominal span, with USB nose retreat; it is a probe showing conflicts.
 x,y=sf(-54.76,16.2);fig.rect(x,y,(69.9+54.76)*9,1.5*14,'#b9e3f1')
 # defective shell: valid external bbox (from saved assembly) only, not healed.

 for a,b,col in [((-54.514,10.6),(-47.209,14.9),'#9d66aa'),((-69.964,10.32),(-54.964,16.32),'#bf6343')]:
  pts=[sf(a[0],a[1]),sf(a[0],b[1]),sf(b[0],b[1]),sf(b[0],a[1]),sf(a[0],a[1])];fig.line(pts,col,1.5,'5 3')
 for z in (0,2,10,11.2,14.7,16.2,22.2):
  fig.line([sf(-60,z),sf(73,z)],'#9aa7b4',.6,'3 4');fig.text(1310,sf(0,z)[1]+5,f'Z{z:g}',14)
 for y in (-50,-30,-10,10,30,50,70):
  fig.line([sf(y,0),sf(y,-.5)],'#586c80');fig.text(sf(y,0)[0]-10,525,str(y),14)
 fig.text(100,565,'Fly EZmate plug: Z8.10–9.40; board bottom Z10; mated stack 1.90, floor gap 6.10.',16)
 fig.text(100,595,'Under Main: 8.00 mm gross height; three bosses and source case/splice hardware are subtracted in volume budget.',16)
 fig.text(100,625,'Rack top is Z22.20 (20.20 mm part height above Z2), not a Z20.20 top datum.',16)
 fig.text(100,655,'USB overmold top Z16.32 requires a small open nose/setback; a roof cannot occupy its insertion envelope.',16)
 fig.save('section-bay.svg')
