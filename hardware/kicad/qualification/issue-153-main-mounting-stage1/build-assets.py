"""Generate review SVG/CSV and input provenance from read-only survey results.

Writes only the evidence directory or an explicit review output directory.
No CAD/manufacturing output.
"""
from pathlib import Path
import argparse
import collections
import csv
import hashlib
import html
import json
import math
import measure

SOURCE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--output-dir',type=Path,default=SOURCE)
args=parser.parse_args()
E=args.output_dir
E.mkdir(parents=True,exist_ok=True)
ROOT=measure.ROOT
data=json.loads((SOURCE/'measurements.json').read_text())
inv=data['inventory']
rows=data['survey']['candidates']
byname={r['label']:r for r in rows}
plans={
    'A-retain-4':['W-upper','NE-corner','SW-corner','S-proposed'],
    'A0-retain-3':['N-inner','E-middle','SW-corner'],
    'B-extend-4':['extension-NW','extension-NE','extension-SW','extension-SE']}
affected=[]
for plan,names in plans.items():
    seen=set()
    for name in names:
        for group,g in byname[name]['groups'].items():
            for hit in g['keepout_hits']:
                i=hit['item']
                if i['uuid'] in seen: continue
                seen.add(i['uuid'])
                affected.append(dict(plan=plan,candidate=name,kind=i['kind'],uuid=i['uuid'],net=i['net'],
                    layer=i.get('layer','through'),start_x=i.get('a',i.get('xy'))[0],
                    start_y=i.get('a',i.get('xy'))[1],end_x=i.get('b',i.get('xy'))[0],
                    end_y=i.get('b',i.get('xy'))[1],width=i.get('width',i.get('diameter')),
                    keepout_intrusion_mm=round(-hit['keepout_gap'],6)))
