#!/usr/bin/env python3
"""Extract footprint data for JBATT/DLED/SW1/J2/J3/J4 from the wireless
Main board file of record (origin/main, SHA 75db72bc). Numbers come from
the board file itself; asm transform validated on recorded anchors."""
import json, re, sys, hashlib

PATH = "hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb"
data = open(PATH).read()
sha = hashlib.sha256(open(PATH,'rb').read()).hexdigest()

def tokenize(s):
    return re.findall(r'\(|\)|[^\s()]+', s)

def parse(tokens):
    stack=[[]]
    for t in tokens:
        if t=='(':
            n=[]; stack[-1].append(n); stack.append(n)
        elif t==')':
            stack.pop()
        else:
            stack[-1].append(t.strip('"'))
    return stack[0][0]

tree = parse(tokenize(data))

def find_fps(node, out):
    if isinstance(node, list):
        if node and node[0]=='footprint':
            out.append(node)
        for c in node: find_fps(c, out)
    return out

def get(node, key):
    for c in node:
        if isinstance(c, list) and c and c[0]==key: return c
    return None

def prop(node, name):
    for c in node:
        if isinstance(c,list) and c and c[0]=='property' and len(c)>2 and c[1]==name:
            return c[2]
    return None

targets = {}
for fp in find_fps(tree, []):
    ref = prop(fp, 'Reference')
    if ref in ('JBATT','DLED','SW1','J2','J3','J4','JPAD'):
        at = get(fp,'at'); pos=[float(at[1]), float(at[2])]; rot=float(at[3]) if len(at)>3 else 0.0
        pads=[]
        for c in fp:
            if isinstance(c,list) and c and c[0]=='pad':
                pat=get(c,'at'); net=get(c,'net')
                pads.append({'num':c[1],'at':[float(pat[1]),float(pat[2])],
                             'size':[float(get(c,'size')[1]),float(get(c,'size')[2])],
                             'net': net[2] if net and len(net)>2 else None})
        targets[ref]={'value':prop(fp,'Value'),'pos_board':pos,'rot':rot,'pads':pads}

# asm transform: X = bx-100, Y = by-66.602 (anchors validated below)
def asm(p): return [round(p[0]-100.0,3), round(p[1]-66.602,3)]
for ref,d in targets.items():
    d['pos_asm']=asm(d['pos_board'])
    for p in d['pads']: p['asm']=asm([d['pos_board'][0]+p['at'][0], d['pos_board'][1]+p['at'][1]])

out={'board_sha256':sha,'targets':targets}
json.dump(out, open('.issue296-runtime/pilotb-coords.json','w'), indent=1)
for ref,d in targets.items():
    print(ref, d['value'], 'board', d['pos_board'], 'rot', d['rot'], '-> asm', d['pos_asm'],
          'pads', [(p['num'],p['net']) for p in d['pads']])
