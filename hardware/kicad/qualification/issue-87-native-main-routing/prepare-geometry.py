from prepare import *
run('geometry-venv',['python3','-m','venv',str(BASE/'geometry')],BASE)
run('geometry-install',[str(BASE/'geometry/bin/pip'),'install','--require-hashes','-r',str(OLD/'geometry-requirements.txt')],BASE,180)
save(ROOT/'evidence/environment-correction.json',dict(failure='System Python 3.12 venv lacks ensurepip',basis='Prior hash lock targets host Python 3.14 wheels; pcbnew stays on /usr/bin/python3 3.12, geometry checker uses host Python 3.14 venv',scope='isolated /tmp environment only',original_failure='processes/venv'))
