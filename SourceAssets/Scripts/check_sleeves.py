"""Measures how far each built item's sleeves drift from the arms when the arms come down.

For every item FBX, vertices whose nearest body point lies on an arm are skinned twice under a
test pose (upper arms lowered, elbows bent): once with the item's own weights, once with the
body's weights at that nearest point. The gap between the two, in cm, is the drift the player sees.

  blender evrar_full_parts.blend --background --python check_sleeves.py -- <fbx_dir> <out.json> [names...]
"""
import glob
import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

args = sys.argv[sys.argv.index("--") + 1:]
fbx_dir, out_path, names = args[0], args[1], args[2:]
ARM_BONES = ("UpperArm", "LowerArm", "Hand", "Thumb", "Index", "Middle", "Ring", "Little")

body = bpy.data.objects["BodyOnly"]
body_to_world = body.matrix_world.copy()
bm = bmesh.new()
bm.from_mesh(body.data)
bm.transform(body_to_world)
bmesh.ops.triangulate(bm, faces=bm.faces)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()
tree = BVHTree.FromBMesh(bm)
tris = [[v.index for v in f.verts] for f in bm.faces]
pos = [v.co.copy() for v in bm.verts]
body_top = max(p.z for p in pos)
# Body length unit: 1 for metres, 100 for centimetres.
unit = 1.0 if body_top < 10 else 100.0
bm.free()
groups = {g.index: g.name for g in body.vertex_groups}
body_w = [{groups[g.group]: g.weight for g in v.groups if g.weight > 0} for v in body.data.vertices]


def lower(arm, pb, angle):
    """Turns a pose bone in world space so its tail goes down by angle degrees."""
    bpy.context.view_layer.update()
    rot = arm.matrix_world.to_3x3().normalized()
    direction = (rot @ (pb.tail - pb.head)).normalized()
    axis = direction.cross(Vector((0, 0, -1)))
    if axis.length < 1e-4:
        return
    turn = Matrix.Rotation(math.radians(angle), 3, axis.normalized())
    current = (rot @ pb.matrix.to_3x3()).normalized()
    pb.rotation_quaternion = pb.rotation_quaternion @ (current.inverted() @ turn @ current).to_quaternion()


def pose_matrices(arm):
    """World skinning matrix per bone for the test pose: upper arms 55 degrees down, elbows 30 more."""
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1, 0, 0, 0)
    for side in ("L", "R"):
        for bone, angle in ((f"J_Bip_{side}_UpperArm", 55), (f"J_Bip_{side}_LowerArm", 30)):
            pb = arm.pose.bones.get(bone)
            if pb is not None:
                lower(arm, pb, angle)
    bpy.context.view_layer.update()
    mw = arm.matrix_world
    return {pb.name: mw @ pb.matrix @ pb.bone.matrix_local.inverted() @ mw.inverted() for pb in arm.pose.bones}


def skin(co, weights, mats):
    total = sum(weights.values()) or 1.0
    out = Vector((0, 0, 0))
    for bone, w in weights.items():
        m = mats.get(bone)
        out += (m @ co if m else co) * (w / total)
    return out


results = {}
paths = sorted(glob.glob(os.path.join(fbx_dir, "SK_*.fbx")))
if names:
    paths = [p for p in paths if os.path.basename(p)[3:-4] in names]
for path in paths:
    item = os.path.basename(path)[3:-4]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    new = set(bpy.data.objects) - before
    arm = next((o for o in new if o.type == "ARMATURE"), None)
    mesh = next((o for o in new if o.type == "MESH"), None)
    if arm and mesh:
        mats = pose_matrices(arm)
        world = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
        # FBX may come back in metres while the body is in centimetres.
        to_body = body_top / max(c.z for c in world)
        to_body = 10 ** round(math.log10(to_body))
        cg = {g.index: g.name for g in mesh.vertex_groups}
        gaps, counts, rest, inside = [], {}, [], 0
        for v, co in zip(mesh.data.vertices, world):
            hit, normal, fi, dist = tree.find_nearest(co * to_body)
            if hit is None:
                continue
            a, b, c = tris[fi]
            bary = barycentric_transform(hit, pos[a], pos[b], pos[c],
                                         Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))
            expect = {}
            for corner, share in zip((a, b, c), bary):
                for bone, w in body_w[corner].items():
                    expect[bone] = expect.get(bone, 0.0) + max(share, 0.0) * w
            if sum(w for bone, w in expect.items() if any(k in bone for k in ARM_BONES)) < 0.6:
                continue
            rest.append(dist)
            # Sunk into the arm: on the skin's inner side by more than 3 mm.
            inside += (co * to_body - hit).dot(normal) < -0.003 * unit
            own = {cg[g.group]: g.weight for g in v.groups if g.weight > 0}
            for bone, w in own.items():
                counts[bone] = counts.get(bone, 0.0) + w
            gaps.append((skin(co, own, mats) - skin(co, expect, mats)).length * to_body)
        if gaps:
            gaps.sort()
            top = sorted(counts.items(), key=lambda kv: -kv[1])[:6]
            results[item] = {
                "arm_verts": len(gaps),
                "p50": round(gaps[len(gaps) // 2], 2),
                "p95": round(gaps[int(len(gaps) * 0.95)], 2),
                "max": round(gaps[-1], 2),
                "inside": round(inside / len(gaps), 3),
                "rest_p50": round(sorted(rest)[len(rest) // 2], 2),
                "rest_p95": round(sorted(rest)[int(len(rest) * 0.95)], 2),
                "bones": {k: round(v / len(gaps), 3) for k, v in top},
            }
            print("SLEEVE", item, results[item])
    for o in new:
        bpy.data.objects.remove(o)
    for block in list(bpy.data.meshes):
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in list(bpy.data.armatures):
        if block.users == 0:
            bpy.data.armatures.remove(block)

json.dump(results, open(out_path, "w"), indent=1)
