"""Bake a short test pose (arms down, head turned, one leg lifted) to an FBX for Unreal.

Run headless:
  blender <stem>_parts.blend --background --python export_test_pose_fbx.py -- <output.fbx>

The .blend file is opened but never saved.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from vroid_fbx_common import prepare_armature  # noqa: E402

cli = sys.argv[sys.argv.index("--") + 1:]
out_path = cli[0]
stand_only = len(cli) > 1 and cli[1] == "stand"  # Arms down only: a neutral standing pose.
os.makedirs(os.path.dirname(out_path), exist_ok=True)

armature = prepare_armature()

# Bone -> (world axis, degrees). Axes are Blender world space; the character faces -Y.
ROTATIONS = {
    "J_Bip_L_UpperArm": ("Y", 65),
    "J_Bip_R_UpperArm": ("Y", -65),
    "J_Bip_C_Head": ("Z", 25),
    "J_Bip_C_Spine": ("Z", -12),
    "J_Bip_L_UpperLeg": ("X", 35),
    "J_Bip_L_LowerLeg": ("X", -45),
}

if stand_only:
    ROTATIONS = {"J_Bip_L_UpperArm": ("Y", 72), "J_Bip_R_UpperArm": ("Y", -72)}

scene = bpy.context.scene
scene.frame_start, scene.frame_end = 1, 2
bpy.ops.object.mode_set(mode="POSE")

for name, (axis, degrees) in ROTATIONS.items():
    pose_bone = armature.pose.bones[name]
    pose_bone.rotation_mode = "QUATERNION"
    # Rest rotation is identity after prepare_armature, so local equals world.
    pose_bone.rotation_quaternion = Matrix.Rotation(math.radians(degrees), 4, axis).to_quaternion()

for frame in (1, 2):
    for pose_bone in armature.pose.bones:
        if pose_bone.name in ROTATIONS:
            pose_bone.keyframe_insert("rotation_quaternion", frame=frame)
bpy.ops.object.mode_set(mode="OBJECT")

bpy.ops.object.select_all(action="DESELECT")
armature.select_set(True)
bpy.data.objects["Top"].select_set(True)
bpy.context.view_layer.objects.active = armature
bpy.ops.export_scene.fbx(
    filepath=out_path,
    use_selection=True,
    object_types={"ARMATURE", "MESH"},
    add_leaf_bones=False,
    bake_anim=True,
    bake_anim_use_all_actions=False,
    bake_anim_use_nla_strips=False,
    bake_anim_force_startend_keying=True,
    bake_anim_simplify_factor=0.0,
    mesh_smooth_type="FACE",
    primary_bone_axis="Y",
    secondary_bone_axis="X",
    axis_forward="-Y",
    axis_up="Z",
)
print("POSE wrote:", out_path, os.path.getsize(out_path))
