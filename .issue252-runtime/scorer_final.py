import json, sys, time
sys.path.insert(0, '.')
import fitlib252 as C
import fitlib18 as F
import repair252 as RP  # fast-bounds patch (conservative boxes; verdict unchanged)
D = json.load(open('design_state.json'))
bodies = C.all_bodies()
wires, lens, failed = C.build_all(D)
solids = {n: r[0] for n, r in wires.items()}
sc = F.Scorer(solids, bodies)
ww = sc.ww_pairs()
wf = {p: sc.wf_pairs(p) for p in bodies}
out = {'ww_count': len(ww), 'wf_17': len(wf[17]), 'wf_16': len(wf[16]),
       'gate1_17': len(ww) + len(wf[17]), 'gate1_16': len(ww) + len(wf[16])}
print(out, flush=True)
json.dump({'ww': ww, 'wf': {str(p): wf[p] for p in wf}, **out}, open('scorer_final.json', 'w'), indent=1)
