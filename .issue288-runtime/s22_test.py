import pcbnew
T = '/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix'
for name in ('TMAG5253BA3_X2SON-4', 'XIAO_nRF52840_SOCKET', 'AP2112_SOT-23-5', 'AO3401A_SOT-23',
             'JST_XH_B2B-XH-A_1x02', 'LED_0805', 'C_0603', 'R_0603', 'TP_1.2mm', 'NPTH_2.2mm',
             'TMUX1208PWR_TSSOP-16', 'TYPE-C-31-M-12'):
    try:
        fp = pcbnew.FootprintLoad(f'{T}/wmatrix.pretty', name)
        pads = [(p.GetNumber(), round(p.GetPosition().x / 1e6, 3), round(p.GetPosition().y / 1e6, 3)) for p in fp.Pads()]
        print(name, 'OK', pads if len(pads) <= 16 else f'{len(pads)} pads')
    except Exception as e:
        print(name, 'FAIL', type(e).__name__, str(e)[:120])
