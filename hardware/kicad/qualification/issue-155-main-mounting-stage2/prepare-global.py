"""Bounded fallback: remove all 0.10 mm routed tracks and all vias; retain 0.20 mm seed copper."""
from common import *
import shutil,collections,sexpdata as sx
local=json.loads((E/'inspection/local/assessment.json').read_text());assert not local['pass_acceptance']
source=E/'inputs/revised';w=E/'inputs/global';w.mkdir(parents=True,exist_ok=True)
assert not (w/'main.kicad_pcb').exists(), 'Never overwrite a frozen routing input'
shutil.copyfile(source/'main.kicad_pro',w/'main.kicad_pro');shutil.copyfile(source/'fp-lib-table',w/'fp-lib-table')
b=sx.loads((source/'main.kicad_pcb').read_text());removed=[];retained=[];output=[b[0]]
def value(n,k):return next(x[1] for x in n if isinstance(x,list) and str(x[0])==k)
for t in b[1:]:
 kind=str(t[0]) if isinstance(t,list) and t else ''
 if kind in ['segment','via']:
  uid=str(value(t,'uuid'));net=int(value(t,'net'))
  if kind=='via' or value(t,'width')==.1:
   removed.append(dict(uuid=uid,kind=kind,net_code=net));continue
  assert value(t,'width')==.2
  retained.append(dict(uuid=uid,net_code=net,layer=value(t,'layer'),width_mm=value(t,'width')))
 if kind=='zone':
  t=[x for x in t if not (isinstance(x,list) and str(x[0]) in ['filled_polygon','fill_segments'])]
 output.append(t)
assert len(removed)==603 and len(retained)==3
(w/'main.kicad_pcb').write_text(sx.dumps(output)+'\n')
save(E/'global-scope.json',dict(utc=now(),reason='Local attempt failed independent retained-copper qualification; no additional local attempt.',local_assessment=local,removed_items=removed,retained_segments=retained,removed_counts=dict(segments_0100mm=537,vias_0600_0300mm=66),original_0200mm_seed_segments_retained=3,other_changes='None: footprints, pad nets, board outline, layer stack, thickness, artwork, GND zone settings, four holes and four keepouts retained.',max_attempts=1,timeout_seconds=1800,condition_args=ARGS,retention_flag='--keep-input-copper'))
print('Full reroute scope frozen: 537 tracks + 66 vias removed; 3 original .20mm segments retained')
