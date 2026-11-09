from common import *
import importlib.util,gzip
w=E/'inspection/final';out=w/'audit';out.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('audit221',E/'audit-vias.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.E=out
src=w/'main.kicad_pcb';(out/'snapshot.kicad_pcb.gz').write_bytes(gzip.compress(src.read_bytes(),mtime=0));runtime=T/('audit221-'+digest(src)[:12]);runtime.mkdir(exist_ok=True);m.audit(dict(board='via-pad',snapshot='snapshot.kicad_pcb.gz',sha256=digest(src)),runtime)
