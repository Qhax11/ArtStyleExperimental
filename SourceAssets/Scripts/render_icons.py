"""Render a 256 px icon for every built item, with its own texture, on a transparent background.

Run headless:
  blender --background --python render_icons.py -- <jobs.json> <out_dir> [<first> <count>]
Writes <out_dir>/T_Icon_<Item>.png.
"""
import json
import math
import os
import re
import sys

import bmesh
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
jobs = json.load(open(args[0]))
out_dir = os.path.abspath(args[1])
if len(args) >= 4:
    jobs = jobs[int(args[2]):int(args[2]) + int(args[3])]
os.makedirs(out_dir, exist_ok=True)
SIZE = 256


def clean(name):
    return re.sub(r"\.\d{3}$", "", name)


def flat_material(src):
    """Unlit-ish copy of a VRM material: base colour texture, alpha clipped."""
    mtoon = src.vrm_addon_extension.mtoon1
    image = mtoon.pbr_metallic_roughness.base_color_texture.index.source
    factor = list(mtoon.pbr_metallic_roughness.base_color_factor)
    mat = bpy.data.materials.new("ICON_" + src.name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")
    diffuse = nt.nodes.new("ShaderNodeBsdfDiffuse")
    add = nt.nodes.new("ShaderNodeAddShader")
    mix = nt.nodes.new("ShaderNodeMixShader")
    transp = nt.nodes.new("ShaderNodeBsdfTransparent")
    tint = nt.nodes.new("ShaderNodeMix")
    tint.data_type = "RGBA"
    tint.blend_type = "MULTIPLY"
    tint.inputs[0].default_value = 1.0
    tint.inputs[7].default_value = factor
    emit.inputs["Strength"].default_value = 0.75
    if image is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = image
        nt.links.new(tex.outputs["Color"], tint.inputs[6])
        alpha = tex.outputs["Alpha"]
    else:
        tint.inputs[6].default_value = (1, 1, 1, 1)
        alpha = None
    nt.links.new(tint.outputs[2], emit.inputs["Color"])
    nt.links.new(tint.outputs[2], diffuse.inputs["Color"])
    nt.links.new(emit.outputs[0], add.inputs[0])
    nt.links.new(diffuse.outputs[0], add.inputs[1])
    if alpha is not None:
        clip = nt.nodes.new("ShaderNodeMath")
        clip.operation = "GREATER_THAN"
        clip.inputs[1].default_value = 0.5
        nt.links.new(alpha, clip.inputs[0])
        nt.links.new(clip.outputs[0], mix.inputs[0])
    else:
        mix.inputs[0].default_value = 1.0
    nt.links.new(transp.outputs[0], mix.inputs[1])
    nt.links.new(add.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    mat.blend_method = "CLIP" if hasattr(mat, "blend_method") else None
    return mat


def setup_scene():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in {
        e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items} else "BLENDER_EEVEE"
    scene.render.resolution_x = scene.render.resolution_y = SIZE * 2
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("IconWorld")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.6, 0.6, 0.6, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
    scene.world = world
    sun = bpy.data.lights.new("Sun", "SUN")
    sun.energy = 2.0
    sun_obj = bpy.data.objects.new("Sun", sun)
    sun_obj.rotation_euler = (math.radians(50), 0, math.radians(-30))
    scene.collection.objects.link(sun_obj)
    cam_data = bpy.data.cameras.new("IconCam")
    cam_data.type = "ORTHO"
    cam = bpy.data.objects.new("IconCam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    return cam


def render_job(job):
    bpy.ops.wm.read_homefile(use_empty=True)
    cam = setup_scene()
    bpy.ops.import_scene.vrm(filepath=job["vrm"])
    sources = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for o in sources:
        o.hide_render = True
    by_name = {}
    for mat in bpy.data.materials:
        by_name.setdefault(clean(mat.name), mat)
    for item in job["items"]:
        mats = [by_name.get(n) for n in item["materials"]]
        if any(m is None for m in mats):
            print("ICON missing material", item["name"])
            continue
        wanted = set(mats)
        pieces = []
        for src in sources:
            if not any(s.material in wanted for s in src.material_slots):
                continue
            obj = src.copy()
            obj.data = src.data.copy()
            bpy.context.scene.collection.objects.link(obj)
            obj.hide_render = False
            me = obj.data
            bm = bmesh.new()
            bm.from_mesh(me)
            keep = {i for i, m in enumerate(me.materials) if m in wanted}
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index not in keep], context="FACES")
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
            bm.to_mesh(me)
            bm.free()
            for i, m in enumerate(me.materials):
                if m in wanted:
                    me.materials[i] = flat_material(m)
            pieces.append(obj)
        if not pieces:
            continue
        # Evaluated (posed, shape-keyed) positions for framing.
        dg = bpy.context.evaluated_depsgraph_get()
        pts = []
        for obj in pieces:
            ev = obj.evaluated_get(dg)
            me = ev.to_mesh()
            pts += [obj.matrix_world @ v.co for v in me.vertices]
            ev.to_mesh_clear()
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        center = (lo + hi) / 2
        size = max(hi.x - lo.x, hi.z - lo.z)
        cam.data.ortho_scale = size * 1.12
        yaw = math.radians(25 if item["name"].startswith("Shoes") else 0)
        dist = max(hi - lo) * 3 + 1
        cam.location = center + Vector((math.sin(yaw), -math.cos(yaw), 0)) * dist
        cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
        cam.data.clip_end = dist * 3
        bpy.context.scene.render.filepath = os.path.join(out_dir, f"T_Icon_{item['name']}.png")
        bpy.ops.render.render(write_still=True)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        print("ICON", item["name"])


for job in jobs:
    try:
        render_job(job)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        print("ICON failed", job["vrm"], exc)
