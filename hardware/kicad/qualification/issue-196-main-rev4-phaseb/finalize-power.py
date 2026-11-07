"""Bind the copper extraction to the final board after stencil-only restoration."""
from common import *
import collections,sexpdata as sx
source=E/'inspection/power01/main.kicad_pcb';final=E/'inspection/final/main.kicad_pcb'
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def ispaste(n):return tag(n).startswith('gr_') and any(tag(c)=='layer' and str(c[1]) in ['F.Paste','B.Paste'] for c in n)
def inventory(path):return collections.Counter(sx.dumps(n) for n in sx.loads(path.read_text())[1:] if not ispaste(n))
a,c=inventory(source),inventory(final);assert a==c,(list((a-c).elements())[:1],list((c-a).elements())[:1])
save(E/'copper-equivalence.json',dict(pass_check=True,extracted_board_sha256=digest(source),final_board_sha256=digest(final),method='Every top-level native AST node except F.Paste/B.Paste drawing nodes compared exactly; no copper, pad, zone, fill, via, routing or project normalization',same_copper=True))
for kind in ['power','ground']:
 data=json.loads((E/(kind+'-extraction-power01.json')).read_text());key='PCB_sha256' if kind=='power' else 'board_sha256';assert data[key]==digest(source);data['extracted_board_sha256']=data[key];data[key]=digest(final);data['final_stencil_only_change_verified_by']='copper-equivalence.json';(E/(kind+'-extraction-final.json')).write_text(json.dumps(data,indent=2)+'\n')
print('Final copper equivalence PASS')
