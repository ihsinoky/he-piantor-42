import runpy,sys
from pathlib import Path
E=Path('hardware/kicad/qualification/issue-113-kicad-routing-tools-falsification/evidence').resolve();globals().update(runpy.run_path(str(E/'prepare-inputs.py')))
run('python-venv',['/usr/bin/python3','-m','venv',str(TMP/'venv')])
run('dependencies',[TMP/'venv/bin/python','-m','pip','install','--no-cache-dir','--report',E/'pip-report.json','-r',TMP/'KiCadRoutingTools/requirements.txt'],timeout=300)
