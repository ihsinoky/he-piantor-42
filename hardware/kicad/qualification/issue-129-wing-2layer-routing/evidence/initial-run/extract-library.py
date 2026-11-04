"""Extract only existing component-library land geometry; never reads design/placement sources."""
import json,unittest,hashlib
from pathlib import Path
from jitx.test import TestCase
from jitx.sample import SampleSubstrate
from jitx.substrate import SubstrateContext
from jitx.landpattern import PadShape
from jitxlib.landpatterns.twopin.smt import SMT
from he_piantor_42_jitx.components.sensors.texas_instruments_drv5055a3qdbzr import DRV5055A3QDBZR
from he_piantor_42_jitx.components.switches.texas_instruments_tmux1208pwr import TMUX1208PWR
from he_piantor_42_jitx.components.connectors.jst_bm14b_ghs_tbt import BM14B_GHS_TBT
from he_piantor_42_jitx.components.generic_electrical import Capacitor,TestPoint
E=Path(__file__).resolve().parent
class Bypass(Capacitor):landpattern=SMT('0603')
class Extract(TestCase):
 def test_extract(self):
  with SubstrateContext(SampleSubstrate()):
   h=DRV5055A3QDBZR();m=TMUX1208PWR();j=BM14B_GHS_TBT();c=Bypass(capacitance=1e-7);t=TestPoint()
   groups={'hall':[(str(i),h.landpattern.p[i]) for i in range(1,4)],'mux':[(str(i),m.landpattern.p[i]) for i in range(1,17)],'connector':[(str(i+1),p) for i,p in enumerate(j.landpattern.contacts)]+[('MP',p) for p in j.landpattern.reinforcement], 'capacitor':[('1',c.landpattern.p[1]),('2',c.landpattern.p[2])], 'testpoint':[('1',t.landpattern.pad)]}
   result={}
   for kind,pads in groups.items():
    result[kind]=[]
    for number,pad in pads:
     shape=pad.shape.shape if isinstance(pad.shape,PadShape) else pad.shape
     g=(pad.transform*shape).to_shapely();x0,y0,x1,y1=g.bounds
     if kind=='testpoint':x0=y0=-.6;x1=y1=.6
     result[kind].append(dict(number=number,x_mm=(x0+x1)/2,y_mm=(y0+y1)/2,width_mm=x1-x0,height_mm=y1-y0,shape='circle' if kind=='testpoint' else 'rect',wkt=g.wkt))
   (E/'library-pads.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':unittest.main()
