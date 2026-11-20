"""Fix round KRT pass 3: the 10 still-broken U1 nets, ripping the 15
pass-1 nets' copper (re-routed in the same run) per KRT's own hint."""
import subprocess
from pathlib import Path
E = Path(__file__).resolve().parent
KRT = Path('/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools')
PY = '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3'
NETS = ['MUX_A0', 'MUX_A2', 'RESET_N', 'MUX_EN0', 'MUX_EN1', 'SYS_3V3', 'VBAT_GATE_M', 'PAD_EN', 'PAD_DR', 'LED_DRV']
RIP = ['ADC_A', 'ADC_B', 'ADC_C', 'ANT_LINK', 'BTN', 'HALL_PWR_EN', 'LED_DRV', 'MUX_A1', 'PAD_SCL', 'PAD_SDA', 'SWDCLK', 'SWDIO', 'USB_DM', 'USB_DP', 'VBUS', 'HALL_PWR_EN']
RIP = ['ADC_A', 'ADC_B', 'ADC_C', 'ANT_LINK', 'BTN', 'HALL_PWR_EN', 'MUX_A1', 'PAD_SCL', 'PAD_SDA', 'SWDCLK', 'SWDIO', 'USB_DM', 'USB_DP', 'VBUS']
cmd = [PY, str(KRT/'py_router/route.py'), str(E/'wmain-v28b-filled.kicad_pcb'), str(E/'wmain-v28c.kicad_pcb'),
       '--nets', *NETS,
       '--rip-existing-nets', *RIP,
       '--track-width', '0.1',
       '--power-nets', 'SYS_3V3', '--power-nets-widths', '0.3',
       '--clearance', '0.1', '--via-size', '0.6', '--via-drill', '0.3',
       '--same-net-pad-clearance', '0.15', '--escalation', 'board',
       '--layers', 'F.Cu', 'In2.Cu', 'B.Cu']
with open(E/'krt-v28c.log', 'w') as lf:
    r = subprocess.run(cmd, cwd=KRT, stdout=lf, stderr=subprocess.STDOUT, timeout=5400)
print('exit', r.returncode)
