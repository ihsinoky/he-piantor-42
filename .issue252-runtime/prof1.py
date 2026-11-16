import cProfile, json, pstats, sys
sys.path.insert(0, '.')
import fitlib252 as C
import repair252 as RP
D = json.load(open('design_seed.json'))
bodies = C.all_bodies()
rp = RP.SegRepair.__new__(RP.SegRepair)
rp.D = D; rp.bodies = bodies
rp.body_bnd = {p: {n: C.F.bounds(s) for n, s in bl} for p, bl in bodies.items()}
rp.wires = {}; rp.wb = {}
rp._build_all()
print('built', flush=True)
pr = cProfile.Profile(); pr.enable()
c = rp.eval_unit('SegW', 0, rp._cand_of('SegW', 0))
pr.disable()
print('eval SegW1:', c, flush=True)
pstats.Stats(pr).sort_stats('cumulative').print_stats(12)
