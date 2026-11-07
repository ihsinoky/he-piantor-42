"""Render saved final copper and manufacturing panel; no PCB mutation."""
from pathlib import Path
from html import escape
import pcbnew as p
from verify import polys,padgeom,xy
E=Path(__file__).resolve().parent

def path(g):
 parts=[]
 for poly in g.geoms if hasattr(g,'geoms') else [g]:
  if poly.is_empty:continue
  for ring in [poly.exterior,*poly.interiors]:parts.append('M '+' L '.join(f'{x:.6f},{y:.6f}' for x,y in ring.coords)+' Z')
 return ' '.join(parts)
def render(w):
 b=p.LoadBoard(str(w/'main.kicad_pcb'));outline=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(outline);board=polys(outline);x0,y0,x1,y1=board.bounds
 for layer,side in ((p.F_Cu,'top'),(p.B_Cu,'bottom')):
  svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0-3} {y0-7} {x1-x0+6} {y1-y0+12}" width="1200" height="{1200*(y1-y0+12)/(x1-x0+6)}">','<rect x="-1000" y="-1000" width="3000" height="3000" fill="white"/>',f'<text x="{x0}" y="{y0-3}" font-size="2" font-family="monospace">{w.name} {side}: top-view coordinates (bottom is NOT mirrored)</text>',f'<path d="{path(board)}" fill="#fafafa" stroke="#222" stroke-width=".12" fill-rule="evenodd"/>']
  for z in b.Zones():
   if not z.GetIsRuleArea() and z.IsOnLayer(layer):svg.append(f'<path d="{path(polys(z.GetFilledPolysList(layer)))}" fill="#e0e9e7" fill-rule="evenodd"/>')
  for t in b.GetTracks():
   if isinstance(t,p.PCB_VIA):
    x,y=xy(t.GetPosition());svg.append(f'<circle cx="{x}" cy="{y}" r=".3" fill="#cda951"/><circle cx="{x}" cy="{y}" r=".15" fill="white"/>')
   elif t.GetLayer()==layer:
    x,y=xy(t.GetStart());xx,yy=xy(t.GetEnd());color='#af594d' if t.GetNetname()=='HALL_5V' else '#477b68' if t.GetNetname()=='GND' else '#8d9ba4';svg.append(f'<path d="M{x},{y} L{xx},{yy}" stroke="{color}" stroke-width="{p.ToMM(t.GetWidth())}" stroke-linecap="round"/>')
  for f in b.GetFootprints():
   for a in f.Pads():
    if a.GetAttribute()==p.PAD_ATTRIB_NPTH:
     x,y=xy(a.GetPosition());svg.append(f'<circle cx="{x}" cy="{y}" r="{p.ToMM(a.GetDrillSize().x)/2}" fill="white" stroke="#333" stroke-width=".05"/>')
    elif a.IsOnLayer(layer):svg.append(f'<path d="{path(padgeom(a,layer))}" fill="#bc9240" fill-rule="evenodd"><title>{escape(f.GetReference()+"."+a.GetNumber()+" "+a.GetNetname())}</title></path>')
   if f.GetLayer()==layer and not f.GetReference().startswith(('MH','H','MB','TOOL','L_H','R_H','L_MH','R_MH','TP','L_TP','R_TP')):
    x,y=xy(f.GetPosition());svg.append(f'<text x="{x}" y="{y-1.5}" text-anchor="middle" font-size=".9" font-family="monospace">{escape(f.GetReference())}</text>')
    for a in f.Pads():
     if a.GetNumber()=='1':
      x,y=xy(a.GetPosition());svg.append(f'<circle cx="{x}" cy="{y}" r=".18" fill="#da2b3e"/>')
  svg.append('</svg>');(w/f'assembly-{side}.svg').write_text('\n'.join(svg)+'\n')
for w in sorted(E.glob('wing-rev3-*'))+sorted(E.glob('panel-*')):
 if (w/'main.kicad_pcb').exists():render(w)
