import subprocess
from pathlib import Path
E = Path(__file__).resolve().parent
KRT = Path('/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools')
PY = '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3'
nets = ['ADC_A', 'ADC_B', 'ADC_C', 'ANT_LINK', 'HALL_3V3', 'HALL_PWR_EN', 'LED_DRV',
        'MUX_A0', 'MUX_A1', 'MUX_A2', 'MUX_EN0', 'MUX_EN1', 'MUX_OUT_A', 'MUX_OUT_B',
        'MUX_OUT_C', 'PAD_3V3', 'PAD_DR', 'PAD_SDA', 'RESET_N', 'SYS_3V3', 'USB_DM',
        'USB_DP', 'VBAT+', 'VBAT_GATE', 'VBAT_GATE_M', 'VBAT_SENSE', 'VBUS', 'VIN_IN']
cmd = [PY, str(KRT/'py_router/route.py'), str(E/'wmain-v13.kicad_pcb'), str(E/'wmain-v13-routed.kicad_pcb'),
       '--nets'] + nets + [
       '--track-width', '0.1', '--power-nets', 'HALL_3V3', 'SYS_3V3', 'VIN_IN', 'VBUS', 'VBAT+',
       '--power-nets-widths', '0.3', '0.3', '0.3', '0.3', '0.3', '--clearance', '0.1', '--via-size', '0.6', '--via-drill', '0.3',
       '--same-net-pad-clearance', '0.15', '--escalation', 'board',
       '--layers', 'F.Cu', 'In2.Cu', 'B.Cu']
with open(E/'krt-v13.log', 'w') as lf:
    r = subprocess.run(cmd, cwd=KRT, stdout=lf, stderr=subprocess.STDOUT, timeout=3000)
print('exit', r.returncode)
