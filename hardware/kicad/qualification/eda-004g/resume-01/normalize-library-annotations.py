"""Two official symbol editorial metadata compatibility corrections only.

KiCad 9 `property private name value` is misread by pinned KSA as name=private,
value=name and a bare unquoted value. Preserve annotation name/value/effects as
ordinary hidden properties in INPUT libraries using public parser/serializer.
No pin, shape, role, symbol placement, PCB or generated output edits.
"""
import sexpdata as sx
from capture import ROOT,save,digest,utc
selected={'MCU_RaspberryPi':'RP2040','Device':'Crystal_GND24'}
changes=[]
for lib,name in selected.items():
    path=ROOT/'library'/f'{lib}.kicad_sym';before=digest(path)
    original=ROOT/'evidence'/f'{lib}-before-annotation-compatibility.kicad_sym.gz'
    import gzip
    original.write_bytes(gzip.compress(path.read_bytes(),mtime=0))
    tree=sx.loads(path.read_text());node=next(x for x in tree if isinstance(x,list) and str(x[0])=='symbol' and x[1]==name)
    for x in node:
        if isinstance(x,list) and str(x[0])=='property' and x[1]==sx.Symbol('private'):
            assert len(x)>4 and isinstance(x[2],str) and isinstance(x[3],str)
            changes.append(dict(library=lib,symbol=name,name=x[2],value=x[3],only_removed_syntax_marker='private'))
            del x[1]
    path.write_text(sx.dumps(tree)+'\n')
    for item in changes:
        if item['library']==lib:item.update(before_sha256=before,after_sha256=digest(path))
save(ROOT/'evidence/library-annotation-compatibility.json',dict(utc=utc(),changes=changes,scope='Editorial private attribute syntax only; original data preserved; no private API used. Definitions/pins/roles/graphics unchanged. New generator input, never generated-output patch.'))
print('input annotation syntax normalized',len(changes))
