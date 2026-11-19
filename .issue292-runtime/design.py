"""Issue #292 wireless Main — single source of truth: parts, pins->nets.
None = no-connect. Symbol pin names come from SYMBOLS below."""

# ISP1807 pin names (datasheet R19 section 3)
ISP_PINS = {
 1:'VSS',2:'P0.09/NFC1',3:'P0.12',4:'P0.10/NFC2',5:'P0.14',6:'P0.26',7:'VSS',
 8:'D+',9:'P0.16',10:'D-',11:'P0.21',12:'VBUS',13:'P0.18/RESET',14:'VSS',
 15:'P0.20',16:'VSS',17:'P0.22',18:'VSS',19:'P0.24',20:'OUT_ANT',21:'VSS',
 22:'OUT_MOD',23:'VSS',24:'VSS',25:'VSS',26:'VCC_nRF',27:'P0.17',28:'SWDIO',
 29:'P0.13',30:'SWDCLK',31:'VSS',32:'P0.08',33:'P0.07',34:'P0.06',
 35:'P0.04/AIN2',36:'P0.05/AIN3',37:'P0.15',38:'P0.03/AIN1',39:'P0.27',
 40:'P0.02/AIN0',41:'P0.25',42:'P0.31/AIN7',43:'P0.11',44:'P0.30/AIN6',
 45:'P0.19',46:'P0.29/AIN5',47:'P0.23',48:'P0.28/AIN4',49:'P1.02',50:'P1.06',
 51:'P1.15',52:'P1.14',53:'P1.13',54:'P1.05',55:'P1.08',56:'P1.09',
 57:'P1.00',58:'P1.03',59:'P1.12',60:'P1.10',61:'P1.11',62:'P1.07',
 63:'P1.04',64:'P1.01'}
for _i in range(65, 79):
    ISP_PINS[_i] = 'NC'

U1 = {1:'GND',7:'GND',14:'GND',16:'GND',18:'GND',21:'GND',23:'GND',24:'GND',
      25:'GND',31:'GND',
      3:'PAD_SCL',5:'MUX_A0',6:'MUX_A1',8:'USB_DP',9:'MUX_A2',10:'USB_DM',
      12:'VBUS',13:'RESET_N',15:'HALL_PWR_EN',17:'MUX_EN0',19:'MUX_EN1',
      20:'ANT_LINK',22:'ANT_LINK',26:'SYS_3V3',27:'VBAT_GATE',28:'SWDIO',
      50:'PAD_DR',30:'SWDCLK',32:'PAD_SDA',33:'PAD_EN',47:'BTN',
      40:'VBAT_SENSE',42:'ADC_C',46:'ADC_B',48:'ADC_A',56:'LED_DRV'}
for _i in range(1, 79):
    U1.setdefault(_i, None)

FH12_J2 = {'1':'GND','2':'MUX_OUT_C','3':'GND','4':'MUX_OUT_B','5':'GND',
 '6':'MUX_OUT_A','7':'GND','8':'MUX_EN0','9':'MUX_A2','10':'MUX_A1',
 '11':'GND','12':'MUX_A0','13':'GND','14':'HALL_3V3','MP':None}
FH12_J3 = dict(FH12_J2, **{'8':'MUX_EN1'})

