"""Round 15 assembly: round 5 fixed operands byte-identical (same
construction as assemble_round14) with the 28 reel wires of the
completed Candidate A (build_reel15). Per pitch: 17mm/ and 16mm/
assembly dirs get assembly.json (with fixed-scope sha256), preview
STEP + render, and the wires STEP.
Usage: assemble_round15.py [17|16|both]
"""
import hashlib, json, sys, time
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round5')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
import build_reel15 as br

def fixed_scope_hash(entries):
    h = hashlib.sha256()
    for e in entries:
        if e['name'].startswith('Wire'): continue
        bb = e['bounds_mm']
        h.update(e['name'].encode()); h.update(e['kind'].encode())
        h.update(json.dumps([[round(v, 4) for v in pt] for pt in bb]).encode())
        h.update(str(round(e['volume_mm3'], 3)).encode())
    return h.hexdigest()

if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'both'
    wires, meta = br.build_all()
    import importlib
    for pitch, mod in ((17, 'build_17mm'), (16, 'build_16mm')):
        if which not in ('both', str(pitch)): continue
        m = importlib.import_module(mod)
        outdir = BASE / f'{pitch}mm'
        t = time.time()
        solids = m.fixed_solids()
        entries = []
        for name, kind, s in solids:
            bb = s.bounding_box()
            entries.append(dict(name=name, kind=kind, volume_mm3=s.volume,
                                bounds_mm=[[bb.min.X, bb.min.Y, bb.min.Z], [bb.max.X, bb.max.Y, bb.max.Z]]))
        shapes = [s for n, k, s in solids]
        names = [n for n, k, s in solids]
        for wn in sorted(wires):
            shapes.append(wires[wn]); names.append(wn)
            bb = wires[wn].bounding_box()
            entries.append(dict(name=wn, kind='harness-wire-reel-r15',
                                volume_mm3=wires[wn].volume,
                                bounds_mm=[[bb.min.X, bb.min.Y, bb.min.Z], [bb.max.X, bb.max.Y, bb.max.Z]]))
        asm = Compound(children=shapes); asm.label = f'issue248-phaseb-{pitch}mm'
        for c, n in zip(asm.children, names): c.label = n
        export_step(asm, outdir / 'preview.step')
        wires_only = Compound(children=[wires[n] for n in sorted(wires)])
        wires_only.label = 'wires'
        for c, n in zip(wires_only.children, sorted(wires)): c.label = n
        export_step(wires_only, outdir / 'wires.step')
        doc = dict(pitch_mm=pitch, candidate='A-reel-round15',
                   fixed_scope_sha256=fixed_scope_hash(entries),
                   solids=len(entries), entries=entries,
                   wire_meta={k: meta[k] for k in sorted(meta)})
        json.dump(doc, open(outdir / 'assembly.json', 'w'), indent=1)
        print(pitch, 'fixed scope sha', doc['fixed_scope_sha256'][:16],
              'entries', len(entries), f'{time.time()-t:.0f}s', flush=True)
    print('done', flush=True)
