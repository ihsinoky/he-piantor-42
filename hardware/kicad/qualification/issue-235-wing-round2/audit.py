"""Refill and qualify the saved repair without replacing its copper."""
from pathlib import Path
import pcbnew as p
import sys,subprocess
from verify import qualify
E=Path(__file__).resolve().parent
for name in sys.argv[1:]:
 w=E/name;b=p.LoadBoard(str(w/'main.kicad_pcb'));mgr=p.GetSettingsManager();mgr.LoadProject(str(w/'input.kicad_pro'));b.SetProject(mgr.Prj());b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();p.SaveBoard(str(w/'main.kicad_pcb'),b)
 subprocess.run(['kicad-cli','pcb','drc','--format','json','--severity-all','-o',str(w/'drc.json'),str(w/'main.kicad_pcb')],check=True)
 qualify(w)
