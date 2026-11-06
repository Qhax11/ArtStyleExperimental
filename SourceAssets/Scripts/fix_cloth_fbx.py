"""Make a clothing FBX deform with the body, and drop its hidden geometry. Every clothing item goes through this.

Two fixes, both needed once idle and final-pose animations play:

1. Hidden geometry. VRoid costumes are often one mesh whose unused areas are made
   invisible with texture alpha (for example a dress top hidden under a hoodie). In
   Unreal those faces still bend and poke through other layers. Faces whose texture is
   fully transparent, in materials that use alpha (MToon MASK or BLEND), are deleted.

2. Skin weights. Costumes fitted from another model, with their extra bones merged into
   the nearest body bone, bend differently from the skin and from each other. Vertices
   close to the body take the body's weights at the nearest surface point, so all layers
   bend together. Vertices far from the body (skirt hems, wide sleeves) keep their own
   weights, with a smooth blend in between.

Run headless on the full-body parts file, which holds the body mesh and the armature:
  blender evrar_full_parts.blend --background --python fix_cloth_fbx.py -- \
      <input.fbx> <output.fbx> [--vrm <source.vrm>] [--near CM] [--far CM]

--vrm    the VRM the costume came from; it supplies the textures for step 1.
--near   up to this distance from the skin a vertex fully takes the body weights (default 3).
--far    from this distance on a vertex keeps its own weights (default 10).
--tuck-above CM, --tuck CM
         pull vertices higher than --tuck-above toward the skin by up to --tuck, so a
         bottom's waistband stays inside the top worn over it.

The .blend file is opened but never saved.
"""
import array
import os
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from vroid_fbx_common import prepare_armature  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
in_path, out_path = args[0], args[1]
options = dict(zip(args[2::2], args[3::2]))
vrm_path = options.get("--vrm")
near = float(options.get("--near", 3.0))
far = float(options.get("--far", 10.0))
tuck_above = float(options.get("--tuck-above", 1e9))
tuck = float(options.get("--tuck", 0.0))
os.makedirs(os.path.dirname(out_path), exist_ok=True)

scene = bpy.context.scene
armature = prepare_armature()
body = bpy.data.objects["BodyOnly"]

# --- Textures and alpha modes from the source VRM, keyed by material name. ---
alpha_maps = {}
if vrm_path:
    before_objects, before_mats = set(bpy.data.objects), set(bpy.data.materials)
    bpy.ops.import_scene.vrm(filepath=vrm_path)
    for mat in set(bpy.data.materials) - before_mats:
        mtoon = mat.vrm_addon_extension.mtoon1
        if mtoon.alpha_mode not in {"MASK", "BLEND"}:
            continue
        image = mtoon.pbr_metallic_roughness.base_color_texture.index.source
        if image is None:
            continue
        w, h = image.size
        pixels = array.array("f", [0.0]) * (w * h * 4)
        image.pixels.foreach_get(pixels)
        alpha_maps[mat.name] = (w, h, pixels[3::4])
    for obj in set(bpy.data.objects) - before_objects:
        bpy.data.objects.remove(obj)
    for mat in set(bpy.data.materials) - before_mats:
        mat.name = "VRMSRC_" + mat.name  # Frees the names for the FBX materials.
print("CLOTH alpha materials:", sorted(alpha_maps))

# --- The clothing FBX, moved onto the body armature. ---
# Materials already in the .blend would make the FBX ones import as "<name>.001",
# which would rename the material slots in Unreal.
for mat in bpy.data.materials:
    if not mat.name.startswith("VRMSRC_"):
        mat.name = "BLEND_" + mat.name
before = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=in_path)
imported = set(bpy.data.objects) - before
meshes = [o for o in imported if o.type == "MESH"]
for obj in meshes:
    obj.data.transform(obj.matrix_world)
    obj.parent = armature
    obj.matrix_parent_inverse.identity()
    obj.matrix_world = armature.matrix_world.copy()
    for mod in obj.modifiers:
        if mod.type == "ARMATURE":
            mod.object = armature
for obj in imported - set(meshes):
    bpy.data.objects.remove(obj)
cloth = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = cloth
    bpy.ops.object.join()
