import sys
step = sys.argv[1]
import pcbnew as p
print('import ok', p.GetBuildVersion(), flush=True)
b = p.BOARD(); print('board ok', flush=True)
if step == '1': sys.exit(0)
b.SetCopperLayerCount(2); print('layers ok', flush=True)
if step == '2': sys.exit(0)
n = p.NETINFO_ITEM(b, 'TEST'); b.Add(n); print('net ok', flush=True)
if step == '3': sys.exit(0)
E = '/home/hatch/workspace/projects/he-piantor-midconn/hardware/kicad/qualification/issue-252-carrier'
f = p.FootprintLoad(f'{E}/connector/Carrier.pretty', 'JST_GH_SM14B-GHS-TB_1x14-1MP_P1.25mm_Horizontal')
print('fp loaded', f is not None, flush=True)
if step == '4': sys.exit(0)
f.SetPosition(p.VECTOR2I(p.FromMM(0), p.FromMM(0))); b.Add(f); print('placed ok', flush=True)
p.SaveBoard('/home/hatch/workspace/projects/he-piantor-midconn/.issue252-runtime/probe.kicad_pcb', b)
print('saved ok', flush=True)
