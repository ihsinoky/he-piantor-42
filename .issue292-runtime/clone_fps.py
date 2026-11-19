"""Clone donor footprints from Rev.10 .kicad_pcb text into wmain.pretty."""
import sys
sys.path.insert(0, '.')
from sexpr import parse, ser, atom, is_str
from pathlib import Path
E = Path('.').resolve()
W = E.parent
TREE = W/'hardware/kicad/qualification/issue-292-wmain'
LIB = TREE/'wmain.pretty'
LIB.mkdir(parents=True, exist_ok=True)
src = (W/'hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb').read_text()
tree = parse(src)

clone = {'J2': 'FH12-14S-0.5SH', 'U6': 'TPS63070RNMR', 'U5': 'TPS22919DCKR',
         'L1': 'XFL4020', 'C26': 'C_1210', 'C23': 'C_0805', 'R17': 'R_0603',
         'C18': 'C_0603', 'TP1': 'TestPoint', 'J4': 'Pico-EZmate_781710004',
         'H1': 'MountingHole_2.2mm'}

def ref_of(fp):
    for ch in fp[1:]:
        if isinstance(ch, list) and ch and ch[0] == 'property' and atom(ch[1]) == 'Reference':
            return atom(ch[2])
    return None

def clean(fp, newname):
    out = []
    for ch in fp:
        if isinstance(ch, list) and ch:
            h = ch[0]
            if h in ('at', 'path', 'sheetname', 'sheetfile', 'model', 'uuid'):
                continue
            if h == 'pad':
                pad = [c for c in ch if not (isinstance(c, list) and c and c[0] in ('net', 'uuid', 'pinfunction', 'pintype'))]
                out.append(pad)
                continue
            if h == 'property' and atom(ch[1]) == 'Footprint':
                ch = ['property', ('str', 'Footprint'), ('str', 'wmain:' + newname)] + ch[3:]
            out.append(ch)
        elif isinstance(ch, tuple) and ch[0] == 'str' and fp.index(ch) == 1:
            out.append(('str', newname))
        else:
            out.append(ch)
    # rename: second element is the quoted lib name
    out[1] = ('str', newname)
    return out

found = {}
for ch in tree[1:]:
    if isinstance(ch, list) and ch and ch[0] == 'footprint':
        r = ref_of(ch)
        if r in clone and r not in found:
            found[r] = ch
for ref, name in clone.items():
    assert ref in found, ref
    fp = clean(found[ref], name)
    (LIB/(name + '.kicad_mod')).write_text(ser(fp) + '\n')
    print('cloned', ref, '->', name)
