"""Split the body mesh into one material section per body region and export it as FBX.

Unreal hides a region with ShowMaterialSection, so clothes can hide the skin under them
without touching the VRM4U MToon master material. Each face goes to the region of its
strongest bone.

Run headless:
  blender <stem>_parts.blend --background --python split_body_regions.py -- <output.fbx>

The .blend file is opened but never saved.
"""
import os
import sys

import bpy
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from vroid_fbx_common import prepare_armature  # noqa: E402

out_path = sys.argv[sys.argv.index("--") + 1]
os.makedirs(os.path.dirname(out_path), exist_ok=True)

# Checked in order: first fragment found in the bone name wins.
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

# Hips faces above this height (as a fraction of body height) go to Belly. By weight alone
# the Hips region reaches above the shorts' waistband (0.96 m of 1.59 m), so hiding it
# under shorts left a notch at the waist.
HIPS_TOP_RATIO = 0.95 / 1.59

# Foot faces above this height (cm, after prepare_armature) go to Ankle, so low shoes can
# hide only what they cover. The line follows the opening of a low shoe (Mary Jane): low
# at the toes, high at the heel. Points are (y, height); the character faces -Y.
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
    raise ValueError(f"No region rule for bone {bone_name}")


armature = prepare_armature()
body = bpy.data.objects["BodyOnly"]
me = body.data
group_region = {g.index: region_of(g.name) for g in body.vertex_groups}

source_material = me.materials[0]
me.materials.clear()
index_of = {}
for region in REGIONS:
    mat = source_material.copy()
    mat.name = f"Region_{region}"
    me.materials.append(mat)
    index_of[region] = len(me.materials) - 1

heights = [(body.matrix_world @ v.co).z for v in me.vertices]
z_min, z_max = min(heights), max(heights)
hips_top = z_min + HIPS_TOP_RATIO * (z_max - z_min)

counts = dict.fromkeys(REGIONS, 0)
for poly in me.polygons:
    totals = dict.fromkeys(REGIONS, 0.0)
    for vertex_index in poly.vertices:
        for g in me.vertices[vertex_index].groups:
            totals[group_region[g.group]] += g.weight
    region = max(REGIONS, key=lambda r: totals[r])
    if region == "Hips" and sum(heights[i] for i in poly.vertices) / len(poly.vertices) > hips_top:
        region = "Belly"
    if region == "Foot":
        centre = sum((body.matrix_world @ me.vertices[i].co for i in poly.vertices), Vector()) / len(poly.vertices)
        if centre.z > foot_top(centre.y):
            region = "Ankle"
    poly.material_index = index_of[region]
    counts[region] += 1

print("REGION faces:", counts)
empty = [r for r, n in counts.items() if n == 0]
if empty:
    raise RuntimeError(f"Empty regions: {empty}")

bpy.ops.object.select_all(action="DESELECT")
armature.select_set(True)
body.select_set(True)
bpy.context.view_layer.objects.active = armature
bpy.ops.export_scene.fbx(
    filepath=out_path,
    use_selection=True,
    object_types={"ARMATURE", "MESH"},
    add_leaf_bones=False,
    bake_anim=False,
    mesh_smooth_type="FACE",
    use_mesh_modifiers=False,
    primary_bone_axis="Y",
    secondary_bone_axis="X",
    axis_forward="-Y",
    axis_up="Z",
)
print("REGION wrote:", out_path, os.path.getsize(out_path))
