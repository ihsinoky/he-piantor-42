"""Blender Cycles renders of the Issue #296 wireless case (run inside Blender).
Views: (1) top, assembled with cover; (2) perspective, cover off with
cells + power board + wings shown; (3) perspective assembled.
"""
import bpy, math, os, sys

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

def load(path, material, name):
    bpy.ops.wm.stl_import(filepath=path)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(material)
    # STL is in mm; scale to metres for sane lighting
    ob.scale = (0.001, 0.001, 0.001)
    return ob

parts = {}
for n, m in [("tray-left", M_CASE), ("tray-right", M_CASE),
             ("centre-infill", M_CASE), ("shell-central", M_CASE),
             ("strip-left", M_CASE), ("strip-right", M_CASE),
             ("plate-left", M_PLATE), ("plate-right", M_PLATE),
             ("battery-cover", M_COVER), ("plunger-sw1", M_COVER),
             ("light-pipe-dled", M_COVER)]:
    parts[n] = load(f"{CASE}/{n}.stl", m, n)
internals = {}
for n, m in [("render-main", M_PCB), ("render-wings", M_PCB),
             ("render-cells", M_CELL), ("render-powerboard", M_PWR)]:
    internals[n] = load(f"{ASM}/{n}.stl", m, n)

# ground plane
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, -0.0027))
gnd = bpy.context.active_object
gnd.data.materials.append(mat("ground", (0.85, 0.86, 0.88), 0.9))

# lights: key area + fill
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

def look(cam, loc, target, lens=None, ortho=None, spin=0):
    cam.location = loc
    d = [target[i] - loc[i] for i in range(3)]
    import mathutils
    direction = mathutils.Vector(d)
    q = direction.to_track_quat("-Z", "Y")
    if spin:
        import mathutils as _mu
        q = q @ _mu.Quaternion((0, 0, 1), spin)
    cam.rotation_euler = q.to_euler()
    if ortho:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = ortho
    else:
        cam_data.type = "PERSP"
        cam_data.lens = lens or 50

def show(objs, on=True):
    for o in objs:
        o.hide_render = not on

# view 1: top, assembled (cover on, internals off except plates visible)
show(internals.values(), False)
show(parts.values(), True)
look(cam, (0, 0.01, 0.62), (0, 0.01, 0), ortho=0.36, spin=math.pi)
sc.render.filepath = f"{OUT}/case296-3d-top.png"
bpy.ops.render.render(write_still=True)

print("renders done")
