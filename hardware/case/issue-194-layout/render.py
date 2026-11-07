"""Draw Phase A review SVG from machine-readable proposals; not a CAM exporter."""
import json
from pathlib import Path
E=Path(__file__).resolve().parent
parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 285 218"><style>text{font-family:monospace;font-size:2px}.title{font-size:3px}</style><rect width="285" height="218" fill="white"/>']
for i,(pitch,side) in enumerate([(16,'left'),(16,'right'),(17,'left'),(17,'right')]):
    d=json.loads((E/f'definition-{pitch}mm-{side}.proposal.json').read_text());ox=72+(i%2)*142;oy=61+(i//2)*108
    def polygon(poly,fill,stroke,width=.15):
        pts=' '.join(f'{ox+x:.4f},{oy-y:.4f}' for x,y in poly)
        parts.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
    def circle(x,y,r,color):
        parts.append(f'<circle cx="{ox+x:.4f}" cy="{oy-y:.4f}" r="{r}" fill="none" stroke="{color}" stroke-width=".15"/>')
    parts.append(f'<text class="title" x="{ox-58}" y="{oy-54}">{pitch}mm {side} / {d["width_mm"]:.1f} x {d["height_mm"]:.1f}</text>')
    polygon(d['outline_mm'],'#f8fafc','#334155',.3)
    for k in d['keys']:
        polygon(k['envelope_mm'],'#dbeafe','#2563eb')
        parts.append(f'<text x="{ox+k["x_mm"]-4:.3f}" y="{oy-k["y_mm"]:.3f}">{k["key"][2:]}</text>')
        for h in k['locator_holes']:circle(h['x_mm'],h['y_mm'],.85,'#64748b')
    for h in d['mounting_holes']:
        circle(h['x_mm'],h['y_mm'],2.5,'#dc2626');circle(h['x_mm'],h['y_mm'],1.1,'#dc2626')
    for s in d['service_reservations']:
        polygon(s['polygon_mm'],'#dcfce7','#15803d',.1)
        c=next(c for c in d['components'] if c['reference']==s['reference'])
        if c['kind'] not in ['testpoint','capacitor']:
            parts.append(f'<text x="{ox+c["x_mm"]-3}" y="{oy-c["y_mm"]}">{c["reference"]}</text>')
parts.append('<text x="8" y="216">Phase A only. Blue: Jade 15.8 square; red: mount keepout; green: service budgets. Not CAM.</text></svg>')
(E/'layout-review.svg').write_text('\n'.join(parts)+'\n')
