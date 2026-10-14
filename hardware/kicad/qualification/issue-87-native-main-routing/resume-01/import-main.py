"""Public SES import into a copy of the original fixed Main; no copper edits."""
import sys,shutil
from pathlib import Path
import pcbnew as p
BASE=Path('/tmp/issue87-resume01');work=BASE/'main-initial-import';work.mkdir(exist_ok=False)
for name in ['main.kicad_pcb','main.kicad_pro','fp-lib-table']:shutil.copyfile(Path('/tmp/issue87/main')/name,work/name)
file=work/'main.kicad_pcb';manager=p.GetSettingsManager();manager.LoadProject(str(file.with_suffix('.kicad_pro')));b=p.LoadBoard(str(file));b.SetProject(manager.Prj())
assert p.ImportSpecctraSES(b,str(BASE/'main-initial-route/output.ses'))
assert p.SaveBoard(str(file),b);assert manager.SaveProject(str(file.with_suffix('.kicad_pro')))
print('imported first Main SES into original fixed board copy; unchanged nonroute input checked independently')
