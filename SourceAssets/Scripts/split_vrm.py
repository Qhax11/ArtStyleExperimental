"""Split a VRoid VRM into dress-up parts, keeping skin weights.

Run headless:
  blender --background --python split_vrm.py -- <input.vrm> <output_dir>

Writes <output_dir>/<stem>_parts.blend and preview PNGs, and prints a report.
The input VRM is never modified.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
vrm_path, out_dir = args[0], args[1]
stem = os.path.splitext(os.path.basename(vrm_path))[0]
os.makedirs(out_dir, exist_ok=True)

# Material name fragment -> part name. Checked in order.
PARTS = [
    ("_Tops_", "Top"),
    ("_Bottoms_", "Bottom"),
    ("_Shoes_", "Shoes"),
    ("_HairBack_", "HairBack"),
    ("_Body_", "BodyOnly"),
]

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj)

result = bpy.ops.import_scene.vrm(filepath=vrm_path)
print("SPLIT import:", result)

scene_objs = bpy.context.scene.objects
body = next(o for o in scene_objs if o.type == "MESH" and o.name == "Body")
hair = next(o for o in scene_objs if o.type == "MESH" and o.name == "Hair")
face = next(o for o in scene_objs if o.type == "MESH" and o.name == "Face")
armature = next(o for o in scene_objs if o.type == "ARMATURE")

# Split Body into one object per material.
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.separate(type="MATERIAL")
bpy.ops.object.mode_set(mode="OBJECT")

pieces = [o for o in bpy.context.scene.objects
          if o.type == "MESH" and (o.name == "Body" or o.name.startswith("Body."))]
for piece in pieces:
    slots = [s.material.name for s in piece.material_slots if s.material]
    used = {piece.material_slots[p.material_index].material.name for p in piece.data.polygons}
    # Drop material slots the piece no longer uses.
    for i in reversed(range(len(piece.material_slots))):
        mat = piece.material_slots[i].material
        if mat is None or mat.name not in used:
            piece.data.materials.pop(index=i)
    label = next((part for frag, part in PARTS if any(frag in m for m in used)), None)
    if label is None:
        print("SPLIT unmatched piece:", piece.name, slots)
        continue
    piece.name = label
    piece.data.name = label

# Merge HairBack into the Hair mesh: one hair slot in the game.
hair_back = bpy.data.objects.get("HairBack")
if hair_back:
    bpy.ops.object.select_all(action="DESELECT")
    hair_back.select_set(True)
    hair.select_set(True)
    bpy.context.view_layer.objects.active = hair
    bpy.ops.object.join()

final_names = ["BodyOnly", "Top", "Bottom", "Shoes", "Hair", "Face"]

# Report: size, used weights, boundary edges (open holes in the mesh).
for name in final_names:
    obj = bpy.data.objects[name]
    me = obj.data
    edge_faces = {}
    for poly in me.polygons:
        for key in poly.edge_keys:
            edge_faces[key] = edge_faces.get(key, 0) + 1
    boundary = sum(1 for n in edge_faces.values() if n == 1)
    unweighted = sum(1 for v in me.vertices if not v.groups)
    world = [obj.matrix_world @ v.co for v in me.vertices]
    zs = [c.z for c in world]
    used_groups = {g.group for v in me.vertices for g in v.groups if g.weight > 0}
    print(f"SPLIT part {name}: verts={len(me.vertices)} faces={len(me.polygons)} "
          f"open_edges={boundary} unweighted={unweighted} "
          f"bones_used={len(used_groups)} z=[{min(zs):.3f},{max(zs):.3f}] "
          f"materials={[m.name for m in me.materials]}")

print("SPLIT armature:", armature.name, "bones:", len(armature.data.bones))
print("SPLIT bones:", ",".join(b.name for b in armature.data.bones))

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, f"{stem}_parts.blend"))


# Previews with the Workbench engine so toon materials cannot hide geometry.
def render_view(visible, azimuth_deg, filename):
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.hide_render = obj.name not in visible
    objs = [bpy.data.objects[n] for n in visible]
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p[i] for p in pts) for i in range(3)))
    hi = Vector((max(p[i] for p in pts) for i in range(3)))
    center = (lo + hi) / 2
    size = max(hi - lo)

    cam_data = bpy.data.cameras.new("PreviewCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = size * 1.1
    cam = bpy.data.objects.new("PreviewCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    az = math.radians(azimuth_deg)
    # VRM characters face -Y in Blender.
    offset = Vector((math.sin(az), -math.cos(az), 0)) * (size * 3)
    cam.location = center + offset
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()

    scene = bpy.context.scene
    scene.camera = cam
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (0.75, 0.75, 0.75)
    scene.display.shading.show_backface_culling = True
    scene.render.resolution_x = 700
    scene.render.resolution_y = 1000
    scene.render.film_transparent = False
    scene.render.filepath = os.path.join(out_dir, filename)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


render_view(["BodyOnly", "Face"], 0, "preview_body_front.png")
render_view(["BodyOnly", "Face"], 180, "preview_body_back.png")
print("SPLIT done")
