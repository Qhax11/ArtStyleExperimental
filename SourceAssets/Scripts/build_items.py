"""Build many dress-up items from VRoid exports in one Blender session.

For every source VRM it does what retarget_costume_fbx.py and fix_cloth_fbx.py do for a
single item, so every clothing item still goes through the cloth pipeline:

  1. faces of the item's materials are copied out of the VRM meshes and moved down by the
     source's lift (VRoid raises the whole model by the heel height of the shoes it wears, so
     a top from such an export sits up to 3 cm high on evrar: sleeves flare out when the arms
     come down and the bust pokes through). Shoes keep their place, so heels stay on the floor,
  2. bones the body skeleton lacks are merged into the nearest body bone,
  3. (clothing) faces whose texture is fully transparent are deleted,
  4. (clothing) vertices near the skin take the body's skin weights (3 cm full, 10 cm none),
  5. the item is exported as FBX on the prepared body armature (centimetres, identity bones).

Hair and VRoid accessories (hats, glasses) skip steps 3 and 4, as before.
Material slots are renamed <Item>_M<i> in the order given, so Unreal slot names are stable.

Run headless:
  blender --background --python build_items.py -- <jobs.json> <out_dir> [<first> <count>]
jobs.json: [{"vrm": path, "items": [{"name": "Top_001", "kind": "cloth|hair|rigid",
                                     "materials": [VRM material names]}]}]
"""
import array
import json
import os
import re
import sys
import time

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from vroid_fbx_common import BONE_RENAMES, prepare_armature  # noqa: E402

REFERENCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "VRoid", "parts_full",
                         "evrar_full_parts.blend")
NEAR, FAR = 3.0, 10.0

args = sys.argv[sys.argv.index("--") + 1:]
jobs = json.load(open(args[0]))
out_dir = args[1]
if len(args) >= 4:
    jobs = jobs[int(args[2]):int(args[2]) + int(args[3])]
os.makedirs(out_dir, exist_ok=True)


def clean(name):
    return re.sub(r"\.\d{3}$", "", name)


