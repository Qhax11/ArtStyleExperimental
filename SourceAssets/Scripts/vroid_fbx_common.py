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
