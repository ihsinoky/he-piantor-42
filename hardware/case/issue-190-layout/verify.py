#!/usr/bin/env python3
"""Read-only checks of geometry proposals; optionally verify downloaded source PCBs."""
import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--upstream-dir', type=Path, help='Directory containing cantor.kicad_pcb and piantor.kicad_pcb')
args=parser.parse_args()
subprocess.run([sys.executable,str(HERE/'analyze.py'),'--check'],check=True,stdout=sys.stderr)
hashes=json.loads((HERE/'input-hashes.json').read_text())
for path,sha in hashes.items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
raw_status='not requested; committed extraction only'
if args.upstream_dir:
    for record in json.loads((HERE/'inputs/upstream.json').read_text()):
        name=record['repository'].split('/')[1]
        raw=(args.upstream_dir/f'{name}.kicad_pcb').read_bytes()
        assert hashlib.sha256(raw).hexdigest()==record['sha256']
        # Isolate balanced footprint expressions; avoid relying on line splitting.
        text=raw.decode();found={}
        for match in re.finditer(r'\(footprint\s',text):
            start=match.start();depth=0;quote=False;escape=False;end=None
            for i in range(start,len(text)):
                c=text[i]
                if escape:escape=False;continue
                if c=='\\' and quote:escape=True;continue
                if c=='"':quote=not quote;continue
                if quote:continue
                if c=='(':depth+=1
                elif c==')':
                    depth-=1
                    if depth==0:end=i+1;break
            assert end
            block=text[start:end]
            ref=re.search(r'\(fp_text reference "(K\d\d)"',block)
            if ref:
                at=list(map(float,re.search(r'\(at ([^)]*)\)',block).group(1).split()))
                found[ref[1]]=at[:2]+[at[2] if len(at)>2 else 0]
        expected={r['source_key']:[float(r[x]) for x in ('source_x_mm','source_y_mm','source_rotation_deg')] for r in csv.DictReader((HERE/f'inputs/{name}-extracted.csv').open())}
        assert found==expected,name
    raw_status='both pinned PCB hashes and all 21 centers/angles independently verified'
for p in (16,17):
    target=ROOT/f'hardware/jitx/wing/generated/representative21-{p}mm'
    d=json.loads((target/'definition.json').read_text())
    proposal=json.loads((HERE/f'definition-{p}mm.proposal.json').read_text())
    for op in proposal['geometry_patch']:
        assert op['op']=='replace'
        tokens=op['path'].strip('/').split('/');node=d
        for token in tokens[:-1]:node=node[int(token)] if isinstance(node,list) else node[token]
        last=int(tokens[-1]) if isinstance(node,list) else tokens[-1]
        assert last<len(node) if isinstance(node,list) else last in node
        node[last]=op['value']
    coords={r['key']:r for r in csv.DictReader((HERE/f'coordinates-{p}mm.csv').open())}
    comps={c['reference']:c for c in d['components']}
    for sensor in d['sensor_sites']:
        r=coords[sensor['source_key_id']];c=comps[sensor['reference']]
        for axis in ('x_mm','y_mm'):
            assert math.isclose(sensor[axis],float(r[axis]),abs_tol=1e-8)
            assert math.isclose(c[axis],sensor[axis],abs_tol=1e-8)
    moves=list(csv.DictReader((HERE/f'placements-{p}mm.proposal.csv').open()))
    assert len(moves)==45
    for r in moves:
        for axis in ('x_mm','y_mm'):
            assert math.isclose(comps[r['reference']][axis],float(r['proposed_'+axis]),abs_tol=1e-8)
    # All unmoved references really retain their original placement.
    original={c['reference']:c for c in json.loads((target/'definition.json').read_text())['components']}
    moved={r['reference'] for r in moves}
    for ref,c in comps.items():
        if ref not in moved:assert c==original[ref]
    keys=list(csv.DictReader((HERE/f'keys-{p}mm.csv').open()))
    oldkeys=list(csv.DictReader((HERE/f'inputs/keys-{p}mm.csv').open()))
    assert list(keys[0])==list(oldkeys[0])
    assert [(r['key'],r['sensor'],r['rotation_deg']) for r in keys]==[(r['key'],r['sensor'],r['rotation_deg']) for r in oldkeys]
    assert all(math.isclose(float(r['kicad_x_mm']),100+float(coords[r['key']]['x_mm']),abs_tol=1e-8) and math.isclose(float(r['kicad_y_mm']),100-float(coords[r['key']]['y_mm']),abs_tol=1e-8) for r in keys)
result=dict(status='pass',source_pcb_verification=raw_status,input_hashes_verified=len(hashes),pitches_mm=[16,17],source_centers=21,pairs_per_envelope_per_pitch=210,rotation_cases=['zero','source'],patch_application='in-memory only; all sensor/components match proposal CSV; unmoved components unchanged',legacy_csv='header, key/sensor/rotation/order retained; 21 new positions match local-to-KiCad conversion',existing_design_files_written=0)
print(json.dumps(result,indent=2))
