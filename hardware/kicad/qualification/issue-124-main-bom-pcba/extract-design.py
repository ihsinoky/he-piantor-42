"""Read-only extraction of Issue #124's pinned Main design with stdlib only.

Run from the repository root. Prints JSON; never writes a design or report.
PCB pad attributes are counted independently from footprint attr smd.
"""
import re,json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path

def parse(path):
    toks=iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',Path(path).read_text()))
    stack=[];root=None
    for t in toks:
        if t=='(':
            a=[]
            if stack:stack[-1].append(a)
            else:root=a
            stack.append(a)
        elif t==')':stack.pop()
        else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
    assert not stack
    return root

def children(a,k):return [b for b in a if isinstance(b,list) and b and b[0]==k]
def child(a,k):return children(a,k)[0]
def props(a):return {b[1]:b[2] for b in children(a,'property')}
base=Path('hardware/kicad/qualification')
pcb=base/'issue-121-full-auto-conditions/evidence/inspection/main-cell1/krt/main.kicad_pcb'
sch=base/'eda-004g/resume-02/evidence/processes/initial-author-schematic/main.kicad_sch'
net=base/'eda-004g/resume-02/evidence/processes/initial-netlist/main.xml'
contract=base/'eda-004g/resume-02/main-contract-v2.json'
c={x['footprint_id']:x for x in json.loads(contract.read_text())['components']}
s={props(x)['Reference']:props(x) for x in children(parse(sch),'symbol') if 'Reference' in props(x)}
s={k:v for k,v in s.items() if not k.startswith("#")}
n={x.attrib['ref']: {'Value':x.findtext('value'),'Footprint':x.findtext('footprint')} for x in ET.parse(net).findall('.//components/comp')}
rows=[]
for f in children(parse(pcb),'footprint'):
 p=props(f);ref=p['Reference'];ct=c[f[1]]
 pads=children(f,'pad')
 rows.append(dict(ref=ref,value=p['Value'],footprint=f[1],source_id=ct['reference'],source_package=ct['source_footprint'],layer=child(f,'layer')[1],pads=len(pads),pad_types={k:sum(x[2]==k for x in pads) for k in sorted({x[2] for x in pads})},schematic_value=s[ref]['Value'],netlist_value=n[ref]['Value'],schematic_footprint=s[ref]['Footprint'],value_match=p['Value']==s[ref]['Value']==n[ref]['Value']))
rows.sort(key=lambda x:(re.sub(r'\d','',x['ref']),int(re.search(r'\d+',x['ref'])[0])))
assert set(s)==set(n)=={x["ref"] for x in rows}
assert len(rows)==len(s)==len(n)==49
assert sum(x['pads'] for x in rows)==199
assert all(x['value_match'] and x['layer']=='F.Cu' and (set(x['pad_types'])=={'smd'} or x['ref']=='J1') and x['footprint']==x['schematic_footprint'] for x in rows)
result=dict(source_commit='c3450394fb0aee3ab1b3e10f116e21c1ebfeee2c',files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [pcb,sch,net,contract]},footprint_count=len(rows),physical_pads=sum(x['pads'] for x in rows),rows=rows)
result['pad_types']={k:sum(x['pad_types'].get(k,0) for x in rows) for k in ['smd','thru_hole','np_thru_hole']}
assert result['pad_types']=={'smd':193,'thru_hole':4,'np_thru_hole':2}
assert next(x for x in rows if x['ref']=='J1')['pad_types']=={'smd':12,'thru_hole':4,'np_thru_hole':2}
print(json.dumps(result,ensure_ascii=False,indent=2))
