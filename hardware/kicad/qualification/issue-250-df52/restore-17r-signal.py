"""Reject target-only MUX_OUT_B via moves; restore original routed signal copper.
The 0.125 target does not justify introducing opens. 0.100 floor stays unchanged.
"""
from pathlib import Path
import pcbnew as p,json
E=Path(__file__).resolve().parent;T=E.parents[3]/'.issue250-runtime';w=E/'wing-rev4-17mm-right';b=p.LoadBoard(str(w/'main.kicad_pcb'));src=p.LoadBoard(str(T/'wing-rev4-17mm-right-route.kicad_pcb'));held=[]
for t in b.GetTracks():
 if t.GetNetname()=='MUX_OUT_B':held.append(t);b.Remove(t)
for t in src.GetTracks():
 if t.GetNetname()=='MUX_OUT_B':
  n=t.Duplicate();n.SetNetCode(b.FindNet('MUX_OUT_B').GetNetCode());b.Add(n);held.append(n)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(w/'main.kicad_pcb'),b)
(w/'rejected-target-moves.json').write_text(json.dumps(dict(net='MUX_OUT_B',status='Target-only via moves rejected after native/independent checks; restored original routed signal objects; gate floor remains .100mm, .125mm is separately reported',source=str(T/'wing-rev4-17mm-right-route.kicad_pcb')),indent=2)+'\n')
