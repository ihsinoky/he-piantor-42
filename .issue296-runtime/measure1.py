import build123d as bd
p = "hardware/case/issue-261-lowdeck-full/preview.step"
top = bd.import_step(p)
solids = top.solids()
print("n solids:", len(solids))
for i, s in enumerate(solids):
    bb = s.bounding_box()
    print(f"{i}: vol={s.volume:9.1f} X[{bb.min.X:8.2f},{bb.max.X:8.2f}] Y[{bb.min.Y:8.2f},{bb.max.Y:8.2f}] Z[{bb.min.Z:6.2f},{bb.max.Z:6.2f}] label={getattr(s,'label','')}")
print("whole:", top.bounding_box().min, top.bounding_box().max)
