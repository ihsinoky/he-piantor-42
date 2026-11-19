import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read()
src = src.split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
print('universe built; footprints ok:', all(hasattr(f, 'Pads') for f in b.GetFootprints()))
n = delete_west('SYS_3V3')
print('deleted', n)
bad = [type(f).__name__ for f in b.GetFootprints() if not hasattr(f, 'Pads')]
print('bad after delete_west:', bad)
comps, _ = net_components('SYS_3V3')
print('components:', len(comps))
