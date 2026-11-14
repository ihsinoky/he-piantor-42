from pathlib import Path
import sys,shutil,json
import pcbnew as p
E=Path(__file__).resolve().parent;R=E.parents[3];T=R/'.issue250-runtime'
for name in sys.argv[1:]:
 w=E/name;src=T/(name+'-route.kicad_pcb');assert src.exists();b=p.LoadBoard(str(src))
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(w/'main.kicad_pcb'),b)
 # Keep baseline design rules. Router-generated project defaults are not adopted.
 if name=='main':
  (w/'fp-lib-table').write_text('''(fp_lib_table
(lib (name Rev4)(type KiCad)(uri "${KIPRJMOD}/../../issue-196-main-rev4-phaseb/Rev4.pretty")(options "")(descr ""))
(lib (name Rev5)(type KiCad)(uri "${KIPRJMOD}/../../issue-221-main-rev5/Rev5.pretty")(options "")(descr ""))
(lib (name DF52)(type KiCad)(uri "${KIPRJMOD}/../DF52.pretty")(options "")(descr "")))\n''')
 print(name,flush=True)
