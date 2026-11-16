"""Classify incumbent (round-18/frontier z1355) WF+WW hits by body and
Common centroid, to map which zones candidate C inherits."""
import json, sys, time
import numpy as np
PB = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
RT = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/frontier'
sys.path.insert(0, PB); sys.path.insert(0, f'{PB}/sources/frontier'); sys.path.insert(0, PB + '/sources/round18')
import fitlibF as FF
import fitlib18 as F
import audit_repair as ar
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

T0 = time.time()
def log(*a): print(round(time.time() - T0, 1), *a, flush=True)

def centroid(shape):
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props, True, False, False)
    c = props.CentreOfMass()
    return [round(c.X(), 2), round(c.Y(), 2), round(c.Z(), 2)]

FF.set_height(0.0)
state = json.load(open(f'{RT}/state_z1355.json'))
M = state['M']
bodies = {p: FF.bodies_at(p, 0.0) for p in (17, 16)}
wires, lens, failed = F.build_all(M)
log('built', len(wires), 'failed', failed)
sc = FF.Scorer(wires, bodies)
out = {'wf': {}, 'ww': {}}
for p in (17, 16):
    hits = []
    for wn, w in wires.items():
        for bn, bs in bodies[p]:
            v = sc._vol(w, bs, sc.wb[wn], sc.bb[p][bn])
            if v > F.HIT:
                cs = ar.common_shape(w, bs)
                hits.append({'wire': wn, 'body': bn, 'vol': round(v, 3),
                             'centroid': None if cs.IsNull() else centroid(cs)})
    out['wf'][str(p)] = hits
    log('pitch', p, 'wf hits', len(hits))
ww = sc.ww_pairs()
wwd = []
for k, v in ww.items():
    na, nb = k.split('x')
    cs = ar.common_shape(wires[na], wires[nb])
    wwd.append({'pair': k, 'vol': v, 'centroid': None if cs.IsNull() else centroid(cs)})
out['ww'] = wwd
log('ww', len(wwd))
json.dump(out, open('/home/hatch/workspace/projects/he-piantor-midconn/.issue252-runtime/incumbent_hits.json', 'w'), indent=1)
log('DONE')
