"""Locate blocking copper components/clearances in native PCB coordinates."""
from pathlib import Path
import json,sys,importlib.util,html
import pcbnew as p
from shapely.ops import unary_union
E=Path(__file__).resolve().parent;BASE=E.parent/'issue-200-wing-rev3';sys.path.insert(0,str(BASE))
s=importlib.util.spec_from_file_location('repair',BASE/'plane-repair.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
allrows=[]
for w in sorted(E.glob('wing-rev4-*')):
 b=p.LoadBoard(str(w/'main.kicad_pcb'));q=json.loads((w/'qualification.json').read_text());groups={};labels=[]
 for net in q['physical_disconnected']:
  gs=r.components(b,net)
  records=[]
  for g in gs:
   refs=[]
   for f in b.GetFootprints():
    for a in f.Pads():
     if a.GetNetname()!=net:continue
     ls=[l for l in (p.F_Cu,p.B_Cu) if a.IsOnLayer(l)]
     if any(r.padgeom(a,l).intersects(geom) for geom,layers,_,item in g for l in ls if l in layers):refs.append(f.GetReference()+'.'+a.GetNumber())
   records.append({'pads':sorted(set(refs)),'copper_bbox_mm':list(unary_union([a[0] for a in g]).bounds)})
  groups[net]=records
  for g in sorted(records,key=lambda x:len(x['pads']))[:-1]:labels+=g['pads']
 drc=json.loads((w/'drc.json').read_text());rows={'variant':w.name,'independent_disconnected_pad_components':groups,'native_DRC_violations':drc['violations'],'DRC_unconnected':len(drc['unconnected_items']),'ERC':'not run: inherited Wing package has no native schematic','min_via_pad_gap_mm':q['min_via_pad_gap_mm'],'width_below_floor':q['width_below_floor'],'pass':q['pass']}
 (w/'final-state.json').write_text(json.dumps({'qualified_routing':q['pass'],'board_sha256':q['sha256'],'voltage_extraction':'resistance-extraction.json' if q['pass'] else 'not performed on failing board','native_ERC':'unavailable: no inherited native schematic'},indent=2)+'\n')
 (w/'blocking-regions.json').write_text(json.dumps(rows,indent=2)+'\n');allrows.append(rows)
 bb=b.GetBoardEdgesBoundingBox();x,y=bb.GetX()/1e6,bb.GetY()/1e6;ww,hh=bb.GetWidth()/1e6,bb.GetHeight()/1e6
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x-4} {y-6} {ww+8} {hh+12}">',f'<text x="{x}" y="{y-2}" font-size="2">{w.name}: diagnostic ONLY / F cyan, B orange; native PCB mm</text>']
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):
   a=r.xy(t.GetPosition());svg.append(f'<circle cx="{a[0]}" cy="{a[1]}" r=".3" fill="#777"/>');continue
  a=r.xy(t.GetStart());z=r.xy(t.GetEnd());color='#088' if t.GetLayer()==p.F_Cu else '#d83'
  svg.append(f'<path d="M{a[0]},{a[1]} L{z[0]},{z[1]}" stroke="{color}" stroke-width="{p.ToMM(t.GetWidth())}"/>')
 for f in b.GetFootprints():
  for a in f.Pads():
   c=r.xy(a.GetPosition());sz=r.xy(a.GetSize());ident=f.GetReference()+'.'+a.GetNumber();mark=ident in labels
   svg.append(f'<rect x="{c[0]-sz[0]/2}" y="{c[1]-sz[1]/2}" width="{sz[0]}" height="{sz[1]}" fill="{ "red" if mark else "#777"}" transform="rotate({-a.GetOrientationDegrees()},{c[0]},{c[1]})"/>')
   if mark:svg.append(f'<text x="{c[0]+1}" y="{c[1]}" font-size="1.2" fill="#900">{html.escape(ident)}</text>')
 for d in b.GetDrawings():
  if d.GetLayer()==p.Edge_Cuts:
   a=r.xy(d.GetStart());z=r.xy(d.GetEnd());svg.append(f'<path d="M{a[0]},{a[1]} L{z[0]},{z[1]}" stroke="#333" stroke-width=".15"/>')
 svg.append('</svg>');(w/'congestion-map.svg').write_text('\n'.join(svg))
(E/'congestion-summary.json').write_text(json.dumps(allrows,indent=2)+'\n');print('Saved component-level blocking evidence for all four variants')
