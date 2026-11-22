"""Blender Cycles renders of the Issue #296 case, hinge round
(A)+(B) (run inside Blender). Views: (1) top (orthographic,
north-up, caps on), assembled; (2) perspective assembled;
(3) NEW: the battery-swap state — shelf OPEN at the verified
95 deg stop about the hinge axis (Y -0.57, Z 19.30), slider
riding with it, pins in the bosses, internals + caps fitted,
bay accessible. North edge is the near edge in perspective
views, as in the previous render sets.
"""
import bpy, math, os
import mathutils

CASE = os.path.expanduser("~/workspace/projects/he-piantor-case296b/hardware/case/issue-296-wireless")
ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
OUT = os.path.expanduser("~/workspace/goals/he-piantor-42-keyboard-pmo/files")
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
bg.inputs[0].default_value = (0.80, 0.82, 0.86, 1)
bg.inputs[1].default_value = 0.45


def mat(name, color, rough=0.55, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    return m


M_CASE = mat("petg", (0.16, 0.17, 0.19), 0.5)
M_COVER = mat("petg-cover", (0.24, 0.26, 0.30), 0.5)
M_PLATE = mat("plate", (0.55, 0.57, 0.60), 0.35, 0.85)
M_PCB = mat("pcb", (0.05, 0.28, 0.12), 0.6)
M_CELL = mat("cell", (0.75, 0.72, 0.62), 0.4, 0.3)
M_PWR = mat("pwr", (0.10, 0.12, 0.35), 0.6)
M_CAP = mat("keycap", (0.82, 0.83, 0.85), 0.45)
M_PIN = mat("pin", (0.70, 0.68, 0.60), 0.3, 0.9)


def load(path, material, name):
    bpy.ops.wm.stl_import(filepath=path)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(material)
    ob.scale = (0.001, 0.001, 0.001)
    return ob


parts = {}
for n, m in [("tray-left", M_CASE), ("tray-right", M_CASE),
             ("centre-infill", M_CASE), ("shell-central", M_CASE),
             ("north-shelf", M_COVER),
             ("plate-left", M_PLATE), ("plate-right", M_PLATE),
             ("plunger-sw1", M_COVER), ("light-pipe-dled", M_COVER),
             ("latch-slider", M_COVER)]:
    parts[n] = load(f"{CASE}/{n}.stl", m, n)
internals = {}
for n, m in [("render-main", M_PCB), ("render-wings", M_PCB),
             ("render-cells", M_CELL), ("render-powerboard", M_PWR)]:
    internals[n] = load(f"{ASM}/{n}.stl", m, n)
caps_ob = load(f"{ASM}/render-caps.stl", M_CAP, "keycaps")

# hinge pins (hardware, not printed parts): two O2 pins on the
# axis, drawn at their seats (they stay with the fixed side)
pins = []
for x0 in (0.0005, -0.0108):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.001, depth=0.0103,
        location=(x0 + 0.00515, -0.00057, 0.0193),
        rotation=(0, math.radians(90), 0))
    p = bpy.context.active_object
    p.data.materials.append(M_PIN)
    pins.append(p)

bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, -0.0027))
gnd = bpy.context.active_object
gnd.data.materials.append(mat("ground", (0.85, 0.86, 0.88), 0.9))


def area(name, loc, energy, size=1.2):
    d = bpy.data.lights.new(name, "AREA")
    d.energy = energy
    d.shape = "DISK"
    d.size = size
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (0, 0, 0)
    return o


key = area("key", (0.35, -0.25, 0.55), 55)
key.rotation_euler = (math.radians(35), 0, math.radians(35))
fill = area("fill", (-0.45, 0.30, 0.35), 18)
fill.rotation_euler = (math.radians(60), 0, math.radians(-120))

cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
bpy.context.collection.objects.link(cam)
sc.camera = cam


def look(cam, loc, target, lens=None, ortho=None):
    cam.rotation_mode = "XYZ"
    cam.location = loc
    d = [target[i] - loc[i] for i in range(3)]
    direction = mathutils.Vector(d)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    if ortho:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = ortho
    else:
        cam_data.type = "PERSP"
        cam_data.lens = lens or 50


def show(objs, on=True):
    for o in objs:
        o.hide_render = not on


shelf = parts["north-shelf"]
slider = parts["latch-slider"]


def roll180():
    cam.rotation_mode = "QUATERNION"
    q = cam.rotation_quaternion
    cam.rotation_quaternion = q @ mathutils.Quaternion((0, 0, 1), math.pi)


def open_shelf(deg=95.0):
    """Rotate shelf + slider about the hinge axis (metres)."""
    ax = mathutils.Matrix.Translation((0, -0.00057, 0.0193))
    rx = mathutils.Matrix.Rotation(math.radians(-deg), 4, "X")
    m = ax @ rx @ ax.inverted()
    for o in (shelf, slider):
        o.matrix_world = m @ o.matrix_world


# view 1: top, assembled, north-up
show(internals.values(), False)
show(pins, False)
show(parts.values(), True)
caps_ob.hide_render = False
look(cam, (0, 0.01, 0.62), (0, 0.01, 0), ortho=0.36)
roll180()
sc.render.filepath = f"{OUT}/case296-3d-top.png"
bpy.ops.render.render(write_still=True)

# view 2: perspective assembled
look(cam, (-0.30, -0.34, 0.24), (0, 0.0, 0.004), lens=42)
sc.render.filepath = f"{OUT}/case296-3d-persp.png"
bpy.ops.render.render(write_still=True)

# view 3: battery-swap state — shelf open at the 95 deg stop
open_shelf(95.0)
show(internals.values(), True)
show(pins, True)
look(cam, (0.30, -0.34, 0.26), (0, -0.01, 0.02), lens=42)
sc.render.filepath = f"{OUT}/case296-hinge-open.png"
bpy.ops.render.render(write_still=True)
print("renders done")
