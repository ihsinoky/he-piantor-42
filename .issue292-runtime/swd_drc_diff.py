#!/usr/bin/env python3
"""Item-level diff of two kicad-cli DRC JSON reports (baseline vs
respin work copy). Identity = type + item descriptions + positions.
Prints class counters for both, then every added / removed item.
"""
import json, sys
from collections import Counter

def key(v):
    items = []
    for i in v.get('items', []):
        pos = i.get('pos') or {}
        items.append((i.get('description', ''),
                      round(pos.get('x', 0), 2), round(pos.get('y', 0), 2)))
    return (v['type'], tuple(sorted(items)))

def load(path):
    d = json.load(open(path))
    out = Counter()
    raw = {}
    for v in d.get('violations', []):
        k = key(v)
        out[k] += 1
        raw[k] = v
    unc = []
    for u in d.get('unconnected_items', []):
        items = []
        for i in u.get('items', []):
            pos = i.get('pos') or {}
            items.append((i.get('description', ''),
                          round(pos.get('x', 0), 2), round(pos.get('y', 0), 2)))
        unc.append(tuple(sorted(items)))
    return out, raw, Counter(unc), d

base, braw, bunc, bd = load(sys.argv[1])
work, wraw, wunc, wd = load(sys.argv[2])

print('=== class counters (base -> work) ===')
bt = Counter(v['type'] for v in bd.get('violations', []))
wt = Counter(v['type'] for v in wd.get('violations', []))
for t in sorted(set(bt) | set(wt)):
    mark = '  <-- CHANGED' if bt[t] != wt[t] else ''
    print('%-24s %4d -> %4d%s' % (t, bt[t], wt[t], mark))
print('total: %d -> %d' % (sum(bt.values()), sum(wt.values())))

print()
print('=== ADDED violations (in work, not in base) ===')
n = 0
for k, c in sorted((work - base).items()):
    print('x%d' % c, k)
    n += c
print('added total:', n)
print()
print('=== REMOVED violations (in base, not in work) ===')
n = 0
for k, c in sorted((base - work).items()):
    print('x%d' % c, k)
    n += c
print('removed total:', n)
print()
print('=== unconnected: base %d, work %d ===' % (sum(bunc.values()), sum(wunc.values())))
print('added unconnected:', list((wunc - bunc).elements()))
print('removed unconnected:', list((bunc - wunc).elements()))
