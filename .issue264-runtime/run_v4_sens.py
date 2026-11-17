import json, sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime')
import build_audit264_v4 as V4
res = {}
for tag, kw in (('sensN', dict(s1_dy=2.0, w=10.4, patch_th=0.35)),
                ('sensS', dict(s1_dy=-2.6, w=10.4, patch_th=0.35))):
    bodies, cable_r, cable_l, zifs = V4.assemble_v4(**kw)
    for side, cable in (('right', cable_r), ('left', cable_l)):
        h, o = V4.audit_classified(f'cable_{side}', cable, bodies)
        res[f'gate1_{tag}_{side}'] = h
        res[f'ownterm_{tag}_{side}'] = o
        print(f'{tag} {side}: gate1={h} own-termination={o}', flush=True)
json.dump(res, open('/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime/audit264_v4b.json', 'w'), indent=1)
print('DONE', flush=True)
