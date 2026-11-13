"""Freeze the study route as a native board; create matching local footprints."""
from common import *
import pcbnew as p
src=Path(sys.argv[1]) if len(sys.argv)>1 else T/'route-power13.kicad_pcb';w=E/'inspection/final';b=p.LoadBoard(str(src));lib=E/'Rev7.pretty';lib.mkdir(exist_ok=True)
for f in b.GetFootprints():
 if f.GetReference() in ['J2','J3']:
  f.SetFPID(p.LIB_ID('Rev7',f.GetReference()));p.FootprintSave(str(lib),f)
p.SaveBoard(str(w/'main.kicad_pcb'),b)
t=(E.parent/'issue-226-main-rev6/inspection/final/fp-lib-table').read_text().replace('\n)', '\n(lib (name Rev7)(type KiCad)(uri "${KIPRJMOD}/../../Rev7.pretty")(options "")(descr ""))\n)');(w/'fp-lib-table').write_text(t)
