import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census as cz
from collections import Counter

def summ(path_a, path_b, label):
    ca, na, ga = cz.census(path_a)
    cb, nb, gb = cz.census(path_b)
    print(f"== {label} ==")
    print("counts base :", dict(ca))
    print("counts final:", dict(cb))
    ob, of = na - nb, nb - na
    def kind(k): return k[0]
    for name, s in (("non-GND only-in-base", ob), ("non-GND only-in-final", of)):
        kinds = Counter(kind(k) for k in s.elements())
        print(f"{name}: {sum(s.values())} kinds={dict(kinds)}")
        for k in sorted(s.elements()):
            if k[0] in ("edge", "trk", "via"):
                print("   ", k)
            elif k[0] == "zonefill":
                pts = [p for poly in k[3] for p in poly]
                xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
                print(f"    zonefill {k[1]} layer={k[2]} bbox=({min(xs):.1f},{min(ys):.1f})-({max(xs):.1f},{max(ys):.1f}) polys={len(k[3])}")
    print("GND removed:", sum((ga - gb).values()), " GND added:", sum((gb - ga).values()))
    for k in sorted((gb - ga).elements()):
        if k[0] in ("trk", "via"):
            print("   +GND", k)
        elif k[0] == "zonefill":
            pts = [p for poly in k[3] for p in poly]
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            print(f"   +GND zonefill layer={k[2]} bbox=({min(xs):.1f},{min(ys):.1f})-({max(xs):.1f},{max(ys):.1f}) polys={len(k[3])}")
    for k in sorted((ga - gb).elements()):
        if k[0] == "zonefill":
            pts = [p for poly in k[3] for p in poly]
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            print(f"   -GND zonefill layer={k[2]} bbox=({min(xs):.1f},{min(ys):.1f})-({max(xs):.1f},{max(ys):.1f}) polys={len(k[3])}")
        else:
            print("   -GND", k)

if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    v = sys.argv[1]
    summ(f"scratch/prerespin/{v}.kicad_pcb",
         f"../hardware/kicad/qualification/issue-299-wwing/{v}/wwing-{v.lower()}.kicad_pcb", v)
