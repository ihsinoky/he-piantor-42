"""Offline review plates: explicit white PNG background, no SVG filter effects.

Only Gerbonara-parsed Gerber/Excellon objects are drawn. This avoids Cairo's
unsupported pretty-SVG filters and transparent PNG converted to black RGB.
Output coordinates for both copper composites are viewed from the front.
"""
import json
import warnings
from pathlib import Path
import cairosvg
from gerbonara import GerberFile, ExcellonFile, LayerStack
from PIL import Image, ImageDraw
from common import E

for pitch in (16,17):
    d=E/f'{pitch}mm'
    pre=json.loads((d/'preflight.json').read_text())
    xmin,ymin,xmax,ymax=pre['outline_bounds_mm']
    bounds=((xmin-2,-ymax-2),(xmax+2,-ymin+2))
    fab=d/'gerber'
    dest=d/'preview-review'
    dest.mkdir(exist_ok=False)
    panels=[]
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        stack=LayerStack.open(fab)
        for f in sorted(fab.iterdir()):
            if f.suffix=='.gbrjob':continue
            data=ExcellonFile.open(f,plated='NPTH' not in f.name) if f.suffix=='.drl' else GerberFile.open(f)
            svg=str(data.to_svg(force_bounds=bounds,fg='#142d4e',bg='white'))
            (dest/(f.stem+'.svg')).write_text(svg)
            png=dest/(f.stem+'.png')
            cairosvg.svg2png(bytestring=svg.encode(),write_to=str(png),output_width=1800,background_color='white')
            panels.append((f.name,png))
        silk=GerberFile.open(next(fab.glob('*.gto')))
        svg=str(silk.to_svg(force_bounds=bounds,fg='#142d4e',bg='white'))
        (dest/'front-silkscreen.svg').write_text(svg)
        cairosvg.svg2png(bytestring=svg.encode(),write_to=str(dest/'front-silkscreen.png'),output_width=2600,background_color='white')
        for side in ('top','bottom'):
            colors={f'{side} copper':'#b26100','mechanical outline':'#161616',
                    'drill pth':'#1177bb','drill npth':'#1177bb'}
            svg=str(stack.to_svg(side_re=f'{side}|mechanical',force_bounds=bounds,colors=colors))
            (dest/f'{side}-copper-holes.svg').write_text(svg)
            cairosvg.svg2png(bytestring=svg.encode(),write_to=str(dest/f'{side}-copper-holes.png'),
                            output_width=2200,background_color='white')
    sheet=Image.new('RGB',(1800,1830),'#e8e8e8')
    draw=ImageDraw.Draw(sheet)
    draw.text((15,10),f'Wing {pitch}mm | offline Gerber / Excellon viewer | white background | front-view coordinates',fill='black')
    for i,(name,png) in enumerate(panels):
        col,row=i%3,i//3
        tile=Image.open(png).convert('RGB')
        tile.thumbnail((580,550))
        sheet.paste(tile,(col*600+10,row*600+65))
        draw.text((col*600+10,row*600+43),name,fill='black')
    sheet.save(dest/'all-layers.png')
print('High-contrast, filter-free review plates written for both pitches.')
