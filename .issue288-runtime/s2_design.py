"""Issue #288 Stage 2 design data: components, pin->net map, symbol geometry.

Single source used by the schematic generator and the PCB builder.
The independent gate checks (schematic netlist vs placed PCB pads) are
generated from the two artifacts, not from this table.
"""

# ---------------------------------------------------------------- symbols
# pin: (number, name, etype, side, local_y)  side 'L' pins point left (rot 0),
# 'R' pins point right (rot 180). Local coords: y up, body half-width per symbol.
SYMBOLS = {
    'TMAG5253': dict(hw=5.08, pins=[
        ('1', 'VCC', 'power_in', 'L', 5.08), ('2', 'GND', 'power_in', 'L', 2.54),
        ('3', 'EN', 'input', 'L', -2.54), ('5', 'EP', 'passive', 'L', -5.08),
        ('4', 'OUT', 'output', 'R', 0.0)]),
    'TMUX1208': dict(hw=7.62, pins=[
        ('13', 'VDD', 'power_in', 'L', 7.62), ('14', 'GND', 'power_in', 'L', 5.08),
        ('1', 'A0', 'input', 'L', 2.54), ('16', 'A1', 'input', 'L', 0.0),
        ('15', 'A2', 'input', 'L', -2.54), ('2', 'EN', 'input', 'L', -5.08),
        ('3', 'VSS', 'power_in', 'L', -7.62),
        ('4', 'S1', 'passive', 'R', 10.16), ('5', 'S2', 'passive', 'R', 7.62),
        ('6', 'S3', 'passive', 'R', 5.08), ('7', 'S4', 'passive', 'R', 2.54),
        ('8', 'D', 'passive', 'R', 0.0), ('12', 'S5', 'passive', 'R', -2.54),
        ('11', 'S6', 'passive', 'R', -5.08), ('10', 'S7', 'passive', 'R', -7.62),
        ('9', 'S8', 'passive', 'R', -10.16)]),
    'XIAO': dict(hw=7.62, pins=[
        ('1', 'D0', 'bidirectional', 'L', 7.62), ('2', 'D1', 'bidirectional', 'L', 5.08),
        ('3', 'D2', 'bidirectional', 'L', 2.54), ('4', 'D3', 'bidirectional', 'L', 0.0),
        ('5', 'D4', 'bidirectional', 'L', -2.54), ('6', 'D5', 'bidirectional', 'L', -5.08),
        ('7', 'D6', 'bidirectional', 'L', -7.62),
        ('8', 'D7', 'bidirectional', 'R', 7.62), ('9', 'D8', 'bidirectional', 'R', 5.08),
        ('10', 'D9', 'bidirectional', 'R', 2.54), ('11', 'D10', 'bidirectional', 'R', 0.0),
        ('12', '3V3', 'power_out', 'R', -2.54), ('13', 'GND', 'power_in', 'R', -5.08),
        ('14', 'VBUS', 'power_in', 'R', -7.62)]),
    'AP2112': dict(hw=5.08, pins=[
        ('1', 'VIN', 'power_in', 'L', 2.54), ('2', 'GND', 'power_in', 'L', 0.0),
        ('3', 'EN', 'input', 'L', -2.54),
        ('5', 'VOUT', 'power_out', 'R', 2.54), ('4', 'NC', 'passive', 'R', -2.54)]),
    'AO3401A': dict(hw=5.08, pins=[
        ('2', 'S', 'passive', 'L', 2.54), ('1', 'G', 'input', 'L', -2.54),
        ('3', 'D', 'passive', 'R', 0.0)]),
    'USB_C': dict(hw=7.62, pins=[
        ('2', 'VBUS', 'passive', 'L', 7.62), ('11', 'VBUS', 'passive', 'L', 5.08),
        ('3', 'CC1', 'passive', 'L', 2.54), ('10', 'CC2', 'passive', 'L', 0.0),
        ('4', 'DP1', 'passive', 'L', -2.54), ('9', 'DP2', 'passive', 'L', -5.08),
        ('5', 'DM1', 'passive', 'L', -7.62), ('8', 'DM2', 'passive', 'L', -10.16),
        ('1', 'GND', 'passive', 'R', 5.08), ('12', 'GND', 'passive', 'R', 2.54),
        ('13', 'SHIELD', 'passive', 'R', 0.0), ('6', 'SBU1', 'passive', 'R', -2.54),
        ('7', 'SBU2', 'passive', 'R', -5.08)]),
    'CONN2': dict(hw=3.81, pins=[
        ('1', 'P1', 'passive', 'L', 2.54), ('2', 'P2', 'passive', 'L', -2.54)]),
    'R': dict(hw=3.81, pins=[
        ('1', '1', 'passive', 'L', 0.0), ('2', '2', 'passive', 'R', 0.0)]),
    'C': dict(hw=3.81, pins=[
        ('1', '1', 'passive', 'L', 0.0), ('2', '2', 'passive', 'R', 0.0)]),
    'LED': dict(hw=3.81, pins=[
        ('1', 'A', 'passive', 'L', 0.0), ('2', 'K', 'passive', 'R', 0.0)]),
    'TP': dict(hw=0.0, pins=[('1', '1', 'passive', 'T', 0.0)]),
}

