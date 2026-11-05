"""Move costume meshes from a Dress-up VRM onto the body skeleton and export them as FBX.

Bones the body skeleton lacks (hoodie strings, colliders) would not follow Leader Pose
in Unreal, so their weights are merged into the nearest ancestor the body has.

Run headless:
  blender <stem>_parts.blend --background --python retarget_costume_fbx.py -- \
      <costume.vrm> <output_dir> <prefix> <Mesh> [<Mesh> ...]

The .blend file is opened but never saved.
"""
import os
import re
import sys

import bpy

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from vroid_fbx_common import BONE_RENAMES, prepare_armature  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
vrm_path, out_dir, prefix, mesh_names = args[0], args[1], args[2], args[3:]
os.makedirs(out_dir, exist_ok=True)

reference = next(o for o in bpy.context.scene.objects if o.type == "ARMATURE")
ref_bones = {BONE_RENAMES.get(b.name, b.name) for b in reference.data.bones} | {
    b.name for b in reference.data.bones
}
# The body's own meshes are not needed; removing them leaves costume names free.
for obj in list(bpy.context.scene.objects):
    if obj.type == "MESH":
        bpy.data.objects.remove(obj)

bpy.ops.import_scene.vrm(filepath=vrm_path)
costume_arm = next(o for o in bpy.context.scene.objects
                   if o.type == "ARMATURE" and o != reference)


def target_bone(name):
    """Nearest bone the body skeleton has: the name itself, its base name, or an ancestor."""
    base = re.sub(r"\.\d+$", "", name)
    if base in ref_bones:
        return base
    bone = costume_arm.data.bones.get(name)
    while bone is not None:
        stripped = re.sub(r"\.\d+$", "", bone.name)
        if stripped in ref_bones:
            return stripped
        bone = bone.parent
    return "J_Bip_C_Hips"


def merge_weights(obj):
    """Fold every vertex group into its target bone's group."""
    merged = {}
    me = obj.data
    groups = {g.index: g.name for g in obj.vertex_groups}
    per_vertex = []
    for v in me.vertices:
        weights = {}
        for g in v.groups:
            if g.weight > 0:
                bone = target_bone(groups[g.group])
                if bone != groups[g.group]:
                    merged[groups[g.group]] = bone
                weights[bone] = weights.get(bone, 0.0) + g.weight
        per_vertex.append(weights)
    obj.vertex_groups.clear()
    for v_index, weights in enumerate(per_vertex):
        for bone, weight in weights.items():
            group = obj.vertex_groups.get(bone) or obj.vertex_groups.new(name=bone)
            group.add([v_index], min(weight, 1.0), "REPLACE")
    return merged


kept = []
for name in mesh_names:
    obj = bpy.data.objects[name]
    merged = merge_weights(obj)
    moved_targets = sorted(set(merged.values()))
    unweighted = sum(1 for v in obj.data.vertices if not v.groups)
    print(f"COSTUME {name}: verts={len(obj.data.vertices)} merged_groups={len(merged)} "
          f"into={moved_targets} unweighted={unweighted} "
          f"materials={[m.name for m in obj.data.materials]}")
    obj.parent = reference
    obj.matrix_parent_inverse.identity()
    for mod in obj.modifiers:
        if mod.type == "ARMATURE":
            mod.object = reference
    new_name = f"{prefix}_{name}"
    obj.name = new_name
    obj.data.name = new_name
    kept.append(new_name)

for obj in list(bpy.context.scene.objects):
    if obj.type in {"ARMATURE", "MESH"} and obj != reference and obj.name not in kept:
        bpy.data.objects.remove(obj)

armature = prepare_armature()
assert armature == reference

for name in kept:
    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = armature
    path = os.path.join(out_dir, f"SK_{name}.fbx")
    bpy.ops.export_scene.fbx(
        filepath=path,
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
    print("COSTUME wrote:", path, os.path.getsize(path))
