import json, math
exec(open('.issue275-runtime/analysis.py').read().split("PAD_R")[0])  # reuse parse + pads_at + cands

def capsule_pts(centre, rot):
    # FH12 signal land 0.30 x 1.30 (Stage 2d corrected land), capsule r=0.15
    out = []
    for num, ux, uy in locals_:
        rx, ry = rot2d(ux, uy, rot)
        cx, cy = centre[0]+rx, centre[1]+ry
        # land long axis = footprint local Y (pads face along local +Y? use pad rot)
        out.append((num, cx, cy))
    return out

def pad_capsule_centres(centre, rot, num):
    # three sample centres along the land's long axis (local pad orientation:
    # FH12 lands are elongated along the connector's insertion axis = local Y of pad)
    ux, uy = next((a, b) for n, a, b in locals_ if n == num)
    rx, ry = rot2d(ux, uy, rot)
    cx, cy = centre[0]+rx, centre[1]+ry
    # pad local rotation in footprint frame: recover from J2 pose (pad rot - footprint rot)
    return (cx, cy)

# Build pad rect sample points: for each pad, sample its capsule axis using the
# pad's own rotation stored in extract (abs rot at J2 pose -> local direction).
j2pads = {p['num']: p for p in j2['pads']}
def pad_samples(centre, rot):
    samples = []  # (num, x, y) capsule spine points, r=0.15
    for num, ux, uy in locals_:
        rx, ry = rot2d(ux, uy, rot)
        cx, cy = centre[0]+rx, centre[1]+ry
        # land axis direction: at J2 pose, pad abs rot = prot; local axis dir:
        prot = j2pads[num]['rot']  # abs at J2 pose (includes J2 rot 38)
        axis_local = prot - j2['rot']  # direction of pad's own rotation in fp frame
        ax, ay = rot2d(math.sin(math.radians(axis_local)), -math.cos(math.radians(axis_local)), rot)
        # KiCad pad rot 0 => land long axis along local Y; spine offsets +-0.5
        for t in (-0.5, 0.0, 0.5):
            samples.append((num, cx+ax*t, cy+ay*t))
    return samples

def clearance_report(site, centre, rot):
    site_nets = {p['net'][1] for p in fp(site)['pads'] if p['net']}
    samples = pad_samples(centre, rot)
    hard, band = [], []
    for (a, b, w, lay, net) in segs:
        if net in site_nets: continue
        dm = min(seg_pt_dist(a, b, (x, y)) for _, x, y in samples) - w/2 - 0.15
        if dm < 0.10: hard.append(('seg', net, lay, round(dm, 3)))
        elif dm < 0.30: band.append(('seg', net, lay, round(dm, 3)))
    for (p, sz, net) in vias:
        if net in site_nets: continue
        dm = min(math.hypot(p[0]-x, p[1]-y) for _, x, y in samples) - sz/2 - 0.15
        if dm < 0.10: hard.append(('via', net, '', round(dm, 3)))
        elif dm < 0.30: band.append(('via', net, '', round(dm, 3)))
    return hard, band

for label, site, pose in (('OLD', 'J2', J2P), ('OLD', 'J3', J3P),
                          ('a', 'J3', cands['a_mirror_J2']['J3']),
                          ('b', 'J2', cands['b_mirror_J3']['J2']),
                          ('c', 'J2', cands['c_middle']['J2']),
                          ('c', 'J3', cands['c_middle']['J3'])):
    h, b = clearance_report(site, pose[0], pose[1])
    print(label, site, 'hard(<0.10):', len(h), h[:4], ' band(0.10-0.30):', len(b), b[:4])
