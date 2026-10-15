from session import *
work=BASE/'smoke-import'
run('small-ses-import',['/usr/bin/python3',str(ROOT/'import-small.py')],BASE,env=ENV,artifacts=[('main.kicad_pcb',work/'main.kicad_pcb'),('main.kicad_pro',work/'main.kicad_pro'),('fp-lib-table',work/'fp-lib-table')])
run('small-read-return',['/usr/bin/python3',str(OLD/'read-pcb.py'),str(work/'main.kicad_pcb'),str(work/'snapshot.json')],work,env=ENV,artifacts=[('snapshot.json',work/'snapshot.json')])
run('small-return-drc',[str(CLI),'pcb','drc','--format','json','--severity-all','-o',str(work/'drc.json'),str(work/'main.kicad_pcb')],work,env=ENV,artifacts=[('drc.json',work/'drc.json')])
run('small-acceptance',[str(GEOM),str(ROOT/'check-import.py'),'smoke','/tmp/issue87/smoke/main.kicad_pcb',str(work/'main.kicad_pcb'),str(PREV/'evidence/processes/smoke-read-before/snapshot.json'),str(work/'snapshot.json'),str(work/'drc.json'),str(ROOT/'evidence/small-acceptance.json')],work)
