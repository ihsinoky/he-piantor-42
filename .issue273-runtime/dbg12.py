import sys, traceback
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
try:
    import fitlibF as FF
    b = FF.bodies_at(17, -2.65)
    print("bodies ok:", len(b))
except Exception:
    traceback.print_exc()
