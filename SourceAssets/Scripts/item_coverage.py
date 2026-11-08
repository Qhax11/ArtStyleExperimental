"""Find which body regions each built clothing item covers, for HiddenBodyRegions.

Body faces are sorted into regions exactly as split_body_regions.py does. From each body
face a ray goes outward along its normal; the face is covered when it meets the item
within MAX_GAP cm. A region is hidden when nearly all its faces are covered, so a hidden
region never leaves a visible hole, and skin cannot poke through a fully covered area.

Run headless:
  blender evrar_full_parts.blend --background --python item_coverage.py -- <fbx_dir> <out.json> [names...]
"""
import json
import os
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from vroid_fbx_common import prepare_armature  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
fbx_dir, out_path, names = args[0], args[1], args[2:]
MAX_GAP = 4.0      # cm
HIDE_AT = 0.96     # share of a region's faces that must be covered

RULES = [
    (("Bust", "UpperChest", "C_Chest"), "Chest"),
    (("C_Spine",), "Belly"),
    (("UpperArm", "Shoulder"), "UpperArm"),
    (("LowerArm",), "LowerArm"),
    (("Hand", "Thumb", "Index", "Middle", "Ring", "Little"), "Hand"),
    (("Neck", "Head", "Hair", "J_Adj"), "Neck"),
    (("UpperLeg",), "Thigh"),
    (("LowerLeg",), "Calf"),
    (("Foot", "ToeBase"), "Foot"),
    (("C_Hips", "Root"), "Hips"),
]
REGIONS = ["Chest", "Belly", "Hips", "UpperArm", "LowerArm", "Hand", "Neck", "Thigh", "Calf", "Foot", "Ankle"]
HIPS_TOP_RATIO = 0.95 / 1.59
FOOT_TOP = [(-12.0, 3.8), (-5.5, 5.6), (0.0, 8.2), (6.0, 8.8)]


def foot_top(y):
    if y <= FOOT_TOP[0][0]:
        return FOOT_TOP[0][1]
    for (y0, h0), (y1, h1) in zip(FOOT_TOP, FOOT_TOP[1:]):
        if y <= y1:
            return h0 + (h1 - h0) * (y - y0) / (y1 - y0)
    return FOOT_TOP[-1][1]


def region_of(bone_name):
    for fragments, region in RULES:
        if any(f in bone_name for f in fragments):
            return region
    return "Hips"


armature = prepare_armature()
body = bpy.data.objects["BodyOnly"]
me = body.data
group_region = {g.index: region_of(g.name) for g in body.vertex_groups}
heights = [(body.matrix_world @ v.co).z for v in me.vertices]
z_min, z_max = min(heights), max(heights)
hips_top = z_min + HIPS_TOP_RATIO * (z_max - z_min)
faces = []  # (region, centre, normal)
for poly in me.polygons:
    totals = dict.fromkeys(REGIONS, 0.0)
    for vi in poly.vertices:
        for g in me.vertices[vi].groups:
            totals[group_region[g.group]] += g.weight
    region = max(REGIONS, key=lambda r: totals[r])
    centre = body.matrix_world @ poly.center
    if region == "Hips" and sum(heights[i] for i in poly.vertices) / len(poly.vertices) > hips_top:
        region = "Belly"
    if region == "Foot" and centre.z > foot_top(centre.y):
        region = "Ankle"
    normal = (body.matrix_world.to_3x3() @ poly.normal).normalized()
    faces.append((region, centre, normal))

if not names:
    names = sorted(f[3:-4] for f in os.listdir(fbx_dir) if f.startswith("SK_") and f.endswith(".fbx"))
result = json.load(open(out_path)) if os.path.exists(out_path) else {}
for name in names:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(fbx_dir, f"SK_{name}.fbx"))
    new = set(bpy.data.objects) - before
    meshes = [o for o in new if o.type == "MESH"]
    bm = bmesh.new()
    for obj in meshes:
        tmp = obj.data.copy()
        tmp.transform(obj.matrix_world)
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    covered = dict.fromkeys(REGIONS, 0)
    total = dict.fromkeys(REGIONS, 0)
    for region, centre, normal in faces:
        total[region] += 1
        hit = tree.ray_cast(centre + normal * 0.05, normal, MAX_GAP)
        if hit[0] is not None:
            covered[region] += 1
    shares = {r: covered[r] / total[r] for r in REGIONS if total[r]}
    hidden = [r for r in REGIONS if shares.get(r, 0) >= HIDE_AT]
    result[name] = {"hidden": hidden, "shares": {r: round(s, 3) for r, s in shares.items() if s > 0.02}}
    print("COVER", name, hidden, result[name]["shares"])
    for obj in new:
        bpy.data.objects.remove(obj)

json.dump(result, open(out_path, "w"), indent=1)