with (E/'affected-copper.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(affected[0]),lineterminator='\n')
    w.writeheader();w.writerows(affected)
with (E/'candidates.csv').open('w') as f:
    fields=['candidate','x','y','local_x','local_y','edge_center','hole_ligament','keepout_edge_gap','head_4_5_edge_gap',
            'pad_keepout_gap','track_keepout_gap','via_keepout_gap','courtyard_keepout_gap','provisional_body_keepout_gap',
            'existing_drill_gap','pad_hits','track_hits','via_hits','plane_hit']
    w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
    native={r['label']:r for r in json.loads((SOURCE/'native-crosscheck.json').read_text())['rows']}
    for r in rows:
        d=dict(candidate=r['label'],x=r['xy'][0],y=r['xy'][1],local_x=r['local_xy'][0],local_y=r['local_xy'][1],
            edge_center=r['edge_center_distance'],hole_ligament=r['hole_edge_ligament'],keepout_edge_gap=r['keepout_to_edge'],
            head_4_5_edge_gap=r['head_4_5_to_edge'],courtyard_keepout_gap=r['actual_courtyard_nearest']['keepout_gap'],
            provisional_body_keepout_gap=r['body_reservation_nearest']['keepout_gap'],
            existing_drill_gap=r['nearest_existing_drill']['proposed_drill_edge_gap'],
            plane_hit=any(z['disk_5mm_hits_existing_fill'] for z in native[r['label']]['zones']))
        for key,group in [('pad','pads'),('track','tracks'),('via','vias')]:
            d[key+'_keepout_gap']=r['groups'][group]['keepout_gap']
            d[key+'_hits']=len(r['groups'][group]['keepout_hits'])
        w.writerow({k:round(v,6) if isinstance(v,float) else v for k,v in d.items()})

prior=json.loads((ROOT/'hardware/kicad/qualification/issue-137-main-manufacturing-review-prep/board-analysis.json').read_text())
old_via_ids={r['uuid'] for r in prior['observations']}
assert prior['board_vias']==66 and len(old_via_ids)==25
affected_uuids={r['uuid'] for r in affected if r['plan']=='A-retain-4'}
assert len(affected_uuids)==3
assert not affected_uuids&old_via_ids
assert {r['net'] for r in affected}=={'VBUS','GND','WING_EN'}
plan_stats={}
for plan,names in plans.items():
    pts=[byname[n]['xy'] for n in names]
    plan_stats[plan]=dict(holes=pts,count=len(pts),outline=[70,78,130,122] if plan.startswith('B') else inv['bounds'],
        affected_existing_items=[r['uuid'] for r in affected if r['plan']==plan],
        affected_old_25_POFV_vias=sorted(affected_uuids&old_via_ids) if plan=='A-retain-4' else [],
        pair_distances_mm=[dict(a=names[i],b=names[j],distance=round(math.dist(pts[i],pts[j]),6)) for i in range(len(pts)) for j in range(i+1,len(pts))])
(E/'plans.json').write_text(json.dumps(plan_stats,indent=2)+'\n')

sources=[measure.PCB,
    'hardware/kicad/qualification/issue-121-full-auto-conditions/evidence/inputs/main-cell1/main.kicad_pro',
    'hardware/kicad/qualification/issue-121-full-auto-conditions/evidence/inspection/main-cell1/krt/independent.json',
    'hardware/kicad/qualification/issue-121-full-auto-conditions/evidence/inspection/main-cell1/krt/router-structured-log.json',
    'hardware/kicad/qualification/issue-137-main-manufacturing-review-prep/board-analysis.json',
    'docs/issue-121-full-auto-conditions.md','docs/issue-137-main-manufacturing-review-prep.md','docs/decisions.md',
    'hardware/rev-m1/main-wing-interface.md','hardware/rev-m1/g0b-freeze-proposal.md',
    'hardware/jitx/wing/generated/representative21-16mm/definition.json',
    'hardware/kicad/qualification/issue-141-wing-power-integrity/runs/KRT-16-2L-P0300/out.kicad_pcb',
    'docs/issue-150-case-stage1.md','hardware/case/issue-150-stage1/measurements.json']
saved_inputs=json.loads((SOURCE/'inputs.json').read_text())
context_paths={'docs/issue-150-case-stage1.md','hardware/case/issue-150-stage1/measurements.json'}
hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() if (ROOT/p).is_file()
        else saved_inputs['files'][p] if p in context_paths else None for p in sources}
assert all(hashes.values()), 'Missing required committed input'
assert hashes[measure.PCB]=='6163ae555a6edf192e52a6dad50721184f3ef9b00f50d468516bf97c545ed2dd'
context_path=ROOT/'docs/issue-150-case-stage1.md'
paragraph=(next(p for p in context_path.read_text().split('\n\n') if p.startswith('**Main 保持**'))
           if context_path.is_file() else saved_inputs['issue150']['main_support_excerpt'])
wing=json.loads((ROOT/sources[10]).read_text())
assert all(h['diameter_mm']==2.2 and h['keepout_diameter_mm']==5 for h in wing['mounting_holes'])
input_record=dict(base_main_commit='f2a6c1388969f42b5a68f8a062fcbcf515b577f2',
    remote_main_verified='git ls-remote origin refs/heads/main: same SHA on 2026-11-05',
    files=hashes,issue150=dict(status='Untracked pre-existing report at task start; preserved and hash-pinned as context. Main dimensions independently reread from committed #121 PCB.',main_support_excerpt=paragraph),
    wing_precedent=dict(path=sources[10],holes=wing['mounting_holes']),
    decisions=dict(D017='GH14 exact pinout; 100mm/14 conductors/1:1; common GND returns and external WING_EN pulldown; final placement remains open in D-017.',
        D019='4 layers F signal/In1 GND/In2 signal/B signal;1.2mm;0.10/0.10mm;vias0.60/0.30mm;KRT',
        D022='POFV for pad vias; same Economic order for J1 SMD plus 4 PTH legs; J1 PTH and NPTH excluded from fill'),
    issue153_scope='Analysis and proposals only; new files only; no PCB edits, routing, ordering, billing, or merge.')
