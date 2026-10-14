"""Hand-transcribed source intent, independent of any schematic/PCB generator.

This is a partial expectation inventory, NOT a Main copper checker or accepted
contract. No historical Circuit JSON is read and no production source is edited.
Unverified pin roles and physical shapes are deliberately left unqualified.
"""
from pathlib import Path
from capture import ROOT, save, digest, utc

parts = []


def part(ref, value, package, x, y, angle, pins):
    parts.append(dict(reference=ref, value=value, source_footprint=package,
                      source_position_mm=[x, y], source_ccw_rotation_deg=angle,
                      pins={str(n): dict(alias=a, named_net=net, intentional_nc=net is None)
                            for n, a, net in pins}))


power = {1, 10, 22, 33, 42, 43, 44, 48, 49}
signals = {4:'MUX_A0', 5:'MUX_A1', 6:'MUX_A2', 7:'WING_EN', 9:'HALL_PWR_EN',
           19:'TESTEN', 20:'XIN', 21:'XOUT', 23:'DVDD23', 24:'SWCLK', 25:'SWDIO',
           26:'RUN', 38:'ADC_A', 39:'ADC_B', 40:'ADC_C', 45:'VREG_OUT', 46:'USB_DM',
           47:'USB_DP', 50:'DVDD50', 51:'QSPI_SD3', 52:'QSPI_SCLK', 53:'QSPI_SD0',
           54:'QSPI_SD2', 55:'QSPI_SD1', 56:'QSPI_SS', 57:'GND_EP'}
mcu = []
for n in range(1, 58):
    alias = f'PWR{n}' if n in power else signals.get(n, f'UNUSED{n}')
    net = 'V3V3' if n in power else None if n not in signals else (
        'V1V1' if n in (23, 45, 50) else 'GND' if n in (19, 57) else
        'QSPI_SS_MCU' if n == 56 else alias)
    mcu.append((n, alias, net))
part('U_MCU', 'RP2040', 'rp2040Footprint', 0, 0, 0, mcu)

part('J_USB', 'TYPE-C-31-M-12', 'usbFootprint', -15, 19, 0,
     [(i+1, a, n) for i, (a, n) in enumerate([
         ('A1_B12','GND'), ('A4_B9','VBUS'), ('A5','CC1'), ('A6','USB_DP_CONN'),
         ('A7','USB_DM_CONN'), ('A8',None), ('B8',None), ('B7','USB_DM_CONN'),
         ('B6','USB_DP_CONN'), ('B5','CC2'), ('A9_B4','VBUS'), ('A12_B1','GND'), ('SHIELD','GND')])])
part('U_ESD', 'USBLC6-2SC6', 'sot23_6', -15, 8, 0,
     [(1,'IO1_1','USB_DP_CONN'), (2,'GND','GND'), (3,'IO2_1','USB_DM_CONN'),
      (4,'IO2_2','USB_DM_ESD'), (5,'VBUS','VBUS'), (6,'IO1_2','USB_DP_ESD')])
part('U_FLASH', 'W25Q16JVUXIQ', 'flashFootprint', 5, 9, 0,
     [(1,'CS','QSPI_SS_FLASH'), (2,'QSPI_SD1','QSPI_SD1'), (3,'QSPI_SD2','QSPI_SD2'),
      (4,'GND','GND'), (5,'QSPI_SD0','QSPI_SD0'), (6,'QSPI_SCLK','QSPI_SCLK'),
      (7,'QSPI_SD3','QSPI_SD3'), (8,'VCC','V3V3'), (9,'EP',None)])
part('Y1', 'ABM8-272-T3', 'crystalFootprint', -15, -3, 0,
     [(1,'XIN','XIN'), (2,'GND1','GND'), (3,'XOUT','XOUT_XTAL'), (4,'GND2','GND')])
part('U_LDO', 'AP2112K-3.3TRG1', 'sot23_5', -18, 0, 0,
     [(1,'VIN','VBUS'), (2,'GND','GND'), (3,'EN','VBUS'), (4,'NC',None), (5,'VOUT','V3V3')])
part('U_LOAD', 'TPS22919DCKR', 'sot363', -18, -7, 0,
     [(1,'IN','VBUS'), (2,'GND','GND'), (3,'ON','HALL_PWR_EN'),
      (4,'NC',None), (5,'QOD',None), (6,'OUT','HALL_5V')])
gh = ['HALL_5V','GND','MUX_A0','GND','MUX_A1','MUX_A2','WING_EN','GND',
      'MUX_OUT_A','GND','MUX_OUT_B','GND','MUX_OUT_C','GND']
part('J_WING', 'BM14B-GHS-TBT(LF)(SN)', 'JstGh14', 10, -16, 0,
     [(i+1, f'P{i+1}', n) for i,n in enumerate(gh)] + [(15,'MP',None)])


def resistor(ref, value, x, y, a, b, angle=0):
    part(ref, value, '0603', x, y, angle, [(1,'pin1',a), (2,'pin2',b)])


def capacitor(ref, value, x, y, rail, package='0402', angle=0):
    part(ref, value, package, x, y, angle, [(1,'pin1',rail), (2,'pin2','GND')])


