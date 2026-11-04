"""Supplement historical geometry reconciliation with explicit native face/net inventories."""
import runpy,sys,re
from pathlib import Path
E=Path(__file__).resolve().parent;globals().update(runpy.run_path(str(E/'prepare-inputs.py')))
sys.path.insert(0,str(RT/'geometry/lib/python3.12/site-packages'));import sexpdata as sx
rows={}
def children(t,tag):return [x for x in t if isinstance(x,list) and x and str(x[0])==tag]
def one(t,tag):
 x=children(t,tag);assert len(x)==1;return x[0]
for stage in ['smoke','main']:
 w=E/'inputs'/stage;native=sx.loads((w/'main.kicad_pcb').read_text())
 text=(w/'corrected.dsn').read_text().replace('(string_quote ")','(string_quote quote_character)');text=re.sub(r'(?<![\w"])(?:Round|Rect|Oval)\[(?:T|A|B)\]Pad_[^\s()"]+',lambda m:json.dumps(m.group()),text);dsn=sx.loads(text)
 faces={}
 for f in children(native,'footprint'):
  ref=next(str(p[2]) for p in children(f,'property') if str(p[1])=='Reference');faces[ref]=str(one(f,'layer')[1])
 dsn_faces={str(p[1]):str(p[4]) for c in children(one(dsn,'placement'),'component') for p in children(c,'place')}
 assert {r:('front' if l=='F.Cu' else 'back' if l=='B.Cu' else 'unknown') for r,l in faces.items()}==dsn_faces
 native_nets={str(n[2]) for n in children(native,'net') if str(n[2])};dsn_nets={str(n[1]) for n in children(one(dsn,'network'),'net')};assert native_nets==dsn_nets
 layers=[str(x[1]) for x in one(native,'layers')[1:] if isinstance(x,list) and str(x[2])=='signal'];assert layers==['F.Cu','B.Cu']
 rows[stage]=dict(footprint_native_faces=faces,dsn_faces=dsn_faces,all_footprint_faces_match=True,all_net_definitions_match=True,native_nets=sorted(native_nets),dsn_nets=sorted(dsn_nets),signal_layers=layers)
save(E/'native-inventory.json',dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),timing='Pre-route explicit native footprint faces and all nonempty net definitions including unused nets',inputs=rows))
print('Explicit footprint faces, complete native net definitions and signal layers match for both frozen inputs')
