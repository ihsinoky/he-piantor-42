import json, pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-17mm-left/main.kicad_pcb')
d = json.load(open('hardware/case/issue-198-final/17mm/dimensions.json'))
t = d['wing_transforms']['left']; M = t['matrix']; T = t['translation']
holes = []
for f in b.GetFootprints():
    for pad in f.Pads():
        if pad.GetDrillSize().x > 0 and not pad.GetNetname():
            q = pad.GetPosition()
            holes.append((f.GetReference(), q.x/1e6, q.y/1e6))
print('drilled no-net pads:', holes)
for ref, kx, ky in holes:
    lx, ly = kx - 100, -ky + 100
    ax = M[0][0]*lx + M[0][1]*ly + T[0]; ay = M[1][0]*lx + M[1][1]*ly + T[1]
    print(f'{ref} kicad({kx:.2f},{ky:.2f}) -> assembly({ax:.3f},{ay:.3f})')