FOOTPRINTS = {
    'TMAG5253': 'wmatrix:TMAG5253BA3_X2SON-4',
    'TMUX1208': 'wmatrix:TMUX1208PWR_TSSOP-16',
    'XIAO': 'wmatrix:XIAO_nRF52840_SOCKET',
    'AP2112': 'wmatrix:AP2112_SOT-23-5',
    'AO3401A': 'wmatrix:AO3401A_SOT-23',
    'USB_C': 'wmatrix:TYPE-C-31-M-12',
    'CONN2': 'wmatrix:JST_XH_B2B-XH-A_1x02',
    'R': 'wmatrix:R_0603',
    'C': 'wmatrix:C_0603',
    'LED': 'wmatrix:LED_0805',
    'TP': 'wmatrix:TP_1.2mm',
}

NC = 'NC'  # sentinel: pin gets a no_connect marker

# ---------------------------------------------------------------- netlist
COMPONENTS = []  # (ref, symbol, value, {pin: net})


def add(ref, sym, value, pins):
    COMPONENTS.append((ref, sym, value, pins))


for g in 'ABC':
    for i in range(6):
        add(f'U_H{g}{i}', 'TMAG5253', 'TMAG5253BA3IQDMRR',
            {'1': 'HALL_3V3', '2': 'GND', '3': f'EN_{g}', '4': f'H_{g}{i}_RAW', '5': 'GND'})
        add(f'C_H{g}{i}', 'C', '100nF', {'1': 'HALL_3V3', '2': 'GND'})
    add(f'U_MUX{g}', 'TMUX1208', 'TMUX1208PWR',
        {'1': 'MUX_A0', '2': 'HALL_3V3', '3': 'GND',
         '4': f'H_{g}0_RAW', '5': f'H_{g}1_RAW', '6': f'H_{g}2_RAW', '7': f'H_{g}3_RAW',
         '8': f'MUX{g}_OUT', '9': 'REF_RAIL', '10': 'GND',
         '11': f'H_{g}5_RAW', '12': f'H_{g}4_RAW',
         '13': 'HALL_3V3', '14': 'GND', '15': 'MUX_A2', '16': 'MUX_A1'})
    add(f'C_MUX{g}', 'C', '100nF', {'1': 'HALL_3V3', '2': 'GND'})

add('U_XIAO', 'XIAO', 'XIAO nRF52840 (socket, hand-fit)',
    {'1': 'MUXA_OUT', '2': 'MUXB_OUT', '3': 'MUXC_OUT', '4': 'EN_C', '5': NC,
     '6': 'LED_DRV', '7': 'MUX_A0', '8': 'MUX_A1', '9': 'MUX_A2', '10': 'EN_A',
     '11': 'EN_B', '12': NC, '13': 'GND', '14': 'VIN'})
