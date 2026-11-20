import sys
ARGS = sys.argv[1:]
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for net in ARGS:
    print(net, 'ripped', delete_west(net))
p.SaveBoard(DST, b)
print('saved')