def build_vrm(job):
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(REFERENCE))
    reference = next(o for o in bpy.context.scene.objects if o.type == "ARMATURE")
    ref_bones = {BONE_RENAMES.get(b.name, b.name) for b in reference.data.bones} | {
        b.name for b in reference.data.bones}
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH" and obj.name != "BodyOnly":
            bpy.data.objects.remove(obj)
    for mat in bpy.data.materials:
        mat.name = "BLEND_" + mat.name

    before_objs, before_mats = set(bpy.data.objects), set(bpy.data.materials)
    bpy.ops.import_scene.vrm(filepath=job["vrm"])
    new_objs = set(bpy.data.objects) - before_objs
    costume_arm = next(o for o in new_objs if o.type == "ARMATURE")
    lift = (costume_arm.matrix_world @ costume_arm.data.bones["J_Bip_C_Hips"].head_local).z - (
        reference.matrix_world @ reference.data.bones["J_Bip_C_Hips"].head_local).z
    sources = [o for o in new_objs if o.type == "MESH"]
    by_name = {}
    for mat in set(bpy.data.materials) - before_mats:
        by_name.setdefault(clean(mat.name), mat)

    def alpha_map(mat):
        mtoon = mat.vrm_addon_extension.mtoon1
        if mtoon.alpha_mode not in {"MASK", "BLEND"}:
            return None
        image = mtoon.pbr_metallic_roughness.base_color_texture.index.source
        if image is None:
            return None
        w, h = image.size
        pixels = array.array("f", [0.0]) * (w * h * 4)
        image.pixels.foreach_get(pixels)
        return (w, h, pixels[3::4])

    def target_bone(name):
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

    built = []
    for item in job["items"]:
        mats = []
        for name in item["materials"]:
            mat = by_name.get(name)
            if mat is None:
                print("BUILD missing material", job["vrm"], name)
            mats.append(mat)
        if any(m is None for m in mats):
            continue
        wanted = set(mats)
        pieces = []
        for src in sources:
            if not any(s.material in wanted for s in src.material_slots):
                continue
            obj = src.copy()
            obj.data = src.data.copy()
            obj.shape_key_clear()
            bpy.context.scene.collection.objects.link(obj)
            me = obj.data
            keep = {i for i, m in enumerate(me.materials) if m in wanted}
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index not in keep], context="FACES")
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
            bm.to_mesh(me)
            bm.free()
            used = {p.material_index for p in me.polygons}
            for i in reversed(range(len(me.materials))):
                if i not in used:
                    me.materials.pop(index=i)
            if len(me.polygons):
                pieces.append(obj)
            else:
                bpy.data.objects.remove(obj)
        if not pieces:
            print("BUILD no faces", item["name"])
            continue
        if len(pieces) > 1:
            bpy.ops.object.select_all(action="DESELECT")
            for p in pieces:
                p.select_set(True)
            bpy.context.view_layer.objects.active = pieces[0]
            bpy.ops.object.join()
        obj = pieces[0]
        me = obj.data
        item_lift = 0.0 if item["name"].startswith("Shoes") else lift
        if item_lift:
            me.transform(Matrix.Translation((0.0, 0.0, -item_lift)))

        # Transparent faces (clothing only).
        removed = 0
        if item["kind"] == "cloth":
            maps = {m.name: alpha_map(m) for m in mats}
            bm = bmesh.new()
            bm.from_mesh(me)
            uv_layer = bm.loops.layers.uv.active
            hidden = []
            for face in bm.faces:
                amap = maps.get(me.materials[face.material_index].name)
                if not amap:
                    continue
                w, h, alpha = amap
                uvs = [loop[uv_layer].uv for loop in face.loops]
                samples = uvs + [sum(uvs, Vector((0.0, 0.0))) / len(uvs)]
                best = 0.0
                for uv in samples:
                    x = min(max(int(uv.x % 1.0 * w), 0), w - 1)
                    y = min(max(int(uv.y % 1.0 * h), 0), h - 1)
                    best = max(best, alpha[y * w + x])
                if best < 0.05:
                    hidden.append(face)
            removed = len(hidden)
            bmesh.ops.delete(bm, geom=hidden, context="FACES")
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
            bm.to_mesh(me)
            bm.free()
            if not len(me.polygons):
                print("BUILD fully transparent", item["name"])
                bpy.data.objects.remove(obj)
                continue

        # Merge bones the body lacks.
        groups = {g.index: g.name for g in obj.vertex_groups}
        per_vertex = []
        for v in me.vertices:
            weights = {}
            for g in v.groups:
                if g.weight > 0:
                    bone = target_bone(groups[g.group])
                    weights[bone] = weights.get(bone, 0.0) + g.weight
            per_vertex.append(weights)
        obj.vertex_groups.clear()
        for vi, weights in enumerate(per_vertex):
            for bone, weight in weights.items():
                group = obj.vertex_groups.get(bone) or obj.vertex_groups.new(name=bone)
                group.add([vi], min(weight, 1.0), "REPLACE")

        # Stable slot names, in the order of the item's material list.
        for i, mat in enumerate(mats):
            copy = mat.copy()
            copy.name = f"{item['name']}_M{i}"
            for slot in obj.material_slots:
                if slot.material == mat:
                    slot.material = copy
        obj.parent = reference
        obj.matrix_parent_inverse.identity()
        for mod in obj.modifiers:
            if mod.type == "ARMATURE":
                mod.object = reference
        obj.name = obj.data.name = item["name"]
        built.append((obj, item, removed, item_lift))

    for obj in sources + [costume_arm]:
        bpy.data.objects.remove(obj)
    armature = prepare_armature()
    body = bpy.data.objects["BodyOnly"]

    tree = None
    for obj, item, removed, item_lift in built:
        me = obj.data
        note = ""
        if item["kind"] == "cloth":
            if tree is None:
                body_bm = bmesh.new()
                body_bm.from_mesh(body.data)
                bmesh.ops.triangulate(body_bm, faces=body_bm.faces)
                body_bm.verts.ensure_lookup_table()
                body_bm.faces.ensure_lookup_table()
                tree = BVHTree.FromBMesh(body_bm)
                body_groups = {g.index: g.name for g in body.vertex_groups}
                body_weights = [{body_groups[g.group]: g.weight for g in v.groups if g.weight > 0}
                                for v in body.data.vertices]
                triangles = [[v.index for v in f.verts] for f in body_bm.faces]
                positions = [v.co.copy() for v in body_bm.verts]
                body_bm.free()
            cloth_groups = {g.index: g.name for g in obj.vertex_groups}
            new_weights = []
            near_count = far_count = 0
            for v in me.vertices:
                own = {cloth_groups[g.group]: g.weight for g in v.groups if g.weight > 0}
                hit, _, face_index, distance = tree.find_nearest(v.co)
                t = min(max((distance - NEAR) / (FAR - NEAR), 0.0), 1.0) if hit else 1.0
                mixed = {}
                if t < 1.0:
                    a, b, c = triangles[face_index]
                    bary = barycentric_transform(hit, positions[a], positions[b], positions[c],
                                                 Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))
                    for corner, share in zip((a, b, c), bary):
                        for bone, weight in body_weights[corner].items():
                            mixed[bone] = mixed.get(bone, 0.0) + (1.0 - t) * max(share, 0.0) * weight
                for bone, weight in own.items():
                    mixed[bone] = mixed.get(bone, 0.0) + t * weight
                total = sum(mixed.values()) or 1.0
                new_weights.append({bone: w / total for bone, w in mixed.items() if w / total > 0.001})
                near_count += t == 0.0
                far_count += t == 1.0
            obj.vertex_groups.clear()
            for index, weights in enumerate(new_weights):
                for bone, weight in weights.items():
                    group = obj.vertex_groups.get(bone) or obj.vertex_groups.new(name=bone)
                    group.add([index], weight, "REPLACE")
            note = f" transparent_removed={removed} body={near_count} own={far_count}"
        zs = [v.co.z for v in me.vertices]
        bpy.ops.object.select_all(action="DESELECT")
        armature.select_set(True)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = armature
        path = os.path.join(out_dir, f"SK_{item['name']}.fbx")
        bpy.ops.export_scene.fbx(
            filepath=path, use_selection=True, object_types={"ARMATURE", "MESH"},
            add_leaf_bones=False, bake_anim=False, mesh_smooth_type="FACE",
            use_mesh_modifiers=False, primary_bone_axis="Y", secondary_bone_axis="X",
            axis_forward="-Y", axis_up="Z")
        print(f"BUILD {item['name']}: verts={len(me.vertices)} z=[{min(zs):.1f},{max(zs):.1f}]"
              f" lift={item_lift * 100:.1f}cm slots={[m.name for m in me.materials]}{note}")


for job in jobs:
    start = time.time()
    try:
        build_vrm(job)
    except Exception as exc:  # keep going with the other files
        import traceback
        traceback.print_exc()
        print("BUILD failed", job["vrm"], exc)
    print(f"BUILD file {os.path.basename(job['vrm'])} done in {time.time() - start:.1f}s")
