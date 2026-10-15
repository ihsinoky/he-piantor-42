from session import *
for name in ['smoke','main']:
    snapshot=PREV/'evidence/processes'/('smoke-read-before' if name=='smoke' else 'baseline-read')/'snapshot.json'
    out=ROOT/'evidence'/(name+'-dsn-parity.json')
    run(name+'-dsn-parity-reader-corrected',[str(GEOM),str(ROOT/'check-dsn.py'),name,str(BASE/name/'corrected.dsn'),str(snapshot),str(BASE/name/'corrected-effective.json'),str(out)],BASE)