PARTS = [
 # ref, value, symbol, footprint, pins {num: net}
 ('U1','ISP1807-LR','ISP1807','ISP1807-LR', {str(k): v for k, v in U1.items()}),
 ('U2','TPS63070RNMR','TPS63070','TPS63070RNMR',
  {'1':'GND','2':'CONV_PG','3':'VAUX','4':'GND','5':'FB_3V3','6':'GND',
   '7':'SYS_3V3','8':'SYS_3V3','9':'SW_B','10':'GND','11':'SW_A',
   '12':'VIN_IN','13':'VIN_IN','14':'VIN_IN','15':'GND'}),
 ('L1','1.5uH XFL4020-152MEC','L','XFL4020', {'1':'SW_A','2':'SW_B'}),
 ('CIN1','22uF','C','C_0805', {'1':'VIN_IN','2':'GND'}),
 ('CIN2','22uF','C','C_0805', {'1':'VIN_IN','2':'GND'}),
 ('COUT1','22uF','C','C_0805', {'1':'SYS_3V3','2':'GND'}),
 ('COUT2','22uF','C','C_0805', {'1':'SYS_3V3','2':'GND'}),
 ('CVAUX','1uF','C','C_0603', {'1':'VAUX','2':'GND'}),
 ('RFB1','49.9k','R','R_0603', {'1':'SYS_3V3','2':'FB_3V3'}),
 ('RFB2','16.0k','R','R_0603', {'1':'FB_3V3','2':'GND'}),
 ('RPG','100k','R','R_0603', {'1':'SYS_3V3','2':'CONV_PG'}),
 ('D1','PMEG4020','D','SOD-123', {'1':'VIN_IN','2':'VBUS'}),   # 1=K, 2=A
 ('D2','PMEG4020','D','SOD-123', {'1':'VIN_IN','2':'VBAT+'}),  # 1=K, 2=A
 ('JBATT','B2B-XH-A','CONN2','GH2', {'1':'VBAT+','2':'GND'}),
 ('U3','TPS22919DCKR','TPS22919','TPS22919DCKR',
  {'1':'SYS_3V3','2':'GND','3':'HALL_PWR_EN','4':None,'5':None,'6':'HALL_3V3'}),
 ('U4','TPS22919DCKR','TPS22919','TPS22919DCKR',
  {'1':'SYS_3V3','2':'GND','3':'PAD_EN','4':None,'5':None,'6':'PAD_3V3'}),
 ('CHIN','1uF','C','C_0603', {'1':'SYS_3V3','2':'GND'}),
 ('CHOUT','1uF','C','C_0603', {'1':'HALL_3V3','2':'GND'}),
 ('CPOUT','1uF','C','C_0603', {'1':'PAD_3V3','2':'GND'}),
 ('RPD1','100k','R','R_0603', {'1':'HALL_PWR_EN','2':'GND'}),
 ('RPD2','100k','R','R_0603', {'1':'MUX_EN0','2':'GND'}),
 ('RPD3','100k','R','R_0603', {'1':'MUX_EN1','2':'GND'}),
 ('J2','FH12-14S-0.5SH(55)','FH12','FH12-14S-0.5SH', FH12_J2),
 ('J3','FH12-14S-0.5SH(55)','FH12','FH12-14S-0.5SH', FH12_J3),
 ('RFA','6.8k','R','R_0603', {'1':'MUX_OUT_A','2':'ADC_A'}),
 ('RFB','6.8k','R','R_0603', {'1':'MUX_OUT_B','2':'ADC_B'}),
 ('RFC','6.8k','R','R_0603', {'1':'MUX_OUT_C','2':'ADC_C'}),
 ('CFA','1nF','C','C_0603', {'1':'ADC_A','2':'GND'}),
 ('CFB','1nF','C','C_0603', {'1':'ADC_B','2':'GND'}),
 ('CFC','1nF','C','C_0603', {'1':'ADC_C','2':'GND'}),
 ('RV1','1M','R','R_0603', {'1':'VBAT+','2':'VBAT_SENSE'}),
 ('RV2','1M','R','R_0603', {'1':'VBAT_SENSE','2':'VBAT_DRAIN'}),
 ('Q1','2N7002','SOT23','SOT-23', {'1':'VBAT_GATE','2':'GND','3':'VBAT_DRAIN'}),
 ('RVG','100k','R','R_0603', {'1':'VBAT_GATE_M','2':'VBAT_GATE'}),
 ('RVPD','100k','R','R_0603', {'1':'VBAT_GATE','2':'GND'}),
 ('CVS','10nF','C','C_0603', {'1':'VBAT_SENSE','2':'GND'}),
 ('J4','781710004 (Fly link)','EZMATE','Pico-EZmate_781710004',
  {'1':'VBUS','2':'USB_DM','3':'USB_DP','4':'GND'}),
 ('JPAD','FH12-6S-class FFC','FFC6','FFC6_0.5mm_land',
  {'1':'PAD_3V3','2':'GND','3':'PAD_SCL','4':'PAD_SDA','5':'PAD_DR','6':'GND','MP':None}),
 ('RPU1','4.7k','R','R_0603', {'1':'PAD_3V3','2':'PAD_SCL'}),
 ('RPU2','4.7k','R','R_0603', {'1':'PAD_3V3','2':'PAD_SDA'}),
 ('JSWD','TC2030-IDC-NL','TC2030','TC2030-IDC-NL_Pads',
  {'1':'SYS_3V3','2':'SWDIO','3':'RESET_N','4':'SWDCLK','5':'GND','6':None}),
 ('RLED','1k','R','R_0603', {'1':'LED_DRV','2':'LED_A'}),
 ('DLED','LED green','LED','R_0603', {'1':'LED_A','2':'GND'}),
 ('SW1','TACT (bring-up)','TACT','TACT_2pad', {'1':'BTN','2':'GND'}),
 ('RRST','10k','R','R_0603', {'1':'SYS_3V3','2':'RESET_N'}),
 ('CVCC1','1uF','C','C_0603', {'1':'SYS_3V3','2':'GND'}),
 ('CVCC2','100nF','C','C_0603', {'1':'SYS_3V3','2':'GND'}),
 ('TP1','TP VIN_IN','TP','TestPoint', {'1':'VIN_IN'}),
 ('TP2','TP SYS_3V3','TP','TestPoint', {'1':'SYS_3V3'}),
 ('TP3','TP HALL_3V3','TP','TestPoint', {'1':'HALL_3V3'}),
 ('TP4','TP PAD_3V3','TP','TestPoint', {'1':'PAD_3V3'}),
 ('TP5','TP GND','TP','TestPoint', {'1':'GND'}),
 ('H1','NPTH 2.2mm','MH','MountingHole_2.2mm', {'1':None}),
 ('H2','NPTH 2.2mm','MH','MountingHole_2.2mm', {'1':None}),
 ('H3','NPTH 2.2mm','MH','MountingHole_2.2mm', {'1':None}),
]
# fix: U1 gate drive net name (module pin 27 drives RVG input)
PARTS[0][4]['27'] = 'VBAT_GATE_M'

