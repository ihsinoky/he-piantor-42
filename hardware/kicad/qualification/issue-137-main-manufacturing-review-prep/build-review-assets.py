"""Derive CSV and an SVG geometry figure from the captured, read-only analysis."""
import csv
import html
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
j=json.loads((BASE/'board-analysis.json').read_text())
cross=json.loads((BASE/'geometry-crosscheck.json').read_text())
rows=[]
for r,c in zip(j['observations'],cross['rows']):
    p=r['copper_pad_hits'][0]
    category=('test-pad-hole' if p['ref'].startswith('TP') else
        'component-pad-center' if p['via_center_in_pad'] else
        'component-pad-edge-hole' if p['drill_overlaps_pad'] else 'component-pad-annulus-only')
    rows.append(dict(log_index=r['log_index'], log_site=r['log_site'], x_mm=r['position_mm'][0],y_mm=r['position_mm'][1],
        net=r['net'], ref=p['ref'], pad=p['pad'],category=category,
        center_in_pad=p['via_center_in_pad'],drill_overlaps_pad=p['drill_overlaps_pad'],
        paste_graphics=len(r['paste_graphic_hits']),drill_overlaps_paste=c['drill_overlaps_paste'],
        via_uuid=r['uuid'],pad_uuid=p['uuid'],
        paste_uuid=';'.join(g['uuid'] for g in r['paste_graphic_hits'])))
with (BASE/'via-observations.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1140" height="420" viewBox="0 0 1140 420">',
    '<rect width="1140" height="420" fill="#fff"/>',
    '<style>text{font:14px sans-serif;fill:#18202b}.title{font:bold 17px sans-serif}.small{font:12px sans-serif}</style>',
    '<text x="20" y="26" class="title">Issue #137: measured via / copper / paste geometry (top view, board Y down)</text>',
    '<text x="20" y="49">Orange: pad copper; green outline: paste opening; blue: via copper; white: drilled hole. Nominal dimensions.</text>']
for i,index in enumerate([1,4,10,16,20]):
    r=j['observations'][index-1];p=r['copper_pad_hits'][0]
    center=p['position_mm']; w,h=p['size_mm']
    if p['orientation_deg']%180==90: w,h=h,w
    vx,vy=r['position_mm'];px,py=center
    lo_x=min(px-w/2,vx-.3)-.1;hi_x=max(px+w/2,vx+.3)+.1
    lo_y=min(py-h/2,vy-.3)-.1;hi_y=max(py+h/2,vy+.3)+.1
    scale=min(170/(hi_x-lo_x),220/(hi_y-lo_y))
    ox=20+i*225+(190-(hi_x-lo_x)*scale)/2-lo_x*scale
    oy=105+(220-(hi_y-lo_y)*scale)/2-lo_y*scale
    def rect(x,y,w,h,style):
        return f'<rect x="{ox+(x-w/2)*scale:.3f}" y="{oy+(y-h/2)*scale:.3f}" width="{w*scale:.3f}" height="{h*scale:.3f}" {style}/>'
    def circ(x,y,r,style):
        return f'<circle cx="{ox+x*scale:.3f}" cy="{oy+y*scale:.3f}" r="{r*scale:.3f}" {style}/>'
    svg.append(f'<text x="{20+i*225}" y="87" class="title">#{index} {p["ref"]}.{p["pad"]}</text>')
    svg.append(circ(px,py,w/2,'fill="#efb563"') if p['shape']==0 else rect(px,py,w,h,'fill="#efb563"'))
    svg.append(circ(vx,vy,.3,'fill="#3f83db" fill-opacity="0.6" stroke="#165aaa"'))
    for g in r['paste_graphic_hits']:
        if g['shape']==3:
            gx,gy=g['center_mm'];rad=((g['end_mm'][0]-gx)**2+(g['end_mm'][1]-gy)**2)**.5
            svg.append(circ(gx,gy,rad,'fill="none" stroke="#137e3c" stroke-width="2"'))
        else:
            a,b=g['start_mm'],g['end_mm']
            svg.append(rect((a[0]+b[0])/2,(a[1]+b[1])/2,abs(a[0]-b[0]),abs(a[1]-b[1]),'fill="none" stroke="#137e3c" stroke-width="2"'))
    # For C5 show its non-intersecting paste opening too (0.7 shrink of copper).
    if index==10: svg.append(rect(px,py,w*.7,h*.7,'fill="none" stroke="#137e3c" stroke-width="2"'))
    svg.append(circ(vx,vy,.15,'fill="white" stroke="#165aaa"'))
    c=cross['rows'][index-1]
    desc=['Center inside pad','Hole crosses pad edge','Annulus only; hole outside','Hole crosses copper, not paste','Bare test pad, no component'][i]
    svg.append(f'<text x="{20+i*225}" y="355" class="small">{html.escape(desc)}</text>')
    svg.append(f'<text x="{20+i*225}" y="376" class="small">Via: ({vx}, {vy}) mm</text>')
svg.append('<text x="20" y="408" class="small">Individual panels auto-scaled. Via OD 0.60 mm / drill 0.30 mm. Figure is review evidence, not an order drawing.</text></svg>')
(BASE/'geometry-cases.svg').write_text('\n'.join(svg)+'\n')
print(json.dumps(dict(csv_rows=len(rows),categories={k:sum(r['category']==k for r in rows) for k in sorted({r['category'] for r in rows})}),indent=2))
