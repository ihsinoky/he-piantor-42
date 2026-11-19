#!/usr/bin/env python3
"""Issue #278: build the flipped fitted body set ONCE and cache every
body as a STEP file under bodies_cache/ (restart-resilient)."""
import sys, os, json, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route_audit as RA
from build123d import export_step

RT = RA.RT
CACHE = os.path.join(RT, 'bodies_cache')

def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

def main():
    os.makedirs(CACHE, exist_ok=True)
    log("building bodies (pocket A only)")
    bodies, sheets = RA.build_bodies()
    manifest = {}
    for n, s in bodies.items():
        fn = re.sub(r'[^A-Za-z0-9_.-]', '_', n) + '.step'
        export_step(s, os.path.join(CACHE, fn))
        manifest[n] = fn
    json.dump(manifest, open(os.path.join(CACHE, 'manifest.json'), 'w'), indent=1)
    log(f"cached {len(manifest)} bodies")

if __name__ == '__main__':
    main()
