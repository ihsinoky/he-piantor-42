"""Read-only failure diagnosis. Does not rerun, repair or override the failed gate."""
import pcbnew as p,json,datetime
from pathlib import Path
E=Path(__file__).resolve().parent
rows={}
for w in sorted((E/'inputs').iterdir()):
 b=p.LoadBoard(str(w/'main.kicad_pcb'));items=[]
 for f in b.GetFootprints():
  items.append(dict(reference=f.GetReference(),library_id=f.GetFPIDAsString(),nickname=str(f.GetFPID().GetLibNickname()),item=str(f.GetFPID().GetLibItemName()),pad_count=len(list(f.Pads()))))
 rows[w.name]=dict(footprint_count=len(items),items=items)
# Isolate the library loader behavior without saving any PCB or routing.
f=p.FootprintLoad(str(E/'Wing129.pretty'),'hall')
report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),failed_gate_preserved=True,no_routing_started=True,diagnosis='FootprintLoad(path, item) returns an item-only LIB_ID; builder does not restore nickname after loading. The serialized footprints therefore have item-only IDs, whereas the independent gate expects Wing129:item.',loaded_hall_id=f.GetFPIDAsString(),boards=rows,repair_performed=False,equivalence_retried=False)
(E/'failure-diagnosis.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='boards'},indent=2))
