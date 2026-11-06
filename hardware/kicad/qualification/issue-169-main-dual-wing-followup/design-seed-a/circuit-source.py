"""Explicit engineering net contract derived from frozen #155 circuit source,
not from router output. Used to author native schematic and independently
compare every PCB pad. Duplicate physical same-number lands are one pin.
"""
from common import *
source=R/'hardware/kicad/qualification/eda-004g/resume-02/main-contract-v2.json'
d=json.loads(source.read_text());components={}
for c in d['components']:
 components[c['cad_reference']]=dict(value=c['display_value'],pins={n:row['named_net'] for n,row in c['pins'].items()},pin_roles=c['pin_roles'],source=c['reference'])
components['U1']['pins']['8']='MUX_EN1';components['U5']['pins']['1']='V5V2'
def add(ref,value,pins,names=None):
 components[ref]=dict(value=value,pins={str(k):v for k,v in pins.items()},pin_roles={str(k):dict(name=(names or {}).get(str(k),str(k)),role='passive') for k in pins},source='Issue169 explicit addition')
pins=components['J2']['pins'].copy();pins['7']='MUX_EN1';add('J3','BM14B-GHS-TBT(LF)(SN)',pins)
add('R16','100k',{'1':'MUX_EN1','2':'GND'})
add('U6','TPS63070RNMR',{'1':'GND','2':'RAIL_PG','3':'VAUX','4':'GND','5':'FB_5V2','6':'GND','7':'V5V2','8':'V5V2','9':'SW2','10':'GND','11':'SW1','12':'VBUS','13':'VBUS','14':'HALL_PWR_EN','15':'GND'},dict(zip(map(str,range(1,16)),['PS/SYNC','PG','VAUX','GND','FB','FB2','VOUT','VOUT','L2','PGND','L1','VIN','VIN','EN','VSEL'])))
add('L1','1.5uH XFL4020-152MEC',{'1':'SW1','2':'SW2'})
for ref in ['C23','C24']:add(ref,'22uF 16V X6S 0805',{'1':'VBUS','2':'GND'})
add('C25','100nF',{'1':'VAUX','2':'GND'})
for ref in ['C26','C27','C28']:add(ref,'22uF 16V X6S 0805',{'1':'V5V2','2':'GND'})
add('R17','54.9k 0.1% 25ppm/K',{'1':'V5V2','2':'FB_5V2'})
add('R18','10k 0.1% 25ppm/K',{'1':'FB_5V2','2':'GND'})
add('R19','100k',{'1':'V3V3','2':'RAIL_PG'})
if __name__=='__main__':save(E/'logical-contract.json',dict(basis=str(source.relative_to(R)),basis_sha256=digest(source),original_components=49,additions=13,components=components))