POWER_NETS = ['GND','SYS_3V3','VIN_IN','VBAT+','VBUS','HALL_3V3','PAD_3V3']

# symbol pin layouts: name -> (left [(num,name)], right [(num,name)])
def _two(n1, n2):
    return ([('1', n1)], [('2', n2)])
SYMBOLS = {
 'R': _two('', ''), 'C': _two('', ''), 'L': _two('', ''),
 'D': ([('1', 'K')], [('2', 'A')]),
 'LED': ([('1', 'A')], [('2', 'K')]),
 'TP': ([('1', '')], []),
 'MH': ([('1', '')], []),
 'CONN2': _two('+', '-'),
 'TACT': _two('', ''),
 'SOT23': ([('1', 'G'), ('2', 'S')], [('3', 'D')]),
 'TPS22919': ([('1', 'IN'), ('2', 'GND'), ('3', 'ON')], [('6', 'OUT'), ('5', 'QOD'), ('4', 'NC')]),
 'TPS63070': ([('12', 'VIN'), ('13', 'VIN'), ('14', 'EN'), ('3', 'VAUX'), ('2', 'PG')],
              [('7', 'VOUT'), ('8', 'VOUT'), ('11', 'L1'), ('9', 'L2'), ('5', 'FB'),
               ('1', 'GND'), ('4', 'GND'), ('6', 'GND'), ('10', 'GND'), ('15', 'GND')]),
 'EZMATE': ([('1', 'VBUS'), ('2', 'D-')], [('3', 'D+'), ('4', 'GND')]),
 'FH12': ([(str(i), '') for i in range(1, 8)], [(str(i), '') for i in range(8, 15)] + [('MP', 'MP')]),
 'FFC6': ([('1', ''), ('2', ''), ('3', '')], [('4', ''), ('5', ''), ('6', ''), ('MP', 'MP')]),
 'TC2030': ([('1', 'VTREF'), ('2', 'SWDIO'), ('3', 'RESET')], [('4', 'SWDCLK'), ('5', 'GND'), ('6', 'SWO')]),
 'ISP1807': ([(str(i), ISP_PINS[i]) for i in range(1, 40)],
             [(str(i), ISP_PINS[i]) for i in range(40, 79)]),
}