part_name = os.path.splitext(os.path.basename(out_path))[0][3:]  # SK_<Part>.fbx
cloth.name = cloth.data.name = part_name


def z_range(obj):
    zs = [(obj.matrix_world @ v.co).z for v in obj.data.vertices]
    return f"[{min(zs):.1f}, {max(zs):.1f}]"


# Both should be in centimetres, the body spanning about 0..160.
print(f"CLOTH {part_name}: body z={z_range(body)} cloth z={z_range(cloth)}")


def base_name(name):
    return name[:-4] if len(name) > 4 and name[-4] == "." and name[-3:].isdigit() and name not in alpha_maps else name


def alpha_at(material_name, uv):
    w, h, alpha = alpha_maps[material_name]
    x = min(max(int(uv.x % 1.0 * w), 0), w - 1)
    y = min(max(int(uv.y % 1.0 * h), 0), h - 1)
    return alpha[y * w + x]


# --- 1. Delete faces that are fully transparent. ---
me = cloth.data
bm = bmesh.new()
bm.from_mesh(me)
uv_layer = bm.loops.layers.uv.active
hidden = []
for face in bm.faces:
    mat = me.materials[face.material_index]
    key = mat.name if mat and mat.name in alpha_maps else (base_name(mat.name) if mat else None)
    if key not in alpha_maps:
        continue
    uvs = [loop[uv_layer].uv for loop in face.loops]
    samples = uvs + [sum(uvs, Vector((0.0, 0.0))) / len(uvs)]
    if max(alpha_at(key, uv) for uv in samples) < 0.05:
        hidden.append(face)
bmesh.ops.delete(bm, geom=hidden, context="FACES")
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
bm.to_mesh(me)
bm.free()
used = {p.material_index for p in me.polygons}
for i in reversed(range(len(me.materials))):
    if i not in used:
        me.materials.pop(index=i)
print(f"CLOTH {part_name}: removed {len(hidden)} transparent faces, materials={[m.name for m in me.materials]}")

# --- 2. Body weights near the skin. ---
body_bm = bmesh.new()
body_bm.from_mesh(body.data)
bmesh.ops.triangulate(body_bm, faces=body_bm.faces)
body_bm.verts.ensure_lookup_table()
body_bm.faces.ensure_lookup_table()
tree = BVHTree.FromBMesh(body_bm)
body_groups = {g.index: g.name for g in body.vertex_groups}
body_weights = [{body_groups[g.group]: g.weight for g in v.groups if g.weight > 0} for v in body.data.vertices]
triangles = [[v.index for v in f.verts] for f in body_bm.faces]
positions = [v.co.copy() for v in body_bm.verts]

tucked = 0
if tuck > 0.0:
    for v in me.vertices:
        if v.co.z <= tuck_above:
            continue
        hit, _, _, distance = tree.find_nearest(v.co)
        if hit is not None and distance > 0.3:
            v.co = v.co + (hit - v.co).normalized() * min(tuck, distance - 0.3)
            tucked += 1
    print(f"CLOTH {part_name}: tucked {tucked} vertices above {tuck_above} cm by up to {tuck} cm")

cloth_groups = {g.index: g.name for g in cloth.vertex_groups}
new_weights = []
far_count = near_count = 0
for v in me.vertices:
    own = {cloth_groups[g.group]: g.weight for g in v.groups if g.weight > 0}
    hit, _, face_index, distance = tree.find_nearest(v.co)
    t = min(max((distance - near) / max(far - near, 1e-6), 0.0), 1.0) if hit else 1.0
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
body_bm.free()

cloth.vertex_groups.clear()
for index, weights in enumerate(new_weights):
    for bone, weight in weights.items():
        group = cloth.vertex_groups.get(bone) or cloth.vertex_groups.new(name=bone)
        group.add([index], weight, "REPLACE")
print(f"CLOTH {part_name}: verts={len(me.vertices)} body-weighted={near_count} own={far_count} "
      f"blended={len(me.vertices) - near_count - far_count}")

bpy.ops.object.select_all(action="DESELECT")
armature.select_set(True)
cloth.select_set(True)
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
print("CLOTH wrote:", out_path, os.path.getsize(out_path))
