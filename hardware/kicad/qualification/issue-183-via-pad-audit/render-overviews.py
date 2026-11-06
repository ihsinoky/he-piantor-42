"""Render audit geometry as SVG evidence, without modifying source boards."""
from audit import *
from html import escape
COLORS={'center':'#c72b37','drill-edge':'#ec7619','annulus-only':'#bc9500','none':'#287456'}

def path_data(g):
    rings=[]
    for polygon in g.geoms if hasattr(g,'geoms') else [g]:
        for ring in [polygon.exterior,*polygon.interiors]:
            coords=list(ring.coords);rings.append('M '+' L '.join(f'{x:.6f},{y:.6f}' for x,y in coords)+' Z')
    return ' '.join(rings)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--runtime',type=Path,default=Path('.issue183-runtime'));args=parser.parse_args()
    for source in json.loads((E/'sources.json').read_text()):
        b,pads,tracks,vias,keepouts,npth=load_geometry(source,args.runtime)
        w=E/source['board'];rows=json.loads((w/'all-vias.json').read_text());summary=json.loads((w/'summary.json').read_text())
        ps=p.SHAPE_POLY_SET();assert b.GetBoardPolygonOutlines(ps);board=polygons(ps);x0,y0,x1,y1=board.bounds
        margin=(x1-x0)*.03;font=(x1-x0)*.018;top=font*4;bottom=font*6
        svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0-margin} {y0-top} {x1-x0+2*margin} {y1-y0+top+bottom}" width="1100" role="img" aria-label="{source["board"]} via pad audit">',f'<rect x="{x0-margin}" y="{y0-top}" width="{x1-x0+2*margin}" height="{y1-y0+top+bottom}" fill="white"/>',f'<g font-family="sans-serif" font-size="{font}">',f'<text x="{x0}" y="{y0-font*2}">{source["board"]}: {summary["overlapping_vias"]}/{len(rows)} overlap; {summary["violates_0p10"]} below 0.10mm</text>',f'<text x="{x0}" y="{y0-font*.6}" font-size="{font*.7}">Pads + vias only; traces, zones, mask and paste omitted. Source {source["commit"][:12]}</text>',f'<path d="{path_data(board)}" fill="#fcfcfc" stroke="#333" stroke-width="0.08"/>']
        for a in pads:
            geom=unary_union(list(a['geoms'].values()))
            svg.append(f'<path d="{path_data(geom)}" fill="#c8cbd0" fill-rule="evenodd"><title>{escape(a["ref"]+"."+a["pad"]+" "+a["net"])}</title></path>')
        for ref,pos,size in npth:
            svg.append(f'<circle cx="{pos[0]}" cy="{pos[1]}" r="{size[0]/2}" fill="white" stroke="#333" stroke-width=".06"><title>{escape(ref)} NPTH</title></circle>')
        for r in rows:
            c=COLORS[r['classification']];stroke='#a027aa' if r['classification']=='none' and not r['passes_0p10'] else c
            title=escape(f'{r["uuid"]} ({r["x_mm"]}, {r["y_mm"]}) {r["net"]}; {r["classification"]}; min gap {r["min_annulus_gap_mm"]}mm; {r["nearest_pad"]}')
            svg.append(f'<circle cx="{r["x_mm"]}" cy="{r["y_mm"]}" r="{r["diameter_mm"]/2}" fill="{c}" stroke="{stroke}" stroke-width=".09"><title>{title}</title></circle>')
            svg.append(f'<circle cx="{r["x_mm"]}" cy="{r["y_mm"]}" r="{r["drill_mm"]/2}" fill="white" pointer-events="none"/>')
        legend=[('center',COLORS['center']),('drill-edge',COLORS['drill-edge']),('annulus-only',COLORS['annulus-only']),('none >=0.10mm',COLORS['none']),('none <0.10mm: purple ring','#a027aa')]
        for i,(label,c) in enumerate(legend):
            svg.append(f'<text x="{x0}" y="{y1+font*(i+1)}" fill="{c}" font-size="{font*.8}">{escape(label)}</text>')
        svg.append('</g></svg>');(w/'overview.svg').write_text('\n'.join(svg)+'\n')
        print(source['board'],'overview saved')
