"""Shared preparation for FBX exports that must match the VRM4U skeleton in Unreal."""
import bpy
from mathutils import Matrix

# VRM4U names this bone with a hyphen; Blender's importer produced a space.
BONE_RENAMES = {
    "J_Sec_R_TopsUpperLegBack_end 1_01": "J_Sec_R_TopsUpperLegBack_end-1_01",
    "J_Sec_R_TopsUpperLegBack_end 1_01_end": "J_Sec_R_TopsUpperLegBack_end-1_01_end",
}


def prepare_armature():
    """Make the armature match SKEL_evrar and return it.

    VRM4U's reference pose keeps every bone's rotation at identity, while the
    Blender importer points bones along their children. Leader Pose and
    animations rely on identical reference rotations, so all bones are reset to
    identity here. Bone positions and skin weights are unchanged.

    The scene is also converted to centimetres with all scales applied. Unreal
    otherwise imports a bone scale of 100, which collapses the mesh under Leader
    Pose because the VRM4U body has a bone scale of 1.
    """
    armature = next(o for o in bpy.context.scene.objects if o.type == "ARMATURE")
    armature.name = "Armature"  # Unreal then adds no extra root bone.
    for old, new in BONE_RENAMES.items():
        bone = armature.data.bones.get(old)
        if bone:
            bone.name = new  # Vertex groups follow the rename.

    # Scale the data rather than the objects: meshes are parented to the armature,
    # so object scales would compound.
    bpy.context.scene.unit_settings.scale_length = 0.01
    to_cm = Matrix.Scale(100.0, 4)
    bpy.context.view_layer.objects.active = armature
    armature.data.transform(to_cm)
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(to_cm)
        if obj.type in {"ARMATURE", "MESH"}:
            obj.location = [v * 100.0 for v in obj.location]

    bpy.ops.object.mode_set(mode="EDIT")
    for edit_bone in armature.data.edit_bones:
        edit_bone.use_connect = False
    for edit_bone in armature.data.edit_bones:
        head = edit_bone.head.copy()
        edit_bone.tail = (head.x, head.y + 5.0, head.z)
        edit_bone.roll = 0.0
    bpy.ops.object.mode_set(mode="OBJECT")
    return armature


def bake_deform_animation(deform, first, rest_old_inv=None):
    """Prepare the armature and key an animation that reproduces recorded deformations.

    ``deform`` holds one dict per frame, mapping each bone name to the matrix it applies
    to the mesh (pose @ rest^-1) in the original Blender units. That matrix does not
    depend on the bones' rest orientation, so it survives prepare_armature(), which
    resets every bone to identity rotation and converts to centimetres.

    Returns the prepared armature, with frames first .. first + len(deform) - 1 keyed.
    """
    armature = next(o for o in bpy.context.scene.objects if o.type == "ARMATURE")
    if armature.animation_data:
        armature.animation_data.action = None
    for pose_bone in armature.pose.bones:
        pose_bone.matrix_basis = Matrix.Identity(4)

    armature = prepare_armature()
    for old, new in BONE_RENAMES.items():
        for frame_deform in deform:
            if old in frame_deform:
                frame_deform[new] = frame_deform.pop(old)
    to_cm = Matrix.Scale(100.0, 4)
    from_cm = to_cm.inverted()

    bones = armature.data.bones
    order = [b.name for b in bones if b.parent is None]
    for name in order:  # Parents before children.
        order.extend(child.name for child in bones[name].children)

    bpy.ops.object.mode_set(mode="POSE")
    for pose_bone in armature.pose.bones:
        pose_bone.rotation_mode = "QUATERNION"
    for index, frame_deform in enumerate(deform):
        frame = first + index
        targets = {}
        for name in order:
            bone = bones[name]
            target = to_cm @ frame_deform[name] @ from_cm @ bone.matrix_local
            targets[name] = target
            if bone.parent:
                rest_rel = bone.parent.matrix_local.inverted() @ bone.matrix_local
                basis = rest_rel.inverted() @ targets[bone.parent.name].inverted() @ target
            else:
                basis = bone.matrix_local.inverted() @ target
            pose_bone = armature.pose.bones[name]
            loc, rot, _ = basis.decompose()
            pose_bone.location = loc
            pose_bone.rotation_quaternion = rot
            pose_bone.keyframe_insert("location", frame=frame)
            pose_bone.keyframe_insert("rotation_quaternion", frame=frame)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.scene.frame_start = first
    bpy.context.scene.frame_end = first + len(deform) - 1
    return armature


def export_animation_fbx(armature, mesh_name, out_path):
    """Export the armature's animation together with one mesh, as Unreal expects."""
    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.data.objects[mesh_name].select_set(True)
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
