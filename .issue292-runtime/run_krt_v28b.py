"""Fix round: re-route the 25 non-GND U1 nets severed by the official
footprint swap, with the same KRT parameters as the layout run."""
import subprocess
from pathlib import Path
E = Path(__file__).resolve().parent
KRT = Path('/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools')
PY = '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3'
NETS = ['PAD_SCL', 'MUX_A0', 'MUX_A2', 'RESET_N', 'HALL_PWR_EN', 'MUX_EN0', 'MUX_EN1', 'SYS_3V3', 'VBAT_GATE_M', 'PAD_EN', 'BTN', 'PAD_DR', 'LED_DRV']
POWER = ['SYS_3V3', 'VBUS']
cmd = [PY, str(KRT/'py_router/route.py'), str(E/'wmain-v28-filled.kicad_pcb'), str(E/'wmain-v28b.kicad_pcb'),
       '--nets', *NETS,
       '--track-width', '0.1',
       '--power-nets', *POWER, '--power-nets-widths', '0.3', '0.3',
       '--clearance', '0.1', '--via-size', '0.6', '--via-drill', '0.3',
       '--same-net-pad-clearance', '0.15', '--escalation', 'board',
       '--layers', 'F.Cu', 'In2.Cu', 'B.Cu']
with open(E/'krt-v28b.log', 'w') as lf:
    r = subprocess.run(cmd, cwd=KRT, stdout=lf, stderr=subprocess.STDOUT, timeout=5400)
print('exit', r.returncode)
