exec(open('.issue268-runtime/bridge_base.py').read())
blocked = raster_blocked('GND', 0.3)
def cell(x, y):
    ix = int(round((x-WIN[0])/STEP)); iy = int(round((y-WIN[2])/STEP))
    return blocked[1][iy, ix]
for y in (129.95, 129.90, 129.85, 129.80, 129.75, 129.70, 129.65, 129.60):
    print('y=%.2f' % y, ''.join('#' if cell(98.60+0.05*i, y) else '.' for i in range(7)), ' (x 98.60..98.90)')
