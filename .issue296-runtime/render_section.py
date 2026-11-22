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


sec = {}
for n, m in [("shell-central", M_CASE), ("trackpad-cover", M_BEZEL),
             ("plunger-sw1", M_SEC), ("module", M_PAD)]:
    sec[n] = load(f"{ASM}/section-{n}.stl", m, f"section-{n}")


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



# section through the pad centre, from the south, tight on the lap
look(cam, (0, 0.17, 0.052), (0, 0.048, 0.0112), ortho=0.066)
sc.render.filepath = f"{OUT}/case296-padsection.png"
bpy.ops.render.render(write_still=True)
print("section render done")
