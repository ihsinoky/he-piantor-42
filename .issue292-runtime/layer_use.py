import pcbnew as p
from collections import Counter
b = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
LN = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}
c = Counter()
for t in b.GetTracks():
    if not isinstance(t, p.PCB_VIA):
        c[(LN[t.GetLayer()], t.GetNetname() == 'GND')] += 1
for L in ('F','I1','I2','B'):
    print(L, 'GND tracks:', c[(L, True)], 'signal tracks:', c[(L, False)])
z = Counter()
for zn in b.Zones():
    for L in ('F','I1','I2','B'):
        pass
    z[zn.GetNetname()] += 1
print('zones by net:', dict(z))
via = [t for t in b.GetTracks() if isinstance(t, p.PCB_VIA)][0]
print('via sample: width F', via.GetWidth(p.F_Cu)/1e6, 'drill', via.GetDrillSize().x/1e6, 'type', via.GetViaType())
