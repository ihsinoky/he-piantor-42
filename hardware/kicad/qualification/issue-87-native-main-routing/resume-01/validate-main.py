from session import *
work=BASE/'main-initial-import'
run('main-initial-ses-import',['/usr/bin/python3',str(ROOT/'import-main.py')],BASE,env=ENV,artifacts=[('main.kicad_pcb',work/'main.kicad_pcb'),('main.kicad_pro',work/'main.kicad_pro')])
run('main-initial-read-return',['/usr/bin/python3',str(OLD/'read-pcb.py'),str(work/'main.kicad_pcb'),str(work/'snapshot.json')],work,env=ENV,artifacts=[('snapshot.json',work/'snapshot.json')])
run('main-initial-return-drc',[str(CLI),'pcb','drc','--format','json','--severity-all','-o',str(work/'drc.json'),str(work/'main.kicad_pcb')],work,env=ENV,artifacts=[('drc.json',work/'drc.json')])
run('main-initial-acceptance',[str(GEOM),str(ROOT/'check-import.py'),'main','/tmp/issue87/main/main.kicad_pcb',str(work/'main.kicad_pcb'),str(PREV/'evidence/processes/baseline-read/snapshot.json'),str(work/'snapshot.json'),str(work/'drc.json'),str(ROOT/'evidence/main-initial-acceptance.json')],work)
