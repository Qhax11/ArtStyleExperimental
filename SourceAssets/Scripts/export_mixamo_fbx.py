"""Retarget a Mixamo animation (FBX, "Without Skin") to the character and bake it for Unreal.

Both rigs rest in a T-pose, so each mapped bone takes the Mixamo bone's world rotation
relative to its rest. Unmapped bones (hair, clothes, spring bones) follow their parent.
The hips also move, scaled by the ratio of hip heights. The result goes through the
same baking as export_vrma_fbx.py, so it plays on SKEL_evrar_full.

Run headless:
  blender <stem>_parts.blend --background --python export_mixamo_fbx.py -- <input.fbx> <output.fbx> [--arm-spread DEG]

--arm-spread turns both whole arms outward at the shoulder by DEG degrees, so hands that
hang close to the hips do not sink into wide bottoms. Check each new idle with the widest
clothes and raise it when hands clip.

The .blend file is opened but never saved.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from vroid_fbx_common import bake_deform_animation, export_animation_fbx  # noqa: E402

cli = sys.argv[sys.argv.index("--") + 1:]
src_path, out_path = cli[0], cli[1]
options = dict(zip(cli[2::2], cli[3::2]))
arm_spread = math.radians(float(options.get("--arm-spread", 0.0)))
ARM_PARTS = ("UpperArm", "LowerArm", "Hand", "Thumb", "Index", "Middle", "Ring", "Little")
# The character faces -Y with its left side on +X; a turn about Y swings an arm sideways.
SPREAD = {
    "_L_": Matrix.Rotation(-arm_spread, 4, "Y"),
    "_R_": Matrix.Rotation(arm_spread, 4, "Y"),
}


def spread_for(name):
    if arm_spread and any(part in name for part in ARM_PARTS):
        for side, rotation in SPREAD.items():
            if side in name:
                return rotation
    return None


os.makedirs(os.path.dirname(out_path), exist_ok=True)

SIDES = {"Left": "L", "Right": "R"}
LIMBS = {
    "Shoulder": "Shoulder", "Arm": "UpperArm", "ForeArm": "LowerArm", "Hand": "Hand",
    "UpLeg": "UpperLeg", "Leg": "LowerLeg", "Foot": "Foot", "ToeBase": "ToeBase",
}
FINGERS = {"Thumb": "Thumb", "Index": "Index", "Middle": "Middle", "Ring": "Ring", "Pinky": "Little"}
BONE_MAP = {
    "Hips": "J_Bip_C_Hips", "Spine": "J_Bip_C_Spine", "Spine1": "J_Bip_C_Chest",
    "Spine2": "J_Bip_C_UpperChest", "Neck": "J_Bip_C_Neck", "Head": "J_Bip_C_Head",
}
for side, s in SIDES.items():
    for mix, vrm in LIMBS.items():
        BONE_MAP[side + mix] = f"J_Bip_{s}_{vrm}"
    for mix, vrm in FINGERS.items():
        for i in (1, 2, 3):
            BONE_MAP[f"{side}Hand{mix}{i}"] = f"J_Bip_{s}_{vrm}{i}"

scene = bpy.context.scene
target = next(o for o in scene.objects if o.type == "ARMATURE")

before = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=src_path)
source = next(o for o in set(bpy.data.objects) - before if o.type == "ARMATURE")
first, last = (int(round(f)) for f in source.animation_data.action.frame_range)


def src_bone(name):
    return source.pose.bones.get("mixamorig:" + name)


pairs = {vrm: mix for mix, vrm in BONE_MAP.items() if src_bone(mix) and vrm in target.pose.bones}
missing = sorted(set(BONE_MAP.values()) - set(pairs))
print("MIXAMO mapped", len(pairs), "missing", missing)

src_world = source.matrix_world


def src_rest_rot(name):
    return (src_world @ source.data.bones["mixamorig:" + name].matrix_local).to_quaternion()


src_rest = {vrm: src_rest_rot(mix) for vrm, mix in pairs.items()}
hips_src_rest = (src_world @ source.data.bones["mixamorig:Hips"].matrix_local).translation
hips_tgt_rest = (target.matrix_world @ target.data.bones["J_Bip_C_Hips"].matrix_local).translation
height_ratio = hips_tgt_rest.z / hips_src_rest.z

bones = target.data.bones
order = [b.name for b in bones if b.parent is None]
for name in order:  # Parents before children.
    order.extend(child.name for child in bones[name].children)

deform = []
for frame in range(first, last + 1):
    scene.frame_set(frame)
    frame_deform = {}
    for name in order:
        bone = bones[name]
        rest_head = bone.head_local
        parent_deform = frame_deform[bone.parent.name] if bone.parent else Matrix.Identity(4)
        if name in pairs:
            pose = src_world @ src_bone(pairs[name]).matrix
            rotation = (pose.to_quaternion() @ src_rest[name].inverted()).to_matrix().to_4x4()
            spread = spread_for(name)
            if spread is not None:
                rotation = spread @ rotation
        else:
            rotation = parent_deform.to_quaternion().to_matrix().to_4x4()
        head = parent_deform @ rest_head
        if name == "J_Bip_C_Hips":
            offset = (src_world @ src_bone("Hips").matrix).translation - hips_src_rest
            head = rest_head + offset * height_ratio
        frame_deform[name] = Matrix.Translation(head) @ rotation @ Matrix.Translation(-rest_head)
    deform.append(frame_deform)

bpy.data.objects.remove(source)
scene.render.fps = 30
armature = bake_deform_animation(deform, first)
export_animation_fbx(armature, "BodyOnly", out_path)
print("MIXAMO arm spread", math.degrees(arm_spread), "frames", first, last, "fps", scene.render.fps, "wrote:", out_path, os.path.getsize(out_path))
