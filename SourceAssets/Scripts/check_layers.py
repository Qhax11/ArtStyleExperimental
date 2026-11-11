"""Which tops and dresses fit under each jacket: counts the under-item's vertices that end up outside
the jacket with the arms lowered as in the idle.

For every under-item vertex: from the nearest skin point, along the skin normal, find the jacket's
surface. If the under-item is further out than the jacket there, it pokes through. Places the jacket
does not cover (open front, below the hem, hands) are not counted.

  blender evrar_full_parts.blend --background --python check_layers.py -- <fbx_dir> <out.json> <jackets,...> <unders,...>
Writes {jacket: {under: {pokes, deep (>0.5 cm out), covered, share}}}.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

args = sys.argv[sys.argv.index("--") + 1:]
fbx_dir, out_path = args[0], args[1]
jackets, unders = args[2].split(","), args[3].split(",")
MARGIN = 0.15  # cm the under-item may come closer than the jacket before it counts as poking


def lower(arm, pb, angle):
    bpy.context.view_layer.update()
    rot = arm.matrix_world.to_3x3().normalized()
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


def posed_world(obj):
    deps = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(deps)
    me = ev.to_mesh()
    verts = [obj.matrix_world @ v.co for v in me.vertices]
    tris = [tuple(p.vertices) for p in me.polygons]
    ev.to_mesh_clear()
    return verts, tris


def load(name):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(fbx_dir, f"SK_{name}.fbx"))
    new = set(bpy.data.objects) - before
    arm = next(o for o in new if o.type == "ARMATURE")
    mesh = next(o for o in new if o.type == "MESH")
    pose(arm)
    verts, tris = posed_world(mesh)
    for o in new:
        bpy.data.objects.remove(o)
    return verts, tris


reference = next(o for o in bpy.context.scene.objects if o.type == "ARMATURE")
body = bpy.data.objects["BodyOnly"]
pose(reference)
body_verts, body_tris = posed_world(body)
body_tree = BVHTree.FromPolygons(body_verts, body_tris)
top = max(v.z for v in body_verts)
cm = 100.0 if top < 10 else 1.0  # world units per cm is 1/cm

jacket_trees = {}
for j in jackets:
    verts, tris = load(j)
    jacket_trees[j] = BVHTree.FromPolygons(verts, tris)

result = {j: {} for j in jackets}
for u in unders:
    if not os.path.exists(os.path.join(fbx_dir, f"SK_{u}.fbx")):
        continue
    verts, _ = load(u)
    samples = []
    for v in verts:
        hit, normal, _, dist = body_tree.find_nearest(v)
        if hit is None or dist * cm > 12:
            continue
        samples.append((hit, normal, (v - hit).dot(normal) * cm))
    for j, tree in jacket_trees.items():
        pokes = deep = covered = 0
        for hit, normal, height in samples:
            # The jacket's surface above this skin point (the nearest one outward).
            jhit = tree.ray_cast(hit + normal * (0.05 / cm), normal, 15 / cm)
            if jhit[0] is None:
                continue
            jacket_height = (jhit[0] - hit).dot(normal) * cm
            covered += 1
            if height > jacket_height - MARGIN:
                pokes += 1
                deep += height > jacket_height + 0.5
        result[j][u] = {"pokes": pokes, "deep": deep, "covered": covered,
                        "share": round(pokes / max(covered, 1), 3)}
    print("LAYER", u, {j: result[j][u] for j in jackets})

json.dump(result, open(out_path, "w"), indent=1)
