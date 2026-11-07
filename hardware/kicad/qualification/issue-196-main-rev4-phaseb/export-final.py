"""Export only independently qualified, refilled final board with original project rules."""
from common import *
import shutil
w=E/'inspection/final';dest=E/'manufacturing';dest.mkdir(exist_ok=True)
assert json.loads((w/'assessment.json').read_text())['pass_acceptance']
assert (E/'assembly-review.json').exists()
work=T/('export196-'+digest(w/'main.kicad_pcb')[:12]);work.mkdir(exist_ok=False)
pcb=work/'main-rev4.kicad_pcb'
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(w/('main.'+ext),pcb.with_suffix('.'+ext))
before=digest(pcb);cli=B/'kicad/usr/bin/kicad-cli';fab=dest/'gerber';paste=dest/'paste';fab.mkdir();paste.mkdir()
assert run('release-gerbers',[cli,'pcb','export','gerbers','--layers','F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts','--precision','6','--subtract-soldermask','-o',str(fab)+'/',pcb])==0
assert run('release-drill',[cli,'pcb','export','drill','--format','excellon','--drill-origin','absolute','--excellon-units','mm','--excellon-zeros-format','decimal','--excellon-oval-format','alternate','--excellon-separate-th','--generate-report','--report-path',dest/'drill-report.txt','-o',str(fab)+'/',pcb])==0
assert run('release-paste',[cli,'pcb','export','gerbers','--layers','F.Paste,B.Paste','--precision','6','-o',str(paste)+'/',pcb])==0
assert run('release-native-pos',[cli,'pcb','export','pos','--format','csv','--units','mm','--side','front','-o',dest/'native-pos-absolute.csv',pcb])==0
assert digest(pcb)==before==digest(w/'main.kicad_pcb')
save(E/'export-provenance.json',dict(utc=now(),board='inspection/final/main.kicad_pcb',board_sha256=before,project='inspection/final/main.kicad_pro',project_sha256=digest(w/'main.kicad_pro'),original_input_project_byte_identical=digest(w/'main.kicad_pro')==digest(E.parent/'issue-175-main-dual-wing-final2/inputs/final/main.kicad_pro'),gerber_drill_origin_absolute=True,gerber_resolution_mm=.000001,drill_resolution_mm=.001,pth_npth_separated=True,cpl_origin_absolute_xy_mm=[62.107317799,137.9],paste='Faithful original openings; no stencil optimization applied; Review required for stencil and TP paste; no via overlaps pad copper under Issue183 audit',manufacturing_release=False))
print('Qualified final manufacturing exports complete; source bytes unchanged')
