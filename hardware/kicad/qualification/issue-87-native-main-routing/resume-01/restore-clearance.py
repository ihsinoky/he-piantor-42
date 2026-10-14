"""Restore exactly one known KiCad9.0.9 DSN typed rule; no DSN writer."""
import re,json,sys,hashlib
from decimal import Decimal
from pathlib import Path
import sexpdata as sx

def parse(raw):
    # Specctra's quote-character declaration is a lexical directive, not a Lisp
    # string. Adapt that one declaration for the standard sexpdata reader only.
    text=raw.decode('utf-8');assert text.count('(string_quote ")')==1
    return sx.loads(text.replace('(string_quote ")','(string_quote DSN_QUOTE_CHARACTER)'))

def tagged(node,tag):return [x for x in node if isinstance(x,list) and x and str(x[0])==tag]
def only(node,tag):
    rows=tagged(node,tag);assert len(rows)==1,(tag,len(rows));return rows[0]
def restore(raw):
    tree=parse(raw);assert str(tree[0])=='pcb'
    unit=only(tree,'unit');resolution=only(tree,'resolution')
    assert unit==[sx.Symbol('unit'),sx.Symbol('um')],unit
    assert resolution==[sx.Symbol('resolution'),sx.Symbol('um'),10],resolution
    structure=only(tree,'structure');rule=only(structure,'rule')
    target=[x for x in tagged(rule,'clearance') if len(x)==3 and x[2]==[sx.Symbol('type'),sx.Symbol('smd_smd')]]
    assert len(target)==1 and Decimal(str(target[0][1]))/1000==Decimal('.05'),target
    def walk(n,path=()):
        if isinstance(n,list):
            if n and str(n[0])=='clearance' and len(n)==3 and n[2]==[sx.Symbol('type'),sx.Symbol('smd_smd')]:yield path
            for i,x in enumerate(n):yield from walk(x,path+(i,))
    paths=list(walk(tree));assert len(paths)==1,paths
    matches=list(re.finditer(rb'\(clearance\s+(50(?:\.0+)?)\s+\(type\s+smd_smd\)\)',raw))
    assert len(matches)==1
    a,z=matches[0].span(1);fixed=raw[:a]+b'200'+raw[z:]
    return fixed,dict(node_index_path=list(paths[0]),node='pcb/structure/rule/clearance[type=smd_smd]',unit='um',resolution_per_um=10,before=50,after=200,before_mm=.05,after_mm=.20,byte_start=a,byte_end_before=z,line=raw[:a].count(b'\n')+1,column=a-raw.rfind(b'\n',0,a),raw_sha256=hashlib.sha256(raw).hexdigest(),corrected_sha256=hashlib.sha256(fixed).hexdigest(),output_format='all bytes identical outside numeric token')
if __name__=='__main__':
    raw=Path(sys.argv[1]);out=Path(sys.argv[2]);record=Path(sys.argv[3]);assert raw.resolve()!=out.resolve() and not out.exists()
    before=raw.read_bytes();fixed,r=restore(before);out.write_bytes(fixed);assert raw.read_bytes()==before
    record.write_text(json.dumps(r,indent=2)+'\n')
