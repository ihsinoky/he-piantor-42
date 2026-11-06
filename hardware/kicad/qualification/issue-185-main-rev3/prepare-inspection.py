from common import *
import pcbnew as p,shutil,os
label=sys.argv[1];w=E/'inspection'/label;w.mkdir(parents=True,exist_ok=True);src=E/'local35/main.kicad_pcb';old=E.parent/'issue-175-main-dual-wing-final2'
shutil.copyfile(src,w/'main.kicad_pcb');shutil.copyfile(old/'inputs/final/main.kicad_pro',w/'main.kicad_pro')
rel=os.path.relpath(old/'Stage175.pretty',w);(w/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Stage175")(type "KiCad")(uri "${KIPRJMOD}/'+rel+'")(options "")(descr "Frozen Issue175 footprints")))\n')
b=p.LoadBoard(str(old/'inspection/final/main.kicad_pcb'));assert p.SaveBoard(str(w/'canonical-baseline.kicad_pcb'),b)
