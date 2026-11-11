"""Renders the body with an item FBX on, arms lowered as in the idle, for checking fit by eye.

  blender evrar_full_parts.blend --background --python render_fit.py -- <out_dir> <fbx>...
Writes <out_dir>/fit_<n>.png per FBX (upper body, front). The body is tan, the item lilac.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index("--") + 1:]
out_dir, fbxs = args[0], args[1:]
os.makedirs(out_dir, exist_ok=True)


def lower(arm, pb, angle):
    bpy.context.view_layer.update()
    rot = arm.matrix_world.to_3x3().normalized()
    # Towards the next joint: prepared armatures point every bone along +Y.
    child = pb.children[0].head if pb.children else pb.tail
    direction = (rot @ (child - pb.head)).normalized()
    axis = direction.cross(Vector((0, 0, -1)))
    if axis.length < 1e-4:
        return
    turn = Matrix.Rotation(math.radians(angle), 3, axis.normalized())
    current = (rot @ pb.matrix.to_3x3()).normalized()
    pb.rotation_mode = "QUATERNION"
    pb.rotation_quaternion = pb.rotation_quaternion @ (current.inverted() @ turn @ current).to_quaternion()


def pose(arm):
    for side in ("L", "R"):
        for bone, angle in ((f"J_Bip_{side}_UpperArm", 70), (f"J_Bip_{side}_LowerArm", 10)):
            pb = arm.pose.bones.get(bone)
            if pb:
                lower(arm, pb, angle)
    bpy.context.view_layer.update()


def flat(name, colour):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = colour
    return mat


scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_cavity = True
scene.render.resolution_x = 520
scene.render.resolution_y = 640
skin = flat("Skin", (0.85, 0.62, 0.48, 1))
cloth = flat("Cloth", (0.78, 0.66, 0.95, 1))

reference = next(o for o in scene.objects if o.type == "ARMATURE")
body = bpy.data.objects["BodyOnly"]
for o in list(scene.objects):
    if o.type == "MESH" and o is not body:
        o.hide_render = True
body.data.materials.clear()
body.data.materials.append(skin)
pose(reference)

deps = bpy.context.evaluated_depsgraph_get()
ev = body.evaluated_get(deps)
pts = [body.matrix_world @ v.co for v in ev.to_mesh().vertices]
ev.to_mesh_clear()
top = max(p.z for p in pts)
lo_z, hi_z = top * 0.45, top * 0.86
xs = [p.x for p in pts if lo_z < p.z < hi_z]
centre = Vector(((min(xs) + max(xs)) / 2, 0, (lo_z + hi_z) / 2))

cam_data = bpy.data.cameras.new("Cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = (hi_z - lo_z) * 1.0
cam_data.clip_end = top * 20
cam = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = centre + Vector((0, -top * 5, 0))
cam.rotation_euler = (math.radians(90), 0, 0)

under = flat("Under", (0.95, 0.95, 0.97, 1))
for n, column in enumerate(fbxs):
    # "a.fbx+b.fbx": several items on at once; the last one is drawn lilac, the others white.
    paths = column.split("+")
    new = set()
    for k, path in enumerate(paths):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=path)
        added = set(bpy.data.objects) - before
        new |= added
        arm = next(o for o in added if o.type == "ARMATURE")
        mesh = next(o for o in added if o.type == "MESH")
        mesh.data.materials.clear()
        mesh.data.materials.append(cloth if k == len(paths) - 1 else under)
        pose(arm)
    scene.render.filepath = os.path.join(out_dir, f"fit_{n}.png")
    bpy.ops.render.render(write_still=True)
    for o in new:
        bpy.data.objects.remove(o)
