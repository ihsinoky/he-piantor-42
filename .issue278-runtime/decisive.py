import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route_audit as RA

def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

log("building bodies in-process")
bodies, sheets = RA.build_bodies()
tl = bodies['tray-left']
bb = tl.bounding_box()
log(f"tray-left type={type(tl).__name__} vol={round(RA.vol(tl),1)} "
    f"bbox={[round(bb.min.X,2),round(bb.min.Y,2),round(bb.min.Z,2),round(bb.max.X,2),round(bb.max.Y,2),round(bb.max.Z,2)]}")
try:
    log(f"tray-left solids: {len(tl.solids())}")
except Exception as e:
    log(f"solids() failed: {e}")
plug = RA.box_at(0, 19.18, 3.45, 5.0, 3.5, 1.30)
log(f"plug vol={round(RA.vol(plug),3)}")
log(f"plug(dz-1.6) x tray-left = {round(RA.common_vol(plug.translate((0,0,-1.6)), tl),3)}")
plug2 = RA.box_at(0, 19.18, 1.85, 5.0, 3.5, 1.30)
log(f"plug-at-1.85 x tray-left = {round(RA.common_vol(plug2, tl),3)}")
log(f"plug(dz0) x tray-left = {round(RA.common_vol(plug, tl),3)}")
tr = bodies['tray-right']
log(f"tray-right vol={round(RA.vol(tr),1)} (cache said 85092.8)")
for n in ('shell-central', 'strip-left', 'splice-1', 'main'):
    s = bodies[n]; bb2 = s.bounding_box()
    log(f"{n}: vol={round(RA.vol(s),1)} zmax={round(bb2.max.Z,2)}")
log("DONE")
