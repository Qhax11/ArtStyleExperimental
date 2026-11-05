"""Move parts of a VRoid VRM onto the body skeleton and export each part as FBX.

Bones the body skeleton lacks (hoodie strings, colliders) would not follow Leader Pose
in Unreal, so their weights are merged into the nearest ancestor the body has.

Run headless:
  blender <stem>_parts.blend --background --python retarget_costume_fbx.py -- \
      <input.vrm> <output_dir> <Spec> [<Spec> ...]

A Spec builds one FBX named SK_<Part>.fbx:
  Part=Mesh                     the whole mesh
  Part=Mesh:frag1,frag2         only faces whose material name contains a fragment
  Part=MeshA+MeshB:frag         several sources joined into one part

The .blend file is opened but never saved.
"""
import os
import re
import sys

import bmesh
import bpy

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from vroid_fbx_common import BONE_RENAMES, prepare_armature  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
vrm_path, out_dir, specs = args[0], args[1], args[2:]
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
sources = [o for o in bpy.context.scene.objects if o.type == "MESH"]


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


def extract(mesh_name, fragments):
    """Copy a source mesh, keeping only faces whose material matches a fragment."""
    source = bpy.data.objects[mesh_name]
    obj = source.copy()
    obj.data = source.data.copy()
    obj.shape_key_clear()
    bpy.context.scene.collection.objects.link(obj)
    me = obj.data
    if fragments:
        keep = {i for i, mat in enumerate(me.materials)
                if mat and any(f in mat.name for f in fragments)}
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index not in keep],
                         context="FACES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bm.to_mesh(me)
        bm.free()
    used = {p.material_index for p in me.polygons}
    for i in reversed(range(len(me.materials))):
        if i not in used:
            me.materials.pop(index=i)
    return obj


parts = []
for spec in specs:
    part, recipe = spec.split("=", 1)
    pieces = []
    for item in recipe.split("+"):
        mesh_name, _, frag_text = item.partition(":")
        pieces.append(extract(mesh_name, [f for f in frag_text.split(",") if f]))
    if len(pieces) > 1:
        bpy.ops.object.select_all(action="DESELECT")
        for piece in pieces:
            piece.select_set(True)
        bpy.context.view_layer.objects.active = pieces[0]
        bpy.ops.object.join()
    obj = pieces[0]
    merged = merge_weights(obj)
    unweighted = sum(1 for v in obj.data.vertices if not v.groups)
    zs = [(obj.matrix_world @ v.co).z for v in obj.data.vertices]
    print(f"COSTUME {part}: verts={len(obj.data.vertices)} faces={len(obj.data.polygons)} "
          f"merged_groups={len(merged)} into={sorted(set(merged.values()))} "
          f"unweighted={unweighted} z=[{min(zs):.3f},{max(zs):.3f}] "
          f"materials={[m.name for m in obj.data.materials]}")
    obj.parent = reference
    obj.matrix_parent_inverse.identity()
    for mod in obj.modifiers:
        if mod.type == "ARMATURE":
            mod.object = reference
    obj.name = part
    obj.data.name = part
    parts.append(obj)

for obj in sources + [costume_arm]:
    bpy.data.objects.remove(obj)

armature = prepare_armature()
assert armature == reference

for obj in parts:
    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = armature
    path = os.path.join(out_dir, f"SK_{obj.name}.fbx")
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
