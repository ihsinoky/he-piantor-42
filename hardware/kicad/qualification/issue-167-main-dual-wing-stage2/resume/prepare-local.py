"""One bounded local repair: remove only failed power nets and named blockers.
Restore exactly the missing V5V2 via and give it a useful top copper connection.
"""
from common import *
import sexpdata as sx,shutil,uuid
w=E/'inputs/local';w.mkdir(parents=True,exist_ok=False)
source=E/'inspection/global';a=sx.loads((source/'main.kicad_pcb').read_text());out=[a[0]];removed=[]
def val(x,k):return next(y[1] for y in x if isinstance(y,list) and str(y[0])==k)
nets={str(x[2]):int(x[1]) for x in a if isinstance(x,list) and str(x[0])=='net'}
targets=['V1V1','V3V3','QSPI_SD0','XOUT'];codes={nets[x] for x in targets}
for x in a[1:]:
 if isinstance(x,list) and str(x[0]) in ['segment','via'] and val(x,'net') in codes:removed.append(sx.dumps(x))
 else:out.append(x)
missing=json.loads((E/'inspection/global/transfer-diff.json').read_text())['missing_retained_vias'];assert len(missing)==1
out.append(sx.loads(missing[0]));out.append(sx.loads(f'(segment (start 90 78.5) (end 90.8875 77.5) (width 0.2) (layer "F.Cu") (net {nets["V5V2"]}) (uuid "{uuid.uuid4()}"))'))
(w/'main.kicad_pcb').write_text(sx.dumps(out)+'\n')
for file in ['main.kicad_pro','fp-lib-table']:shutil.copyfile(E/'inputs/global'/file,w/file)
save(E/'local-scope.json',dict(utc=now(),max_attempts=1,timeout_seconds=900,reason='Independent global check: V1V1/V3V3 have three missing physical joins; router diagnostics name XOUT/QSPI_SD0 blockers. Global output lost one orphan V5V2 via.',target_nets=targets,removed_segments_and_vias=removed,restored_via=missing[0],additional_v5v2_connection='0.2mm top trace from restored via to C26.1; no narrowing or placement changes',frozen_input_sha256=digest(w/'main.kicad_pcb'),condition_args=ARGS))
print('Local repair frozen',len(removed),'target-net copper objects')
