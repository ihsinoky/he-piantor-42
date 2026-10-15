from session import *
for name in ['smoke','main']:
    work=BASE/name;work.mkdir()
    # Raw bytes already retained in previous epoch, referenced without duplication.
    raw=Path('/tmp/issue87')/name/'input.dsn';fixed=work/'corrected.dsn'
    run(name+'-restore',[str(GEOM),str(ROOT/'restore-clearance.py'),str(raw),str(fixed),str(work/'mutation.json')],BASE,artifacts=[('corrected.dsn',fixed),('mutation.json',work/'mutation.json')])
    run(name+'-independent-diff',[str(GEOM),str(ROOT/'check-clearance-change.py'),str(raw),str(fixed),str(work/'diff.json')],BASE,artifacts=[('diff.json',work/'diff.json')])
