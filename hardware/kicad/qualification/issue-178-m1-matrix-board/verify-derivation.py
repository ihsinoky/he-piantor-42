"""Strictly reconcile final edits with the one raw route; all changes enumerated."""
from common import *
import sexpdata as sx,collections,csv,math

def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def children(n,k):return [x for x in n if tag(x)==k]
def val(n,k):return children(n,k)[0][1:]
def counter(tree):return collections.Counter(sx.dumps(n) for n in tree[1:])
report={}
for label,old,new in [('input',E/'inputs/m1-matrix18-16-17mm/main.kicad_pcb',E/'cell-inputs/final/main.kicad_pcb'),('output',E/'runs/KRT-M1-01/out.kicad_pcb',E/'runs/final/out.kicad_pcb')]:
 a=sx.loads(old.read_text());z=sx.loads(new.read_text());tp=0;removed=0
 for f in children(a,'footprint'):
  ref=next(x[2] for x in children(f,'property') if x[1]=='Reference')
  if str(ref).startswith('TP_'):
   for q in children(f,'pad'):children(q,'layers')[0].remove('F.Paste')
   tp+=1
 if label=='output':
  nodes=[n for n in children(a,'segment') if val(n,'uuid')==['3b526ba3-fcea-418c-ac55-dcc9733483be']];assert len(nodes)==1
  a.remove(nodes[0]);removed=1
 silk=[n for n in z[1:] if tag(n).startswith('gr_') and children(n,'layer') and val(n,'layer')==['F.SilkS']]
 for n in silk:z.remove(n)
 assert counter(a)==counter(z),(label,'unexplained design change')
 assert len(silk)==json.loads((E/'final-design-derivation.json').read_text())['added_silk_primitives']
 assert tp==18
 report[label]=dict(original_sha256=digest(old),final_sha256=digest(new),testpad_paste_removals=tp,silk_additions=len(silk),exact_segments_removed=removed,all_other_AST_nodes_identical=True)
# Both sides got literally the same silk objects, not independent approximations.
inputs=sx.loads((E/'cell-inputs/final/main.kicad_pcb').read_text());outputs=sx.loads((E/'runs/final/out.kicad_pcb').read_text())
def silks(t):return collections.Counter(sx.dumps(n) for n in t[1:] if tag(n).startswith('gr_') and children(n,'layer') and val(n,'layer')==['F.SilkS'])
assert silks(inputs)==silks(outputs)
L=E/'PCBA.pretty';oldlib=E/'Wing129.pretty'
for p in oldlib.iterdir():
 old=p.read_text();new=(L/p.name).read_text()
 assert new==(old.replace(' "F.Paste"','') if p.name=='testpoint.kicad_mod' else old)
assert (E/'board/m1-matrix18.kicad_pcb').read_bytes()==(E/'runs/final/out.kicad_pcb').read_bytes()
assert (E/'board/m1-matrix18.kicad_pro').read_bytes()==(E/'cell-inputs/final/main.kicad_pro').read_bytes()
bom=list(csv.DictReader((E/'manufacturing/BOM.csv').open()));cpl=list(csv.DictReader((E/'manufacturing/CPL.csv').open()))
refs=[ref for row in bom for ref in row['Designator'].split(',')];assert len(refs)==len(set(refs))==43
assert set(refs)=={r['Designator'] for r in cpl}
ledger={r['reference']:r for r in json.loads((E/'assembly-review.json').read_text())['parts']}
for row in cpl:
 x,y=ledger[row['Designator']]['body_centroid_kicad_mm']
 assert math.isclose(float(row['Mid X'].removesuffix('mm')),x-36,abs_tol=1e-6)
 assert math.isclose(float(row['Mid Y'].removesuffix('mm')),140-y,abs_tol=1e-6)
 assert row['Layer']=='top' and float(row['Rotation'])==0
save(E/'derivation-verification.json',dict(utc=now(),comparisons=report,identical_silk_on_both_sides=True,only_testpad_paste_library_change=True,delivered_board_exact_final_bytes=True,bom_cpl_exact_reference_match=43,CPL_body_centroids_checked=True,unexplained_changes=0))
print('Strict raw/final AST derivation and BOM/CPL reconciliation passed')
