import pcbnew as p, sys
def mm(v): return v / 1e6
b = p.LoadBoard(sys.argv[1])
n = 0
for t in b.GetTracks():
    if t.GetNetname() != 'PAD_SCL' or isinstance(t, p.PCB_VIA): continue
    s, e = t.GetStart(), t.GetEnd()
    a, bb = (mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))
    if max(a[1], bb[1]) > 128.4 and min(a[0], bb[0]) > 73 and max(a[0], bb[0]) < 84:
        print('SCL trk L', t.GetLayer(), a, bb); n += 1
print(sys.argv[1], 'strip-adjacent SCL tracks:', n)
