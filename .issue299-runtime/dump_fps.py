#!/usr/bin/env python3
"""Dump footprint census (ref, value, fp name, pad->net) from a KiCad pcb."""
import re, sys, json

def parse(path):
    txt = open(path).read()
    # split into footprint blocks by top-level "(footprint " occurrences
    fps = []
    idx = 0
    while True:
        m = re.search(r'\(footprint ', txt[idx:])
        if not m:
            break
        start = idx + m.start()
        # walk to matching close paren
        depth = 0
        i = start
        while i < len(txt):
            c = txt[i]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        fps.append(txt[start:i+1])
        idx = i + 1
    out = []
    for fp in fps:
        name = re.search(r'\(footprint "([^"]*)"', fp).group(1)
        ref = re.search(r'\(property "Reference" "([^"]*)"', fp)
        val = re.search(r'\(property "Value" "([^"]*)"', fp)
        pads = {}
        for pm in re.finditer(r'\(pad "([^"]*)" [^()]*?(?:\([^()]*\)[^()]*?)*?\(net \d+ "([^"]*)"\)', fp):
            pads[pm.group(1)] = pm.group(2)
        # fallback simpler pad/net scan
        if not pads:
            for pm in re.finditer(r'\(pad "([^"]*)"', fp):
                seg = fp[pm.start():pm.start()+400]
                nm = re.search(r'\(net \d+ "([^"]*)"\)', seg)
                if nm:
                    pads[pm.group(1)] = nm.group(1)
        out.append({"fp": name, "ref": ref.group(1) if ref else "?",
                    "value": val.group(1) if val else "?", "pads": pads})
    return out

for path in sys.argv[1:]:
    print("=====", path)
    fps = parse(path)
    for f in fps:
        if f["fp"] in ("NPTH",):
            continue
        print(json.dumps(f, ensure_ascii=False))
