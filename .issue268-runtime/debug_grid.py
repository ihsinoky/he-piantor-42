exec(open('.issue268-runtime/bridge_base.py').read())
blocked = raster_blocked('GND', 0.3)
# x 102.30..103.20 step .05 -> cols; y 132.40 down to 130.00 rows
print('     ' + ''.join(str(int((102.30+0.05*i)*100) % 10) for i in range(19)))
for j in range(49):
    y = 132.40 - 0.05*j
    iy = int(round((y - WIN[2])/STEP))
    row = ''
    for i in range(19):
        x = 102.30 + 0.05*i
        ix = int(round((x - WIN[0])/STEP))
        row += '#' if blocked[1][iy, ix] else '.'
    print('%.2f %s' % (y, row))
