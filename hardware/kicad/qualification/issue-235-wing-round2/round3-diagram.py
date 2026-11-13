"""Native-copper local illustration; gates use the saved PCB, not this view."""
from pathlib import Path
import html
import pcbnew as p
from verify import xy, polys, padgeom
from shapely.geometry import box

E=Path(__file__).resolve().parent
W=E/'wing-rev4-16mm-left'
b=p.LoadBoard(str(W/'main.kicad_pcb'))
out=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="650" viewBox="0 0 14 8.3">',
     '<rect width="14" height="8.3" fill="white"/>',
     '<text x=".3" y=".4" font-size=".25">16L round 3: native mm; red HALL_5V, blue signals, gray GND</text>']
for l,offset in [(p.F_Cu,.3),(p.B_Cu,7.3)]:
    out.append(f'<text x="{offset}" y=".9" font-size=".25">{b.GetLayerName(l)}</text>')
    out.append(f'<svg x="{offset}" y="1.1" width="6.4" height="6.6" viewBox="127.8 37.3 6.4 6.6">')
    def draw(g, color, opacity=1):
        g=g.intersection(box(127.8,37.3,134.2,43.9))
        if g.is_empty:return
        out.append(g.svg(fill_color=color, opacity=opacity).replace('stroke-width="2.0"','stroke-width="0"'))
    for z in b.Zones():
        if z.IsOnLayer(l) and not z.GetIsRuleArea():draw(polys(z.GetFilledPolysList(l)), '#d4ead4')
    for t in b.GetTracks():
        if not t.IsOnLayer(l):continue
        color='#c22' if t.GetNetname()=='HALL_5V' else '#888' if t.GetNetname()=='GND' else '#2782b0'
        if isinstance(t,p.PCB_VIA):
            x,y=xy(t.GetPosition())
            out.append(f'<circle cx="{x}" cy="{y}" r=".3" fill="{color}"/><circle cx="{x}" cy="{y}" r=".15" fill="white"/>')
        else:
            a,z=xy(t.GetStart()),xy(t.GetEnd())
            out.append(f'<path d="M{a[0]},{a[1]} L{z[0]},{z[1]}" stroke="{color}" stroke-width="{p.ToMM(t.GetWidth())}" fill="none"/>')
    for f in b.GetFootprints():
        for a in f.Pads():
            if not a.IsOnLayer(l):continue
            ident=f.GetReference()+'.'+a.GetNumber()
            draw(padgeom(a,l),'#c22' if ident=='U_MUX_C.13' else '#bd8b9a')
            x,y=xy(a.GetPosition())
            if f.GetReference()=='U_MUX_C':
                out.append(f'<text x="{x}" y="{y}" font-size=".16">{html.escape(a.GetNumber())}</text>')
    out.append('</svg>')
out.append('<text x=".3" y="8.05" font-size=".2">MUX_A1 via: (129.4,41.2); H_C6 via: (130.95,42.47). All footprints fixed.</text></svg>')
(W/'round3/local-closure.svg').write_text('\n'.join(out)+'\n')
