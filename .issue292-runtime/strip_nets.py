import sys
sys.path.insert(0, '.')
from sexpr import parse, ser
from pathlib import Path
E = Path('.').resolve()
NETS = {'ADC_C', 'BTN', 'FB_3V3', 'SWDCLK', 'SYS_3V3', 'VBAT_GATE_M', 'VBAT_SENSE'}
src = parse((E/'wmain-routed.kicad_pcb').read_text())
netnames = {}
for c in src[1:]:
    if isinstance(c, list) and c and c[0] == 'net':
        netnames[c[1]] = c[2]
codes = {code for code, nm in netnames.items() if nm in NETS}
removed = 0
out = []
for c in src:
    if isinstance(c, list) and c and c[0] in ('segment', 'via', 'arc'):
        netnode = [x for x in c if isinstance(x, list) and x and x[0] == 'net']
        if netnode and netnode[0][1] in codes:
            removed += 1
            continue
    out.append(c)
(E/'wmain-stripped.kicad_pcb').write_text(ser(out) + '\n')
print('stripped', removed, 'items of nets', sorted(NETS))
