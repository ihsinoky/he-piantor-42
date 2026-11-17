import math
# Headings phi: degrees from +Y axis, + toward +X (east). t = (sin phi, cos phi)
def tvec(phi):
    r = math.radians(phi); return (math.sin(r), math.cos(r))
def reflect(v, f):
    d = v[0]*f[0] + v[1]*f[1]
    return (2*d*f[0]-v[0], 2*d*f[1]-v[1])
def fold_line(tin, tout):
    sx, sy = tin[0]+tout[0], tin[1]+tout[1]
    n = math.hypot(sx, sy)
    if n < 1e-6:  # 180 deg fold: line is transverse to tin
        return (-tin[1], tin[0])
    return (sx/n, sy/n)

# Right side headings (deg): T0->A, A->B, B->S1 (climb line), S1->S2, S2->V7, V7->T1
heads = [-4.4, -116.9, 2.66, -177.34, 2.66, 43.0]
def transport(heads):
    # s0 = R-90(t0): (x,y)->(y,-x) applied to t0
    t0 = tvec(heads[0]); s = (t0[1], -t0[0])
    flips = 0
    for i in range(len(heads)-1):
        tin, tout = tvec(heads[i]), tvec(heads[i+1])
        f = fold_line(tin, tout)
        s = reflect(s, f); flips += 1
    tf = tvec(heads[-1]); sref = (tf[1], -tf[0])
    dot = s[0]*sref[0] + s[1]*sref[1]
    return flips, s, sref, dot
fl, s, sref, dot = transport(heads)
print('RIGHT: folds =', fl, ' s_final =', [round(x,3) for x in s], ' s_ref(Main frame) =', [round(x,3) for x in sref], ' dot =', round(dot,3))
print('RIGHT mapping:', 'IDENTITY (k -> k)' if dot > 0 else 'REVERSAL (k -> 15-k)')
# Left side: mirrored headings phi -> -phi, final approach yaw +38 class: mirror of right with Main yaw 38 vs 43
headsL = [4.4, 116.9, -2.66, 177.34, -2.66, -38.0]
fl, s, sref, dot = transport(headsL)
print('LEFT: folds =', fl, ' dot =', round(dot,3), ' mapping:', 'IDENTITY (k -> k)' if dot > 0 else 'REVERSAL (k -> 15-k)')

# Length budget (mm), right side, leg2 = absorber
segs = {'T0->A': 23.57, 'A->B': 15.50, 'B->S1 (incl climb extra)': 46.90, 'S2->V7': 29.61, 'V7->T1': 12.87}
base = sum(segs.values())
for L in (148, 150, 152, 154, 156):
    leg2 = L - base
    print(f'cable {L} mm -> leg2 (S-pair southbound run) = {leg2:.1f} mm')
