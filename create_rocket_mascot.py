"""Procedurally build an original stylized Rocket desktop-companion mascot.

Run in Blender's Text Editor or from the command line:
    blender --background --python create_rocket_mascot.py
The scene is saved next to this script as Rocket_v1.blend.
"""
import bpy
import math
import os
from mathutils import Vector


# ---------- scene and materials ----------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.materials, bpy.data.curves, bpy.data.meshes,
                   bpy.data.cameras, bpy.data.lights):
    # Keep this safe for repeated execution without trying to forcibly remove linked data.
    pass

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x, scene.render.resolution_y = 720, 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Rocket_preview.png')
scene.world.color = (0.045, 0.055, 0.075)

collection = bpy.data.collections.get('ROCKET_CHARACTER') or bpy.data.collections.new('ROCKET_CHARACTER')
if collection not in scene.collection.children:
    scene.collection.children.link(collection)

def material(name, color, metallic=0.0, roughness=0.45, emission=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    if emission:
        p.inputs['Emission Color'].default_value = (*emission[0], 1)
        p.inputs['Emission Strength'].default_value = emission[1]
    return m

suit   = material('Rocket_Suit',      (0.82, 0.87, 0.91), 0.05, 0.34)
orange = material('Rocket_Orange',    (0.95, 0.20, 0.055), 0.12, 0.30)
dark   = material('Rocket_DarkMetal', (0.035, 0.055, 0.085), 0.78, 0.25)
bronze = material('Rocket_Bronze',    (0.42, 0.19, 0.055), 0.65, 0.27)
visor  = material('Rocket_Visor',     (0.055, 0.23, 0.34), 0.48, 0.16)
eye    = material('Rocket_Eye',       (0.008, 0.012, 0.022), 0.10, 0.18)
mouth  = material('Rocket_Mouth',     (0.22, 0.018, 0.025), 0.0, 0.35)
core   = material('Rocket_AICore',    (0.02, 0.50, 1.0), 0.15, 0.20, ((0.02, 0.42, 1.0), 5.0))
white  = material('Rocket_EyeHighlight', (0.9, 0.97, 1.0), 0.0, 0.15)
ground = material('Studio_Ground', (0.10, 0.12, 0.15), 0.0, 0.65)

def link_to_character(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def smooth(obj):
    if obj.type == 'MESH':
        for poly in obj.data.polygons: poly.use_smooth = True
    return obj

def uv(name, loc, scale, mat, segments=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=loc)
    o = bpy.context.object; o.name = name; o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat); return link_to_character(smooth(o))

def cyl(name, loc, radius, depth, mat, rotation=(0, 0, 0), bevel=0.08):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc, rotation=rotation)
    o = bpy.context.object; o.name = name; o.data.materials.append(mat)
    bev = o.modifiers.new('Soft_Edges', 'BEVEL'); bev.width = bevel; bev.segments = 3
    return link_to_character(smooth(o))

def cube(name, loc, scale, mat, bevel=0.12):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object; o.name = name; o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    b = o.modifiers.new('Rounded_Edges', 'BEVEL'); b.width = bevel; b.segments = 3
    return link_to_character(smooth(o))

def torus(name, loc, major, minor, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=36,
                                     minor_segments=10, location=loc, rotation=rotation)
    o = bpy.context.object; o.name = name; o.data.materials.append(mat)
    return link_to_character(smooth(o))

# ---------- torso, helmet, face ----------
uv('Torso_RoundedSuit', (0, 0, 4.20), (1.55, 1.12, 1.60), suit)
# Original asymmetric orange chest-chevron panels, not copied clothing decoration.
cube('Chest_OrangePanel_L', (-0.48, -1.04, 4.32), (0.45, 0.065, 0.25), orange, 0.08).rotation_euler[1] = -0.25
cube('Chest_OrangePanel_R', (0.48, -1.04, 4.32), (0.45, 0.065, 0.25), orange, 0.08).rotation_euler[1] = 0.25
torus('Chest_Core_Ring', (0, -1.16, 4.35), 0.30, 0.075, bronze, (math.pi/2, 0, 0))
uv('AI_Core_Emissive', (0, -1.25, 4.35), (0.20, 0.055, 0.20), core)

uv('Helmet_RoundedShell', (0, 0.02, 6.55), (1.72, 1.30, 1.60), suit)
# Visor plate and rim project forward (-Y), preserving a highly legible face.
uv('Helmet_Visor', (0, -1.15, 6.48), (1.22, 0.17, 0.93), visor)
torus('Visor_BronzeRim', (0, -1.30, 6.48), 1.05, 0.095, bronze, (math.pi/2, 0, 0))
for x in (-0.43, 0.43):
    uv('Eye_' + ('L' if x < 0 else 'R'), (x, -1.36, 6.58), (0.24, 0.055, 0.36), eye)
    uv('Eye_Shine_' + ('L' if x < 0 else 'R'), (x - 0.07, -1.415, 6.73), (0.065, 0.018, 0.09), white)
