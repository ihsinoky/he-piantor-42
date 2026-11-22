"""Blender Cycles renders of the Issue #296 case, trackpad LAP
round (run inside Blender). Views: (1) tight centre close-up of
the pad + shiplap cover, perspective from the south-east;
(2) SECTION through the pad centre (Y=48 plane, south half
kept, viewed from the south) showing the lap joint: flange
seated in the shell rabbet on both sides; (3) top
(orthographic, north-up, caps on), assembled.
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
M_BEZEL = mat("petg-bezel", (0.45, 0.30, 0.16), 0.5)
M_PLATE = mat("plate", (0.55, 0.57, 0.60), 0.35, 0.85)
M_CAP = mat("keycap", (0.82, 0.83, 0.85), 0.45)
M_PAD = mat("trackpad", (0.05, 0.05, 0.06), 0.25)
M_SEC = mat("petg-section", (0.62, 0.36, 0.14), 0.5)


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
             ("latch-slider", M_COVER),
             ("trackpad-cover", M_BEZEL)]:
    parts[n] = load(f"{CASE}/{n}.stl", m, n)
caps_ob = load(f"{ASM}/render-caps.stl", M_CAP, "keycaps")

bpy.ops.mesh.primitive_cylinder_add(
    radius=0.020, depth=0.0015, location=(0, 0.048, 0.01195))
pad = bpy.context.active_object
pad.name = "trackpad-module"
pad.data.materials.append(M_PAD)

sec = {}
for n, m in [("shell-central", M_CASE), ("trackpad-cover", M_BEZEL),
             ("plunger-sw1", M_SEC), ("centre-infill", M_CASE),
             ("module", M_PAD)]:
    sec[n] = load(f"{ASM}/section-{n}.stl", m, f"section-{n}")
    sec[n].hide_render = True

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


def roll180():
    cam.rotation_mode = "QUATERNION"
    q = cam.rotation_quaternion
    cam.rotation_quaternion = q @ mathutils.Quaternion((0, 0, 1), math.pi)


# view 1: tight close-up of pad + cover, from the south-east
look(cam, (0.105, 0.155, 0.085), (0, 0.047, 0.011), lens=50)
sc.render.filepath = f"{OUT}/case296-padcover-closeup.png"
bpy.ops.render.render(write_still=True)

# view 2: section through the pad centre, from the south
for ob in list(parts.values()) + [caps_ob, pad]:
    ob.hide_render = True
for ob in sec.values():
    ob.hide_render = False
gnd.hide_render = True
look(cam, (0, 0.30, 0.028), (0, 0.048, 0.0105), ortho=0.088)
sc.render.filepath = f"{OUT}/case296-padsection.png"
bpy.ops.render.render(write_still=True)

# view 3: top, assembled, north-up (standing top view, refreshed)
for ob in list(parts.values()) + [caps_ob, pad]:
    ob.hide_render = False
for ob in sec.values():
    ob.hide_render = True
gnd.hide_render = False
look(cam, (0, 0.01, 0.62), (0, 0.01, 0), ortho=0.36)
roll180()
sc.render.filepath = f"{OUT}/case296-3d-top.png"
bpy.ops.render.render(write_still=True)
print("renders done")
