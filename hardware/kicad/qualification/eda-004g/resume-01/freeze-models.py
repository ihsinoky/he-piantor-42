"""Independent four-part role/number/position contract BEFORE packaging/tests.

Roles are explicit manufacturer/official/source-backed declarations. EP/MP are
passive physical-land annotations with source-owned NC, not invented supplies.
"""
import json
from pathlib import Path
from capture import ROOT, save, digest, utc

OLD = ROOT.parent
REPO = ROOT.parents[4]

if __name__ == '__main__':
    def pin(name,role,position,net):
        return dict(name=name,role=role,local_schematic_mm=position,net=net,nc=net is None)
    models = {
        'U_LOAD':dict(symbol='TPS22919DCKR',pins={
            '1':pin('IN','power_in',[-8.89,5.08],'VBUS'),
            '2':pin('GND','power_in',[0,-10.16],'GND'),
            '3':pin('ON','input',[-8.89,0],'HALL_PWR_EN'),
            '4':pin('NC','passive',[8.89,-5.08],None),
            '5':pin('QOD','output',[8.89,0],None),
            '6':pin('OUT','power_out',[8.89,5.08],'HALL_5V')}),
        'U_FLASH':dict(symbol='W25Q16JVUXIQ',pins={
            '1':pin('~{CS}','input',[-12.7,2.54],'QSPI_SS_FLASH'),
            '2':pin('DO(IO1)','bidirectional',[12.7,2.54],'QSPI_SD1'),
            '3':pin('~{WP}(IO2)','bidirectional',[12.7,-2.54],'QSPI_SD2'),
            '4':pin('GND','power_in',[0,-10.16],'GND'),
            '5':pin('DI(IO0)','bidirectional',[12.7,5.08],'QSPI_SD0'),
            '6':pin('CLK','input',[-12.7,-2.54],'QSPI_SCLK'),
            '7':pin('~{HOLD}(IO3)','bidirectional',[12.7,-5.08],'QSPI_SD3'),
            '8':pin('VCC','power_in',[0,10.16],'V3V3'),
            '9':pin('EP','passive',[5.08,-10.16],None)}),
        'J_USB':dict(symbol='HRO_TYPE_C_31_M_12',pins={
            '1':pin('GND','passive',[-2.54,-22.86],'GND'),
            '2':pin('VBUS','passive',[12.7,15.24],'VBUS'),
            '3':pin('CC1','bidirectional',[12.7,7.62],'CC1'),
            '4':pin('D+','bidirectional',[12.7,0],'USB_DP_CONN'),
            '5':pin('D-','bidirectional',[12.7,-7.62],'USB_DM_CONN'),
            '6':pin('SBU1','passive',[12.7,-15.24],None),
            '7':pin('SBU2','passive',[12.7,-17.78],None),
            '8':pin('D-','bidirectional',[12.7,-10.16],'USB_DM_CONN'),
            '9':pin('D+','bidirectional',[12.7,-2.54],'USB_DP_CONN'),
            '10':pin('CC2','bidirectional',[12.7,5.08],'CC2'),
            '11':pin('VBUS','passive',[12.7,12.7],'VBUS'),
            '12':pin('GND','passive',[2.54,-22.86],'GND'),
            '13':pin('SHIELD','passive',[0,-22.86],'GND')},
            old_to_source_number=dict(A1_B12='1',A4_B9='2',A5='3',A6='4',A7='5',A8='6',B8='7',B7='8',B6='9',B5='10',A9_B4='11',A12_B1='12',S1='13'),
            physical_duplicates={'13':4}, mechanical_holes=2),
        'J_WING':dict(symbol='BM14B_GHS_TBT',pins={
            **{str(i+1):pin(f'Pin_{i+1}','passive',[-5.08,round(15.24-2.54*i,6)],n)
               for i,n in enumerate(['HALL_5V','GND','MUX_A0','GND','MUX_A1','MUX_A2','WING_EN','GND','MUX_OUT_A','GND','MUX_OUT_B','GND','MUX_OUT_C','GND'])},
            '15':pin('MP','passive',[-5.08,-22.86],None)},
            physical_duplicates={'15':2}, mechanical_land_is_not_contact=True)}
    source = json.loads((OLD/'source-intent.partial.json').read_text())
    for ref,m in models.items():
        old=next(c for c in source['components'] if c['reference']==ref)
        assert set(m['pins'])==set(old['pins'])
        assert all(p['net']==old['pins'][n]['named_net'] and p['nc']==old['pins'][n]['intentional_nc'] for n,p in m['pins'].items())
    evidence = {
        'TPS22919':dict(path='hardware/jitx/.sources/datasheets/TPS22919.pdf',basis='TI SLVSEN5B p3: six functions; NC4 floating, QOD5 may float; inherited verified six-pin model and explicit typed legacy definition.'),
        'W25Q16JVUXIQ':dict(path='hardware/jitx/.sources/winbond.pdf',basis='Winbond Rev J printed p5 8-signal pin table, p67 UX physical metal D1/E1. Source EP9 is unassigned physical metal, passive annotation + NC, not a claimed manufacturer power or ninth signal pin. Floating note for ZP/UU is not falsely assigned to UX.'),
        'TYPE_C_31_M_12':dict(path='hardware/jitx/.sources/hro.pdf',basis='Exact M-12 sheet4, paired lands, 12 contacts/4 shield stakes/2 locators. Source logical aliases and source bond retained.'),
        'BM14B_GHS_TBT':dict(path='hardware/tscircuit/src/qualification/JstGh14.tsx',basis='PO-confirmed KRD-32980-5 R0, hash in source; 14 passive contacts plus two mechanical NC MP lands. D-017 interface.'),
    }
    for e in evidence.values():e['sha256']=digest(REPO/e['path'])
    contract=dict(version=1,status='FROZEN_BEFORE_PACKAGING',frozen_utc=utc(),models=models,
        independent_of_packager=True,source_intent_sha256=digest(OLD/'source-intent.partial.json'),
        evidence=evidence,allowed_symbol_only_change='Flash EP9 schematic endpoint moves from shared GND4 coordinate to (5.08,-10.16); GH adds MP physical-land annotation; USB literal number correspondence. No PCB or net changes.',
        old_default_footprints_forbidden=True,physical_geometry_qualification='Separate full Main contract required before Main generation; this role/number contract does not substitute geometry.',
        manufacturer_internal_EP_electrical_connection='Not specified for UX in inspected drawing; no supply claim or inherited GND connection. Preserve fixed source NC physical metal, with product disposition unqualified.')
    save(ROOT/'model-contract-v1.json',contract)
    save(ROOT/'evidence/model-contract-freeze-v1.json',dict(recorded_utc=utc(),sha256=digest(ROOT/'model-contract-v1.json')))
    print('four-part independent contract v1 frozen')
