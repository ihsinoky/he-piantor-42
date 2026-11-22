"""Blender Cycles render: dish section view (round 2).

Three dish variants (0.35 / 0.50 / 0.60, left -> right) half-sectioned
at y=0, seen from the front — the XZ profile shows the pocket, the
rim land at TOP_Z and the cylinder curvature. Same style as
render_keycaps.py. Run: blender -b --factory-startup -P
render_section.py  (after prep_render.py)
"""
import bpy, math, os

RT = os.path.expanduser("~/workspace/projects/he-piantor-keycaps/"
                        ".issue296-keycaps-runtime/render")
OUT = os.path.expanduser("~/workspace/goals/he-piantor-42-keyboard-pmo/"
                         "files")
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = 48
sc.cycles.device = "CPU"
sc.cycles.use_denoising = True
sc.render.resolution_x = 1600
sc.render.resolution_y = 700
sc.view_settings.view_transform = "Filmic"
sc.view_settings.look = "Medium High Contrast"
sc.view_settings.exposure = -0.6

world = bpy.data.worlds.new("World")
sc.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.95, 0.95, 0.96, 1)
bg.inputs[1].default_value = 1.0


def mat(name, color, rough=0.55):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    return m


M_CAP = mat("cap", (0.76, 0.74, 0.70), 0.5)


def load(path, material, name):
    bpy.ops.wm.stl_import(filepath=path)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (0.001, 0.001, 0.001)
    if material:
        ob.data.materials.append(material)
    return ob


def area(name, loc, energy, rot):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = energy
    ld.shape = "DISK"
    ld.size = 0.25
    o = bpy.data.objects.new(name, ld)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rot
    return o


area("key", (0.30, -0.30, 0.50), 55, (math.radians(35), 0, math.radians(35)))
area("fill", (-0.45, -0.20, 0.35), 18, (math.radians(60), 0, math.radians(-120)))

cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
bpy.context.collection.objects.link(cam)
sc.camera = cam

load(f"{RT}/cap-sections.stl", M_CAP, "sections")

# front view, slightly above: look at the middle cap's top region
cam.location = (0, -0.085, 0.030)
import mathutils
target = mathutils.Vector((0, 0, 0.0075))
d = target - mathutils.Vector(cam.location)
cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
cam_data.type = "PERSP"
cam_data.lens = 50
cam_data.clip_start = 0.001
cam_data.clip_end = 10.0

sc.render.filepath = os.path.join(OUT, "keycap-dish-section.png")
bpy.ops.render.render(write_still=True)
print("rendered keycap-dish-section.png")
