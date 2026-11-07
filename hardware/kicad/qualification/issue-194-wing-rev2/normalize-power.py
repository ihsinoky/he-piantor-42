"""Enforce D-021 on a routed candidate, recording every widened segment.
No automatic acceptance: refill, native DRC, copper graph and widths must pass.
"""
from pathlib import Path
import json,sys
import pcbnew as p
E=Path(__file__).resolve().parent
for name in sys.argv[1:]:
 w=E/name;src=w/('tapped.kicad_pcb' if (w/'tapped.kicad_pcb').exists() else 'power-repaired.kicad_pcb');b=p.LoadBoard(str(src));assert b
 changes=[]
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA) or t.GetNetname() not in ('GND','HALL_5V') or t.GetWidth()>=300000:continue
  changes.append(dict(uuid=t.m_Uuid.AsString(),net=t.GetNetname(),old_width_mm=p.ToMM(t.GetWidth()),new_width_mm=.3,start=[p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)],end=[p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)]));t.SetWidth(300000)
 for z in list(b.Zones()):
  if not z.GetIsRuleArea():b.Delete(z)
 assert p.SaveBoard(str(w/'repaired.kicad_pcb'),b)
 (w/'power-width-normalization.json').write_text(json.dumps(changes,indent=2)+'\n');print(w.name,'widened',len(changes),flush=True)
