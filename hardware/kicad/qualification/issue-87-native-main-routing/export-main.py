from prepare import *
ENV=json.loads((ROOT/'evidence/kicad-env.json').read_text());work=BASE/'main'
run('main-dsn',['/usr/bin/python3',str(ROOT/'pcb-probes.py'),'dsn',str(work),str(work/'main.kicad_pcb')],work,env=ENV,artifacts=[('input.dsn',work/'input.dsn')])
