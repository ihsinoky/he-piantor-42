"""Blender Cycles renders for the Issue #296 keycap design.
Run: blender -b --factory-startup -P render_keycaps.py
Views: (1) single cap close-up on a simplified Jade Pro; (2) cap
underside (socket / cavity / boss); (3) row of six at 17 mm pitch;
(4) all 42 caps in the case, top view.
Style follows the case team's render.py (0.001 scale, Filmic)."""
import bpy, math, os

RT = os.path.expanduser("~/workspace/projects/he-piantor-keycaps/"
                        ".issue296-keycaps-runtime/render")
CASE = os.path.expanduser("~/workspace/projects/he-piantor-keycaps/"
                          "hardware/case/issue-296-wireless")
OUT = os.path.expanduser("~/workspace/goals/he-piantor-42-keyboard-pmo/"
                         "files")
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = 48
sc.cycles.device = "CPU"
sc.cycles.use_denoising = True
sc.render.resolution_x = 1400
sc.render.resolution_y = 1050
sc.view_settings.view_transform = "Filmic"
sc.view_settings.look = "Medium High Contrast"
sc.view_settings.exposure = -0.6

world = bpy.data.worlds.new("World")
sc.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.95, 0.95, 0.96, 1)
bg.inputs[1].default_value = 1.0


def mat(name, color, rough=0.55, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    return m


M_CAP = mat("cap", (0.76, 0.74, 0.70), 0.5)
M_SW = mat("switch", (0.10, 0.11, 0.13), 0.5)
M_PLATE = mat("plate", (0.42, 0.44, 0.47), 0.4, 0.8)
M_CASE = mat("petg", (0.16, 0.17, 0.19), 0.5)
M_SHELF = mat("petg-shelf", (0.24, 0.26, 0.30), 0.5)


def load(path, material, name):
    bpy.ops.wm.stl_import(filepath=path)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (0.001, 0.001, 0.001)
    if material:
        ob.data.materials.append(material)
    return ob


def area(name, loc, energy):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = energy
    ld.shape = "DISK"
    ld.size = 0.25
    o = bpy.data.objects.new(name, ld)
    bpy.context.collection.objects.link(o)
    o.location = loc
    import mathutils
    o.rotation_euler = mathutils.Vector((0, 0, 0)).to_track_quat(
        "-Z", "Y").to_euler()
    return o


key = area("key", (0.35, -0.25, 0.55), 55)
key.rotation_euler = (math.radians(35), 0, math.radians(35))
fill = area("fill", (-0.45, 0.30, 0.35), 18)
fill.rotation_euler = (math.radians(60), 0, math.radians(-120))

cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
bpy.context.collection.objects.link(cam)
sc.camera = cam


def look(loc, target, lens=None, ortho=None):
    cam.location = loc
    import mathutils
    d = mathutils.Vector([target[i] - loc[i] for i in range(3)])
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    if ortho:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = ortho
    else:
        cam_data.type = "PERSP"
        cam_data.lens = lens or 50
    cam_data.clip_start = 0.001
    cam_data.clip_end = 10.0


def show(objs, on=True):
    for o in objs:
        o.hide_render = not on


def render(fname):
    sc.render.filepath = os.path.join(OUT, fname)
    bpy.ops.render.render(write_still=True)
    print("rendered", fname)


# --- scene 1+2: single cap -------------------------------------------
cap1 = load(f"{RT}/cap-single.stl", M_CAP, "cap")
sw1 = load(f"{RT}/switch-single.stl", M_SW, "switch")
pl1 = load(f"{RT}/plate-single.stl", M_PLATE, "plate")
cap2 = load(f"{RT}/cap-single.stl", M_CAP, "cap-flipped")
cap2.rotation_euler = (math.pi, 0, 0)
cap2.location = (0, 0, 0.0165)
show([cap2], False)

look((0.030, -0.034, 0.026), (0, 0, 0.006), lens=50)
render("keycap-closeup.png")

show([cap1, sw1, pl1], False)
show([cap2], True)
look((0.026, -0.030, 0.024), (0, 0, 0.008), lens=50)
render("keycap-underside.png")

# --- scene 3: row -----------------------------------------------------
for o in (cap1, cap2, sw1, pl1):
    bpy.data.objects.remove(o, do_unlink=True)
rc = load(f"{RT}/row-caps.stl", M_CAP, "row-caps")
rs = load(f"{RT}/row-switches.stl", M_SW, "row-switches")
rp = load(f"{RT}/row-plate.stl", M_PLATE, "row-plate")
look((0.055, -0.075, 0.045), (0, 0, 0.005), lens=50)
render("keycap-row.png")

# --- scene 4: in-case top --------------------------------------------
for o in (rc, rs, rp):
    bpy.data.objects.remove(o, do_unlink=True)
parts = []
for f, m in (("tray-left.stl", M_CASE), ("tray-right.stl", M_CASE),
             ("plate-left.stl", M_PLATE), ("plate-right.stl", M_PLATE),
             ("shell-central.stl", M_CASE), ("north-shelf.stl", M_SHELF)):
    parts.append(load(os.path.join(CASE, f), m, f))
M_COVER = mat("padcover", (0.85, 0.78, 0.62), 0.5)
M_PAD = mat("pad", (0.25, 0.27, 0.30), 0.25)
parts.append(load(os.path.join(CASE, "trackpad-cover.stl"), M_COVER,
                  "padcover"))
bpy.ops.mesh.primitive_cylinder_add(radius=0.020, depth=0.0012,
                                    location=(0, 0.0457, 0.0121))
pad = bpy.context.active_object
pad.data.materials.append(M_PAD)
parts.append(pad)
parts.append(load(f"{RT}/incase-caps-left.stl", M_CAP, "caps-left"))
parts.append(load(f"{RT}/incase-caps-right.stl", M_CAP, "caps-right"))
look((0, 0.001, 0.62), (0, 0.001, 0), ortho=0.36)
import mathutils as _mu
_q = cam.rotation_euler.to_quaternion()
_q = _q @ _mu.Quaternion((0, 0, 1), math.pi)  # north-up (case-team view)
cam.rotation_euler = _q.to_euler()
render("keycap-incase-top.png")
print("ALL RENDERS DONE")