add('R_LED', 'R', '1k', {'1': 'LED_DRV', '2': 'LED_A'})
add('D_LED', 'LED', 'KT-0805G green', {'1': 'LED_A', '2': 'GND'})

add('J_USB', 'USB_C', 'TYPE-C-31-M-12',
    {'1': 'GND', '2': 'VIN_SRC', '3': 'CC1', '4': NC, '5': NC, '6': NC, '7': NC,
     '8': NC, '9': NC, '10': 'CC2', '11': 'VIN_SRC', '12': 'GND', '13': 'GND'})
add('R_CC1', 'R', '5.1k', {'1': 'CC1', '2': 'GND'})
add('R_CC2', 'R', '5.1k', {'1': 'CC2', '2': 'GND'})
add('J_BATT', 'CONN2', 'B2B-XH-A', {'1': 'VIN_SRC', '2': 'GND'})
add('Q_PROT', 'AO3401A', 'AO3401A', {'1': 'GND', '2': 'VIN_SRC', '3': 'VIN'})
add('U_LDO', 'AP2112', 'AP2112K-3.3TRG1',
    {'1': 'VIN', '2': 'GND', '3': 'VIN', '4': NC, '5': 'HALL_3V3_SRC'})
add('C_LDO_IN', 'C', '10uF', {'1': 'VIN', '2': 'GND'})
add('C_LDO_OUT', 'C', '10uF', {'1': 'HALL_3V3_SRC', '2': 'GND'})
add('R_SHUNT', 'R', '0R (current-shunt position)', {'1': 'HALL_3V3_SRC', '2': 'HALL_3V3'})
add('R_DIV1', 'R', '10k', {'1': 'HALL_3V3', '2': 'REF_RAIL'})
add('R_DIV2', 'R', '10k', {'1': 'REF_RAIL', '2': 'GND'})

TPS = {
    'TP_VIN_SRC': 'VIN_SRC', 'TP_VIN': 'VIN', 'TP_3V3_SRC': 'HALL_3V3_SRC',
    'TP_RAIL_N': 'HALL_3V3', 'TP_RAIL_E': 'HALL_3V3',
    'TP_MUXA': 'MUXA_OUT', 'TP_MUXB': 'MUXB_OUT', 'TP_MUXC': 'MUXC_OUT',
    'TP_A0': 'MUX_A0', 'TP_A1': 'MUX_A1', 'TP_A2': 'MUX_A2',
    'TP_EN_A': 'EN_A', 'TP_EN_B': 'EN_B', 'TP_EN_C': 'EN_C',
    'TP_REF': 'REF_RAIL',
    'TP_GND_A': 'GND', 'TP_GND_B': 'GND', 'TP_GND_C': 'GND', 'TP_GND_D': 'GND',
    'TP_H16_CTR': 'H_B1_RAW', 'TP_H16_N': 'H_B0_RAW', 'TP_H16_DIAG': 'H_A0_RAW',
    'TP_H17_CTR': 'H_B4_RAW', 'TP_H17_N': 'H_B3_RAW', 'TP_H17_DIAG': 'H_A3_RAW',
}
for ref, net in TPS.items():
    add(ref, 'TP', 'TestPoint', {'1': net})

# nets that receive a PWR_FLAG in the schematic (ERC power-driver rule)
PWR_FLAG_NETS = ['VIN_SRC', 'VIN', 'HALL_3V3_SRC', 'HALL_3V3', 'GND']

if __name__ == '__main__':
    nets = {}
    for ref, sym, val, pins in COMPONENTS:
        for p, n in pins.items():
            if n != NC:
                nets.setdefault(n, []).append(f'{ref}.{p}')
    print(f'{len(COMPONENTS)} components, {len(nets)} nets')
    for n in sorted(nets):
        print(f'  {n}: {len(nets[n])} pins')
