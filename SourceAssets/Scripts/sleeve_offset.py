"""Prints, per arm segment, how far an item's sleeve centre sits from the arm's centre (rest pose).

  blender evrar_full_parts.blend --background --python sleeve_offset.py -- <fbx_dir> <names...>
"""
import glob
import math
import os
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
fbx_dir, names = args[0], args[1:]
body = bpy.data.objects["BodyOnly"]
ref = next(o for o in bpy.context.scene.objects if o.type == "ARMATURE")
bw = body.matrix_world
body_pts = [bw @ v.co for v in body.data.vertices]
body_top = max(p.z for p in body_pts)
groups = {g.index: g.name for g in body.vertex_groups}


def segments():
    out = []
    for side in ("L", "R"):
        for a, b in (("UpperArm", "LowerArm"), ("LowerArm", "Hand")):
            ba = ref.data.bones[f"J_Bip_{side}_{a}"]
            bb = ref.data.bones[f"J_Bip_{side}_{b}"]
            out.append((f"{side}_{a}", ref.matrix_world @ ba.head_local, ref.matrix_world @ bb.head_local))
    return out


def ring_centre(points, head, tail, t0, t1):
    axis = tail - head
    length = axis.length
    axis.normalize()
    sel = []
    for p in points:
        t = (p - head).dot(axis) / length
        if t0 <= t <= t1:
            radial = (p - head) - axis * ((p - head).dot(axis))
            if radial.length < length * 0.6:
                sel.append(radial)
    if len(sel) < 8:
        return None, 0
    # Middle of the cross-section's extent: vertex density does not pull it.
    lo = Vector((min(v.x for v in sel), min(v.y for v in sel), min(v.z for v in sel)))
    hi = Vector((max(v.x for v in sel), max(v.y for v in sel), max(v.z for v in sel)))
    return (lo + hi) / 2, len(sel)


segs = segments()
arm_pts = [p for p, v in zip(body_pts, body.data.vertices)
           if any(("Arm" in groups[g.group] or "Hand" in groups[g.group]) and g.weight > 0.5 for g in v.groups)]
for name in names:
    path = os.path.join(fbx_dir, f"SK_{name}.fbx")
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    new = set(bpy.data.objects) - before
    mesh = next(o for o in new if o.type == "MESH")
    pts = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
    scale = 10 ** round(math.log10(body_top / max(p.z for p in pts)))
    pts = [p * scale for p in pts]
    print("ITEM", name)
    for seg, head, tail in segs:
        for t0, t1 in ((0.2, 0.4), (0.5, 0.7), (0.8, 0.95)):
            c_arm, n_arm = ring_centre(arm_pts, head, tail, t0, t1)
            c_cloth, n_cloth = ring_centre(pts, head, tail, t0, t1)
            if c_arm is None or c_cloth is None or n_cloth < 8:
                continue
            d = (c_cloth - c_arm) * (100.0 if body_top < 10 else 1.0)
            print(f"  {seg} {t0:.1f}-{t1:.1f}: offset cm x={d.x:+.2f} y={d.y:+.2f} z={d.z:+.2f} (cloth {n_cloth}, arm {n_arm})")
    for o in new:
        bpy.data.objects.remove(o)
