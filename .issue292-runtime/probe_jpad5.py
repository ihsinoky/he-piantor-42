import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for lay in PAD_INDEX.get('PAD_DR', []):
    ref, sh = lay[1], lay[0]
    if ref.startswith('JPAD'):
        print('JPAD PAD_DR pad bounds', [round(v, 3) for v in sh['F'].bounds])
