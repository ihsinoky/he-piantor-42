"""Issue #296 2D gate - kernel checks (build123d). All inputs cited in case-2d.md."""
import build123d as bd
import math

def box_at(l, w, h, x, y, z):
    return bd.Solid.make_box(l, w, h).moved(bd.Location((x, y, z)))

def cell_x(x0, z_base):
    """AA cell, axis along X, bottom resting at z_base. Returns solid."""
    c = bd.Solid.make_cylinder(14.5 / 2, 50.5)          # axis +Z, base at origin
    c = c.moved(bd.Location((0, 0, 0), (0, 90, 0)))     # axis -> +X, centre at Z=0
    return c.moved(bd.Location((x0, 0, z_base + 14.5 / 2)))

def vol(shape):
    return 0.0 if shape is None else shape.volume

print("== C1 tray channel width vs cell max diameter ==")
# D-060 field Y = 14.5; BK-3MCD max diameter 14.5 (D-048 / aa-sizing record)
for inner in (14.5, 15.6):
    cell = cell_x(-25.25, 0)
    wall_n = box_at(60, 2.0, 20, -30, inner / 2, -10)
    wall_s = box_at(60, 2.0, 20, -30, -inner / 2 - 2.0, -10)
    inter = vol(cell.intersect(wall_n)) + vol(cell.intersect(wall_s))
    print(f"inner={inner}: interference={inter:.4f} mm3, clearance/side={(inner - 14.5) / 2:.2f} mm")

print("== C2 length chain ==")
print("4x50.5 =", 4 * 50.5, "+ interfaces 6.0 + walls 4.0 =", 4 * 50.5 + 6.0 + 4.0,
      "(D-060 bay X = 212)")
print("spring travel/interface 0.75 nominal; cell length tol +-0.5 class -> worst-stack margin 0.25 (flag)")

print("== C3 height stack (solids) ==")
floor_top = 1.60  # tray floor datum, #263 production README
board = box_at(212, 15.6, 0.8, -106, -7.8, floor_top)
cells = [cell_x(x0, floor_top + 0.8) for x0 in (-100.75, -50.25, 0.25, 50.75)]
top = max(c.bounding_box().max.Z for c in cells)
print(f"floor_top={floor_top} board_top={floor_top + 0.8:.1f} cell_top={top:.2f} "
      f"datum=22.00 recess_below_datum={22.00 - top:.2f}")
print("stack check 0.8+14.5 =", 0.8 + 14.5, "(D-059/060 pack stack 15.3)")

print("== C4 cable route (figure frame: Y from north edge of NEW outline) ==")
# new-outline frame: Main south edge Y = 132.3 (old frame) + 17 (growth) = 149.3;
# JBATT X ~ +20 (board-frame x=124 of ~155-wide board, board centred - approx, Pilot B to confirm)
pts = [(100, 10), (60, 80), (22, 146), (20, 149.3)]
L = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
print(f"diagonal route polyline={L:.0f} mm; + slack ~10 -> ~{L + 10:.0f} mm")
print("NOTE: D-060 '~150 mm' was estimated for the centred +54 block tray; the row tray's")
print("end exit routes ~10-15% longer. Cable is cut to length - record corrected figure.")

print("== C5 antenna band (south-notch study record) ==")
print("Main south edge -> straightened case edge:", 81.702 - 67.900,
      "mm; less 2.0 wall -> clear PETG zone ~11.8 mm deep")

print("== C6 tray span ==")
print("bay 212 of outline 291 -> band remaining each side:", (291 - 212) / 2, "mm")