(E/'inputs.json').write_text(json.dumps(input_record,ensure_ascii=False,indent=2)+'\n')

def svg(plan,title,filename):
    bounds=plan_stats[plan]['outline']
    x0,y0,x1,y1=bounds
    s=12
    def point(x,y):return ((x-x0)*s+85,(y-y0)*s+95)
    width=(x1-x0)*s+170
    height=750
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style>text{font-family:Arial,sans-serif;fill:#163044} .small{font-size:11px} .label{font-size:13px;font-weight:bold}</style>',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',f'<text x="25" y="28" font-size="19">{title}</text>',
        '<text x="25" y="50" class="small">Read-only #121 geometry; proposal only. Absolute XY (mm), top view, X right / Y down.</text>']
    def line(a,b,stroke,w,dash=''):
        ax,ay=point(*a);bx,by=point(*b)
        out.append(f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="{stroke}" stroke-width="{w}" {dash}/>')
    def box(b,stroke,fill='none',dash=''):
        ax,ay=point(b[0],b[1]);bx,by=point(b[2],b[3])
        out.append(f'<rect x="{ax}" y="{ay}" width="{bx-ax}" height="{by-ay}" stroke="{stroke}" fill="{fill}" stroke-width="1" {dash}/>')
    box(bounds,'#172e3c','#f4f9f6')
    if plan.startswith('B'):
        box(inv['bounds'],'#526372','none','stroke-dasharray="6 4"')
    for c in inv['board_graphic_courtyards']:
        points=' '.join(f'{point(x,y)[0]},{point(x,y)[1]}' for x,y in c['points'])
        out.append(f'<polygon points="{points}" fill="none" stroke="#a3adb6" stroke-width="0.7"/>')
    for service in data['survey']['services']:
        b=service['box']
        box([max(b[0],x0),max(b[1],y0),min(b[2],x1),min(b[3],y1)],'#819eac','none','stroke-dasharray="3 3"')
    colors={'F.Cu':'#be7c2a','In2.Cu':'#9062b3','B.Cu':'#4684ba'}
    for t in inv['tracks']:
        line(t['a'],t['b'],colors[t['layer']],max(.6,t['width']*s))
    for p in inv['pads']:
        cx,cy=point(*p['xy']);w,h=[v*s for v in p['size']]
        color='#c89242' if p['attribute']!='np_thru_hole' else '#fff'
        if p['shape']=='circle':
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{w/2}" fill="{color}" stroke="#9b752f" stroke-width=".6"/>')
        else:
            rx=min(w,h)/2 if p['shape']=='oval' else 0
            out.append(f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" rx="{rx}" transform="rotate({-p["angle"]},{cx},{cy})" fill="{color}" stroke="#9b752f" stroke-width=".6"/>')
    for v in inv['vias']:
        cx,cy=point(*v['xy'])
        out.append(f'<circle cx="{cx}" cy="{cy}" r="3.6" fill="#d8a556" stroke="#816735" stroke-width=".5"/><circle cx="{cx}" cy="{cy}" r="1.8" fill="white"/>')
    for f in inv['footprints']:
        x,y=point(*f['xy'])
        out.append(f'<text x="{x+3}" y="{y-7}" class="small">{html.escape(f["ref"])}</text>')
    for t in affected:
        if t['plan']==plan:
            line([t['start_x'],t['start_y']],[t['end_x'],t['end_y']],'#d2203d',3)
    for i,name in enumerate(plans[plan],1):
        x,y=byname[name]['xy'];cx,cy=point(x,y)
        out.append(f'<circle cx="{cx}" cy="{cy}" r="30" fill="#3fae7730" stroke="#18764c" stroke-width="1.5" stroke-dasharray="5 3"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="13.2" fill="white" stroke="#18764c" stroke-width="2"/>')
        textx=cx-20 if x>x1-6 else cx+18
        texty=cy+45 if y<y0+6 else cy-35
        anchor='end' if x>x1-6 else 'start'
        out.append(f'<text x="{textx}" y="{texty}" class="label" text-anchor="{anchor}">H{i} ({x:g}, {y:g})</text>')
    # Overall dimensions and coordinate edges.
    line([x0,y0-1.2],[x1,y0-1.2],'#163044',1)
    x,y=point((x0+x1)/2,y0-2)
    out.append(f'<text x="{x}" y="{y}" text-anchor="middle" class="label">{x1-x0:g} mm (X {x0:g} to {x1:g})</text>')
    x,y=point(x0-1.2,(y0+y1)/2)
    out.append(f'<text x="{x-10}" y="{y}" transform="rotate(-90,{x-10},{y})" text-anchor="middle" class="label">44 mm (Y 78 to 122)</text>')
    plane_note = ('In1 GND fill omitted. B holes do not intersect existing copper or saved GND fill; dashed outline = existing 48 x 44 mm.'
                  if plan.startswith('B') else
                  'In1 GND fill omitted. All four A holes intersect the saved GND fill; all-layer keepouts and refill required in Stage 2.')
    out += ['<text x="25" y="665" class="small">Green: proposed NPTH 2.2 / keepout 5.0. Red: existing traces intersecting the proposed keepouts.</text>',
            '<text x="25" y="685" class="small">Orange F.Cu / purple In2.Cu / blue B.Cu. Gray: actual courtyards; dashed boxes: provisional service areas.</text>',
            f'<text x="25" y="705" class="small">{plane_note}</text>',
            '<text x="25" y="725" class="small">Body/height, screw tolerance, insertion load and case fit require Stage 2 verification. No CAD has been changed.</text>','</svg>']
    (E/filename).write_text('\n'.join(out)+'\n')

svg('A-retain-4','A: retain 48 x 44 mm, four nonrectangular mounting holes','retained-outline.svg')
svg('B-extend-4','B: optional 60 x 44 mm, four corner mounting holes','extended-outline.svg')

# Compact lattice map shows options without claiming that the unsampled continuum was proved.
out=['<svg xmlns="http://www.w3.org/2000/svg" width="740" height="700" viewBox="0 0 740 700">',
     '<rect width="740" height="700" fill="white"/><g font-family="Arial,sans-serif" fill="#17334a">',
     '<text x="24" y="30" font-size="19">48 x 44 mm: 0.5 mm mounting-center survey</text>',
     '<text x="24" y="52" font-size="12">3 mm edge setback. Each dot tests a 5 mm disk against pads, tracks, vias and body reservations.</text>']
for p in data['survey']['scan']['points']:
    x=(p['x']-76)*12+80;y=(p['y']-78)*12+85
    color='#2d9364' if p['clear'] else '#de8d46'
    out.append(f'<circle cx="{x}" cy="{y}" r="2.1" fill="{color}"/>')
out.append('<rect x="80" y="85" width="576" height="528" fill="none" stroke="#17334a"/>')
for f in inv['footprints']:
    x=(f['xy'][0]-76)*12+80;y=(f['xy'][1]-78)*12+85
    out.append(f'<text x="{x}" y="{y}" font-size="10">{f["ref"]}</text>')
out += ['<text x="24" y="645" font-size="12">Green = no pad/track/via hit; orange = trace/via hit with body space. Empty = excluded by body screen.</text>',
        '<text x="24" y="665" font-size="12">GND plane excluded: all 15 individually reviewed in-outline candidates intersect saved GND fill.</text>',
        '</g></svg>']
(E/'survey-map.svg').write_text('\n'.join(out)+'\n')
print('CSV, proposal SVGs, lattice map, plans and input provenance generated.')
