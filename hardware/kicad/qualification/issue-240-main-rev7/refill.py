from common import *
import pcbnew as p
f=Path(sys.argv[1]) if len(sys.argv)>1 else E/'inspection/final/main.kicad_pcb'
b=p.LoadBoard(str(f));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
