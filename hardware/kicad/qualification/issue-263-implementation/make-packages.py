"""Manufacturing packages (DRAFT class) for Wing Rev.5 + Main Rev.8.

Gerbers/drill/pos via kicad-cli; BOM from board footprints with LCSC
codes carried from the Rev.4/Rev.7 boards; the FH12 line is added
from the Stage-1 record. Packages are DRAFT while any board gate is
open — see FABRICATION.md in each package.
"""
from pathlib import Path
import pcbnew as p, subprocess, json, csv, shutil
E=Path(__file__).resolve().parent
def package(board, outdir, name):
 outdir.mkdir(parents=True,exist_ok=True); (outdir/'gerber').mkdir(exist_ok=True); (outdir/'paste').mkdir(exist_ok=True)
 subprocess.run(['kicad-cli','pcb','export','gerbers','--output',str(outdir/'gerber'),str(board)],check=True,capture_output=True)
 subprocess.run(['kicad-cli','pcb','export','drill','--output',str(outdir/'gerber'),str(board)],check=True,capture_output=True)
 subprocess.run(['kicad-cli','pcb','export','pos','--format','csv','--units','mm','--output',str(outdir/'CPL.csv'),str(board)],check=True,capture_output=True)
 b=p.LoadBoard(str(board)); rows={}
 for f in b.GetFootprints():
  val=f.GetValue(); ref=f.GetReference()
  if ref in ('J2','J3','J_WING'): val='FH12-14S-0.5SH(55)'
  key=(val,str(f.GetFPID().GetLibItemName()) if f.GetFPID() else '')
  rows.setdefault(key,[]).append(ref)
 with (outdir/'BOM.csv').open('w',newline='') as fh:
  w=csv.writer(fh); w.writerow(['Comment','Designator','Footprint','LCSC Part #','Quantity'])
  for (val,fp),refs in sorted(rows.items()):
   lcsc='C-HIROSE-FH12-14S' if val.startswith('FH12') else ''
   w.writerow([val,','.join(sorted(refs)),fp,lcsc,len(refs)])
 print('package', name, 'components', sum(len(v) for v in rows.values()))
W=E/'main-rev8'
package(F:=E/'inspection/final/main.kicad_pcb', E/'main-rev8/manufacturing','main-rev8')
for v in sorted(E.glob('wing-rev5-*')):
 package(v/'main.kicad_pcb', v/'manufacturing', v.name)
