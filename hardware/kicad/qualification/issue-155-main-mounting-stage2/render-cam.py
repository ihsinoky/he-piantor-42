"""Offline contact sheet rendered exclusively from exported CAM files."""
from common import *
import warnings
from gerbonara import GerberFile,ExcellonFile
from PIL import Image,ImageDraw
import cairosvg
dest=E/'manufacturing';work=T/'preview';work.mkdir(exist_ok=True)
names=['gerber/main-stage2-F_Cu.gtl','gerber/main-stage2-In1_Cu.g1','gerber/main-stage2-In2_Cu.g2','gerber/main-stage2-B_Cu.gbl','gerber/main-stage2-F_Mask.gts','gerber/main-stage2-NPTH.drl','gerber/main-stage2-F_Silkscreen.gto','paste/main-stage2-F_Paste.gtp','paste/main-stage2-B_Paste.gbp']
sheet=Image.new('RGB',(1800,1900),'#eeeeee');draw=ImageDraw.Draw(sheet)
draw.text((18,10),'Main Stage 2 | exported CAM | all layers viewed from front | absolute XY, no mirror',fill='black')
with warnings.catch_warnings():
 warnings.simplefilter('ignore')
 for i,name in enumerate(names):
  file=dest/name
  data=ExcellonFile.open(file,plated=False) if file.suffix=='.drl' else GerberFile.open(file)
  svg=str(data.to_svg(force_bounds=((74,-124),(126,-76)),fg='#172f47',bg='white'))
  png=work/(file.name+'.png');cairosvg.svg2png(bytestring=svg.encode(),write_to=str(png),output_width=1100,background_color='white')
  tile=Image.open(png).convert('RGB');tile.thumbnail((580,560));col,row=i%3,i//3
  sheet.paste(tile,(col*600+10,row*620+70));draw.text((col*600+10,row*620+45),file.name,fill='black')
sheet.save(dest/'cam-review.png')
print('Offline CAM contact sheet rendered')
