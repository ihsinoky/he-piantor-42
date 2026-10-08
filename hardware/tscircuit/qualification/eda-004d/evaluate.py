"""One pre-route boundary evaluation group, raw saved before acceptance decision."""
from process import *
import shutil
BASE=Path(os.environ.get('EDA004D_WORK_DIR', '/tmp/eda004d'));PRIOR=ROOT.parent/'eda-004c'
raw=PRIOR/'evidence/processes/smoke-generation-corrected/smoke.circuit.json'
shutil.copyfile(ROOT/'test-patch.mjs',BASE/'runtime/test-patch.mjs')
run('patch-unit-tests',['node',str(BASE/'runtime/test-patch.mjs'),str(raw)],BASE/'runtime',180)
run('patched-smoke-conversion',['node',str(BASE/'runtime/convert.mjs'),str(raw),str(BASE/'smoke')],BASE/'runtime',120,
 artifacts=[('smoke.'+ext,BASE/('smoke.'+ext)) for ext in ['kicad_pcb','kicad_sch','kicad_pro']])
# Boundary group captures all read-only reports before its content decision.
# Libraries are explicitly unconfigured at this assessment: this cannot PASS.
env=json.loads((EVIDENCE/'kicad-env.json').read_text())
run('kicad-inventory',['/usr/bin/python3',str(PRIOR/'inspect-board.py'),
 str(BASE/'smoke.kicad_pcb'),str(BASE/'board-inventory.json')],BASE,env=env,
 artifacts=[('board-inventory.json',BASE/'board-inventory.json')])
cli=str(BASE/'kicad/usr/bin/kicad-cli')
run('kicad-pre-route-drc',[cli,'pcb','drc','--format','json','--output',str(BASE/'pre-route-drc.json'),
 str(BASE/'smoke.kicad_pcb')],BASE,env=env,artifacts=[('pre-route-drc.json',BASE/'pre-route-drc.json')])
run('kicad-synthetic-erc',[cli,'sch','erc','--format','json','--output',str(BASE/'synthetic-erc.json'),
 str(BASE/'smoke.kicad_sch')],BASE,env=env,artifacts=[('synthetic-erc.json',BASE/'synthetic-erc.json')])
