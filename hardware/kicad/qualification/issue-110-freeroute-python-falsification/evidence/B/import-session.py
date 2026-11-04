"""Import one saved SES into a copy of the original KiCad board, without copper edits."""
import json,pathlib,shutil,sys
import pcbnew as p
E=pathlib.Path(__file__).resolve().parent; ROOT=E.parents[5]
stage=sys.argv[1]; assert stage in ('smoke','main')
old=ROOT/'hardware/kicad/qualification/issue-87-native-main-routing/evidence/processes'/('smoke-read-before' if stage=='smoke' else 'baseline-read')
work=E/'processes'/(stage+'-import'); work.mkdir(exist_ok=False)
for suffix in ['pcb','pro']: shutil.copyfile(old/('main.kicad_'+suffix),work/('main.kicad_'+suffix))
file=work/'main.kicad_pcb'; manager=p.GetSettingsManager(); manager.LoadProject(str(file.with_suffix('.kicad_pro'))); board=p.LoadBoard(str(file)); board.SetProject(manager.Prj())
if stage=='main':
    libs={}; io=p.PCB_IO_KICAD_SEXPR()
    for fp in board.GetFootprints():
        nickname=str(fp.GetFPID().GetLibNickname()); assert nickname
        lib=work/(nickname+'.pretty'); lib.mkdir(exist_ok=True); io.FootprintSave(str(lib),fp); libs[nickname]=lib
    (work/'fp-lib-table').write_text('(fp_lib_table (version 7) '+''.join(f'(lib (name "{name}")(type "KiCad")(uri "{lib}")(options "")(descr "Original fixed fixture"))' for name,lib in libs.items())+')\n')
print('KiCad',p.GetBuildVersion())
assert p.ImportSpecctraSES(board,str(E/'processes'/stage/'out.ses'))
assert p.SaveBoard(str(file),board)
assert manager.SaveProject(str(file.with_suffix('.kicad_pro')))
print('SES imported and board saved; original non-route objects retained')
