"""Export parts from <stem>_parts.blend as FBX files for Unreal.

Run headless:
  blender <stem>_parts.blend --background --python export_parts_fbx.py -- <output_dir> <Part> [<Part> ...]

The .blend file is opened but never saved.
"""
import os
import sys

import bpy

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from vroid_fbx_common import prepare_armature  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
out_dir, part_names = args[0], args[1:]
os.makedirs(out_dir, exist_ok=True)

armature = prepare_armature()

for part in part_names:
    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.data.objects[part].select_set(True)
    bpy.context.view_layer.objects.active = armature
    path = os.path.join(out_dir, f"SK_{part}.fbx")
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
    print("EXPORT wrote:", path, os.path.getsize(path))
