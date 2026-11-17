"""Issue 264 fitted audit v3 — fused right cable (healthy) + build123d
mirror for the left cable/channel (v1's left fuse chain produced a
malformed solid; mirroring a finished solid is a pure transform).
Gate 1 machinery identical to #261 audit_static (repaired vol_pair)."""
import json, sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime')
import build_audit264 as B1
import fitlibF as FF
import fitlib18 as F
import repair18_lib as R
from build123d import mirror, Plane, Compound, export_step

RT = '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime'

def assemble_v3(s1_dy=0.0, w=9.6, t=0.32, patch_th=0.30):
    zifs = B1.make_zifs()
    bodies = [(n, s) for n, s in FF.bodies_at(17, -2.65)
              if n not in ('Main-GH-left-DRAWING-BOUND', 'Main-GH-right-DRAWING-BOUND')]
    bodies += list(zifs.items())
    chan_r = B1.build_channel(w, t, patch_th, s1_dy, sx=1)
    chan_l = mirror(chan_r, about=Plane.YZ)
    out = []
    for n, s in bodies:
        if n == 'tray-right': s = s.cut(chan_r)
        elif n == 'tray-left': s = s.cut(chan_l)
        out.append((n, s))
    cable_r = B1.build_cable(w, t, patch_th, s1_dy, sx=1)
    cable_l = mirror(cable_r, about=Plane.YZ)
    print('cable vols R/L:', round(cable_r.volume, 1), round(cable_l.volume, 1), flush=True)
    return out, cable_r, cable_l, zifs

if __name__ == '__main__':
    res = {}
    for tag, kw in (('base', {}), ('sensN', dict(s1_dy=2.0, w=10.4, patch_th=0.35)),
                    ('sensS', dict(s1_dy=-2.6, w=10.4, patch_th=0.35))):
        bodies, cable_r, cable_l, zifs = assemble_v3(**kw)
        res[f'gate1_{tag}_right'] = B1.audit('cable_r', cable_r, bodies)
        print(f'{tag} right hits:', res[f'gate1_{tag}_right'], flush=True)
        res[f'gate1_{tag}_left'] = B1.audit('cable_l', cable_l, bodies)
        print(f'{tag} left hits:', res[f'gate1_{tag}_left'], flush=True)
        if tag == 'base':
            res['cable_vs_cable'] = float(R.vol_pair(cable_r, cable_l, F.bounds(cable_r), F.bounds(cable_l), repair=True))
            print('cable_vs_cable:', res['cable_vs_cable'], flush=True)
            export_step(Compound(children=[cable_r, cable_l] + list(zifs.values())), f'{RT}/preview264.step')
    json.dump(res, open(f'{RT}/audit264_v3.json', 'w'), indent=1)
    print('DONE', flush=True)
