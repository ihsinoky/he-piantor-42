"""Public session import into original KiCad board, never replacement from DSN."""
import pcbnew as p
import sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent;work=Path('/tmp/issue87-resume01/smoke-import');work.mkdir(exist_ok=False)
original=Path('/tmp/issue87/smoke')
for name in ['main.kicad_pcb','main.kicad_pro']:shutil.copyfile(original/name,work/name)
file=work/'main.kicad_pcb';manager=p.GetSettingsManager();manager.LoadProject(str(file.with_suffix('.kicad_pro')));b=p.LoadBoard(str(file));b.SetProject(manager.Prj())
lib=work/'Probe.pretty';lib.mkdir();io=p.PCB_IO_KICAD_SEXPR()
for fp in b.GetFootprints():io.FootprintSave(str(lib),fp)
(work/'fp-lib-table').write_text(f'(fp_lib_table (version 7) (lib (name "Probe")(type "KiCad")(uri "{lib}")(options "")(descr "Fixed small fixture")))\n')
assert p.ImportSpecctraSES(b,'/tmp/issue87-resume01/smoke-route/output.ses')
assert p.SaveBoard(str(file),b);assert manager.SaveProject(str(file.with_suffix('.kicad_pro')))
print('SES imported into original KiCad board; original pad/drill/printing objects retained for checking')
