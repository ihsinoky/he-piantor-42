"""Supply the original fixture footprint library for KiCad inspection (no board edits)."""
import pathlib,pcbnew as p
E=pathlib.Path(__file__).resolve().parent; ROOT=E.parents[4]; work=E/'processes/smoke-import'
original=ROOT/'hardware/kicad/qualification/issue-87-native-main-routing/evidence/processes/smoke-read-before/main.kicad_pcb'
board=p.LoadBoard(str(original)); lib=work/'Probe.pretty'; lib.mkdir(exist_ok=False); io=p.PCB_IO_KICAD_SEXPR()
for fp in board.GetFootprints(): io.FootprintSave(str(lib),fp)
(work/'fp-lib-table').write_text(f'(fp_lib_table (version 7) (lib (name "Probe")(type "KiCad")(uri "{lib}")(options "")(descr "Original smoke fixture")))\n')
print('Original footprints saved for library resolution; input and returned boards unchanged')
