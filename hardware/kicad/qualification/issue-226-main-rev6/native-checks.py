"""Fresh native DRC, ERC and independent object snapshot; inherited schematic unchanged."""
from common import *
import shutil
V=E.parent/'issue-221-main-rev5';W=E/'inspection/final';S=E/'schematic';S.mkdir(exist_ok=True)
for name in ['main.kicad_sch','main.kicad_pro','review.kicad_sym','sym-lib-table','main.net.xml']:
 shutil.copyfile(V/'schematic'/name,S/name)
(S/'fp-lib-table').write_text((V/'schematic/fp-lib-table').read_text().replace('${KIPRJMOD}/../Rev5.pretty','${KIPRJMOD}/../../issue-221-main-rev5/Rev5.pretty'))
cli=B/'kicad/usr/bin/kicad-cli'
assert run('snapshot',[sys.executable,R/'hardware/kicad/qualification/eda-004g/resume-02/read-pcb.py',W/'main.kicad_pcb',W/'snapshot.json'])==0
assert run('native-drc',[cli,'pcb','drc','--format','json','--severity-all','--exit-code-violations','-o',W/'drc.json',W/'main.kicad_pcb'])==0
assert run('native-erc',[cli,'sch','erc','--format','json','--severity-all','--exit-code-violations','-o',S/'erc-final.json',S/'main.kicad_sch'])==0
