"""Independent AST+exact-diff oracle; does not import the mutation routine."""
import json,sys,re,hashlib
from pathlib import Path
import sexpdata

def read(p):
    text=p.read_text();assert text.count('(string_quote ")')==1
    return sexpdata.loads(text.replace('(string_quote ")','(string_quote "double-quote")'))

def diff(a,b,path=()):
    if type(a)!=type(b):return [(path,a,b)]
    if isinstance(a,list):
        assert len(a)==len(b),('structure size',path)
        return [d for i,(x,y) in enumerate(zip(a,b)) for d in diff(x,y,path+(i,))]
    return [] if a==b else [(path,a,b)]
def nodes(t,tag,path=()):
    if isinstance(t,list):
        if t and str(t[0])==tag:yield path,t
        for i,x in enumerate(t):yield from nodes(x,tag,path+(i,))
raw,fixed,out=map(Path,sys.argv[1:4]);a,b=read(raw),read(fixed)
changes=diff(a,b);assert len(changes)==1,changes
path,old,new=changes[0];assert old==50 and new==200
parent=a
for index in path[:-1]:parent=parent[index]
assert parent==[sexpdata.Symbol('clearance'),50,[sexpdata.Symbol('type'),sexpdata.Symbol('smd_smd')]]
unit=list(nodes(a,'unit'));assert len(unit)==1 and str(unit[0][1][1])=='um'
x,y=raw.read_bytes(),fixed.read_bytes();prefix=0
while prefix<min(len(x),len(y)) and x[prefix]==y[prefix]:prefix+=1
suffix=0
while suffix<min(len(x)-prefix,len(y)-prefix) and x[-1-suffix]==y[-1-suffix]:suffix+=1
assert x[prefix:len(x)-suffix]==b'5' and y[prefix:len(y)-suffix]==b'20'
# Every global/class/layer/type rule is reported, not just the changed text.
clearances=list(nodes(b,'clearance'));widths=list(nodes(b,'width'))
assert all(float(n[1])==200 for _,n in clearances),clearances
assert all(float(n[1])==200 for _,n in widths),widths
r=dict(status='PASS_WITH_SCOPE',semantic_changes=[dict(path=list(path),before=old,after=new)],only_authorized_numeric_token_diff=True,formatting_changed=False,byte_diff=dict(offset=prefix,before='5',after='20',suffix_bytes=suffix),unit='um',all_clearance_nodes=[dict(path=list(p),node=str(n)) for p,n in clearances],all_width_nodes=[dict(path=list(p),node=str(n)) for p,n in widths],raw_sha256=hashlib.sha256(x).hexdigest(),corrected_sha256=hashlib.sha256(y).hexdigest(),effective_router_readback_required=True)
out.write_text(json.dumps(r,indent=2)+'\n');print('one semantic rule value change, byte-local difference, other nodes unchanged')
