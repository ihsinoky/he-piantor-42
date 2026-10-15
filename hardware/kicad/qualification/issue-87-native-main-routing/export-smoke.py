from prepare import *
ENV=json.loads((ROOT/'evidence/kicad-env.json').read_text());work=BASE/'smoke'
run('smoke-create-typed-footprint',['/usr/bin/python3',str(ROOT/'pcb-probes.py'),'smoke',str(work)],BASE,env=ENV)
run('smoke-read-before',['/usr/bin/python3',str(OLD/'read-pcb.py'),str(work/'main.kicad_pcb'),str(work/'before.json')],work,env=ENV,artifacts=[('snapshot.json',work/'before.json'),('main.kicad_pcb',work/'main.kicad_pcb'),('main.kicad_pro',work/'main.kicad_pro')])
run('smoke-dsn',['/usr/bin/python3',str(ROOT/'pcb-probes.py'),'dsn',str(work),str(work/'main.kicad_pcb')],work,env=ENV,artifacts=[('input.dsn',work/'input.dsn')])
