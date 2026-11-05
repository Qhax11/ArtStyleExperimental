"""Print a VRM's meshes, materials and bones, and compare bones with a reference VRM.

Run headless:
  blender --background --python inspect_vrm.py -- <input.vrm> [<reference.vrm>]
"""
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:]


def load(path):
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj)
    bpy.ops.import_scene.vrm(filepath=path)
    arm = next(o for o in bpy.context.scene.objects if o.type == "ARMATURE")
    return arm, {b.name: tuple(round(v, 4) for v in b.head_local) for b in arm.data.bones}


arm, bones = load(args[0])
print("VRM bones:", len(bones))
for obj in bpy.context.scene.objects:
    if obj.type != "MESH":
        continue
    me = obj.data
    counts = {}
    for poly in me.polygons:
        counts[poly.material_index] = counts.get(poly.material_index, 0) + 1
    print(f"VRM mesh {obj.name}: verts={len(me.vertices)} faces={len(me.polygons)}")
    for i, mat in enumerate(me.materials):
        print(f"VRM   slot {i}: {mat.name if mat else None} faces={counts.get(i, 0)}")

if len(args) > 1:
    _, ref = load(args[1])
    print("VRM only_in_input:", sorted(set(bones) - set(ref)))
    print("VRM only_in_reference:", sorted(set(ref) - set(bones)))
    moved = {k: (bones[k], ref[k]) for k in set(bones) & set(ref)
             if max(abs(a - b) for a, b in zip(bones[k], ref[k])) > 0.001}
    print("VRM moved_bones:", len(moved), dict(list(sorted(moved.items()))[:10]))