for row in [
    ('R_CC1','5.1k',-21,13,'CC1','GND',90),
    ('R_CC2','5.1k',-9,16,'CC2','GND',90),
    ('R_USB_DP','27',-9,8,'USB_DP_ESD','USB_DP',0),
    ('R_USB_DM','27',-9,5,'USB_DM_ESD','USB_DM',0),
    ('R_QSPI_SS','1k',9,9,'QSPI_SS_MCU','QSPI_SS_FLASH',90),
    ('R_WING_PD','100k',-7,-12,'WING_EN','GND',0),
    ('R_HALL_PD','100k',-17,-10,'HALL_PWR_EN','GND',0),
    ('R_RUN','10k',-7,-6,'V3V3','RUN',90),
    ('R_XOUT','1k',-12,-3,'XOUT_XTAL','XOUT',90)]:
    resistor(*row)
capacitor('C_XIN','15pF',-15,-6,'XIN')
capacitor('C_XOUT','15pF',-15,0,'XOUT_XTAL')
for i, (x,y) in enumerate([(-6,4),(-6,1),(-6,-2),(0,-6),(4,-6),(6,-3),(6,0),(6,3)]):
    capacitor(f'C_MCU_HF{i+1}','100nF',x,y,'V3V3',angle=90 if i>4 else 0)
for row in [
    ('C_MCU_HF9','100nF',3,6,'V1V1','0402'),
    ('C_VREG_IN','1uF',9,3,'V3V3','0402'), ('C_VREG_OUT','1uF',9,0,'V1V1','0402'),
    ('C_MCU_BULK','10uF',9,6,'V3V3','0805'), ('C_FLASH','100nF',1,9,'V3V3','0402'),
    ('C_LDO_IN','1uF',-20,3,'VBUS','0603'), ('C_LDO_OUT','1uF',-16,3,'V3V3','0603'),
    ('C_LOAD_IN','1uF',-20,-4,'VBUS','0603'), ('C_LOAD_OUT','1uF',-12,-7,'HALL_5V','0603')]:
    capacitor(*row)
for i,ch in enumerate('ABC'):
    x = 11+i*4
    resistor(f'R_ADC_{ch}_TOP','6.8k',x,-11,f'MUX_OUT_{ch}',f'ADC_{ch}',90)
    resistor(f'R_ADC_{ch}_BOTTOM','10k',x,-7,f'ADC_{ch}','GND',90)
    capacitor(f'C_ADC_{ch}','1nF',x,-4,f'ADC_{ch}',angle=90)
for i,net in enumerate(['SWDIO','SWCLK','RUN','QSPI_SS_FLASH']):
    part('TP_'+net, None, 'testpoint:circle:1.2mm', -12+i*3, -18, 0, [(1,'pin1',net)])

if __name__ == '__main__':
    endpoints = []
    for comp in parts:
        for n, pin in comp['pins'].items():
            multiplicity = 4 if (comp['reference'], n) == ('J_USB','13') else 2 if (comp['reference'], n) == ('J_WING','15') else 1
            for land in range(multiplicity):
                endpoints.append(dict(reference=comp['reference'], source_pin=n,
                                      physical_land_index=land, **pin))
    nets = sorted({e['named_net'] for e in endpoints if e['named_net']})
    assert len(parts) == 49 and len(nets) == 37
    assert len(endpoints) == 197 and sum(e['intentional_nc'] for e in endpoints) == 30
    save(ROOT / 'source-intent.partial.json', dict(
        recorded_utc=utc(), status='PARTIAL_EXPECTATION_NOT_ACCEPTED',
        provenance='Manual transcription of hashed RepresentativeMain strategy=3 and JstGh14. No generated schematic/PCB/Circuit JSON input.',
        components=parts, named_nets=nets, physical_endpoint_intent=endpoints,
        counts=dict(components=49, named_nets=37, logical_pin_numbers=193,
                    physical_endpoints=197, required_physical_endpoints=167,
                    intentional_nc_logical_pin_numbers=29, intentional_nc_physical_endpoints=30),
        board=dict(size_mm=[48,44], copper_layers=2, thickness_mm=1.2,
                   trace_width_mm=.2, material_clearance_mm=.2, via_copper_diameter_mm=.6, via_drill_diameter_mm=.3),
        local_bond=dict(reference='J_USB', source_name='USB_SHELL_BOND', net='GND',
                        layer='top', width_mm=.2, distinct_length_mm=17,
                        source_anchor_frame_points_mm=[[-4.32,-3.13],[-4.32,1.05],[4.32,1.05],[4.32,-3.13],[4.32,1.05],[-4.32,1.05],[-4.32,-3.13]]),
        unqualified=['electrical roles for complete Main', 'every physical pad shape/dimension/drill/layer',
                     'stock footprint expansion', 'local bond anchor transform/physical attachment',
                     'complete independent physical checker and its four required negative tests']))
    save(ROOT / 'evidence/partial-expectation-freeze.json', dict(
        recorded_utc=utc(), sha256=digest(ROOT / 'source-intent.partial.json'),
        complete=False, authoring_started=False, immutable_after_freeze=True))
    print('source intent partial inventory: 49 parts, 37 nets, 193 logical pin numbers, 197 physical endpoints (167 required + 30 NC)')