uv('Friendly_Mouth', (0, -1.37, 6.12), (0.28, 0.05, 0.12), mouth)
# Distinct three-fin beacon cap: a tiny rocket silhouette without matching any reference branding.
cyl('Cap_Base', (0, 0.02, 8.03), 0.55, 0.14, dark)
bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.48, radius2=0.06, depth=0.78, location=(0, 0.02, 8.47))
cap = bpy.context.object; cap.name = 'Rocket_BeaconCap'; cap.data.materials.append(orange); link_to_character(smooth(cap))
for angle in (0, 2.1, 4.2):
    x, y = 0.58 * math.cos(angle), 0.58 * math.sin(angle)
    uv('Cap_NavigationDot', (x, y + 0.02, 8.05), (0.07, 0.07, 0.07), core, 16, 8)

# ---------- arms: individual named pieces for future armature parenting ----------
for side, x in (('L', -1), ('R', 1)):
    sx = x * 1.64
    uv('ShoulderJoint_' + side, (sx, 0, 4.82), (0.38, 0.38, 0.38), dark)
    cyl('UpperArm_' + side, (x * 1.95, -0.02, 4.34), 0.24, 0.70, suit, (0.18, 0, x * 0.22))
    uv('ElbowJoint_' + side, (x * 2.0, -0.03, 3.92), (0.27, 0.27, 0.27), bronze)
    cyl('Forearm_' + side, (x * 2.08, -0.10, 3.52), 0.24, 0.56, suit, (-0.15, 0, x * 0.12))
    uv('Hand_' + side, (x * 2.13, -0.16, 3.18), (0.32, 0.27, 0.28), orange)

# ---------- legs: separated mechanisms, knee pivots, oversized stable boots ----------
for side, x in (('L', -1), ('R', 1)):
    lx = x * 0.70
    uv('HipJoint_' + side, (lx, 0, 3.08), (0.30, 0.30, 0.30), dark)
    cyl('Thigh_' + side, (lx, 0, 2.56), 0.26, 0.76, suit)
    uv('KneeJoint_' + side, (lx, -0.02, 2.10), (0.32, 0.30, 0.32), bronze)
    cyl('Shin_' + side, (lx, 0.03, 1.57), 0.25, 0.75, dark)
    cube('Boot_' + side, (lx, -0.25, 0.95), (0.53, 0.76, 0.30), orange, 0.18)
    cube('BootSole_' + side, (lx, -0.31, 0.70), (0.57, 0.80, 0.10), dark, 0.08)

# ---------- compact rear pack and twin thrusters ----------
cube('Backpack_Main', (0, 1.02, 4.65), (0.88, 0.38, 0.90), dark, 0.18)
for side, x in (('L', -0.53), ('R', 0.53)):
    cyl('Thruster_' + side, (x, 1.33, 4.65), 0.28, 0.90, bronze, (math.pi/2, 0, 0))
    cyl('Thruster_Nozzle_' + side, (x, 1.80, 4.65), 0.22, 0.18, dark, (math.pi/2, 0, 0))
    torus('Thruster_OrangeBand_' + side, (x, 1.65, 4.65), 0.28, 0.055, orange, (math.pi/2, 0, 0))

# ---------- studio ----------
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0.57))
floor = bpy.context.object; floor.name = 'Studio_Ground'; floor.data.materials.append(ground)

def light(name, loc, energy, size, color):
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object; o.name = name; o.data.energy = energy; o.data.shape = 'DISK'; o.data.size = size; o.data.color = color
    direction = Vector((0, 0, 4.2)) - o.location
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

light('Key_Softbox', (-4.5, -5.0, 9), 900, 5, (0.72, 0.86, 1.0))
light('Warm_Rim', (4.0, 2.5, 7), 700, 4, (1.0, 0.34, 0.12))
light('Front_Fill', (0, -5.5, 4.5), 350, 3, (0.80, 0.90, 1.0))

bpy.ops.object.camera_add(location=(10.5, -16.5, 9.0))
camera = bpy.context.object; camera.name = 'Camera_Rocket_ThreeQuarter'; scene.camera = camera
camera.data.lens = 56
camera.rotation_euler = (Vector((0, 0, 4.55)) - camera.location).to_track_quat('-Z', 'Y').to_euler()

# Color management for a soft animation-film look.
scene.view_settings.look = 'AgX - Medium High Contrast'

# Friendly root empty makes later rig/animation hierarchy setup straightforward.
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0.57))
root = bpy.context.object; root.name = 'ROCKET_ROOT_FutureRig'; link_to_character(root)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Rocket_v1.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
print('Saved original Rocket mascot to: ' + out)
