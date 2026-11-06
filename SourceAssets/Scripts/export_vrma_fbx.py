"""Put a VRM Animation (.vrma) on the character and bake it to an FBX animation for Unreal.

The VRM add-on applies the .vrma to the armature through its humanoid mapping. The
animation is then rebuilt for the armature that prepare_armature() produces (identity
bone rotations, centimetres), so it plays on SKEL_evrar_full like SK_StandPose_Anim.

Run headless:
  blender <stem>_parts.blend --background --python export_vrma_fbx.py -- <input.vrma> <output.fbx>

The .blend file is opened but never saved.
"""
import os
import sys

import bpy

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from vroid_fbx_common import bake_deform_animation, export_animation_fbx  # noqa: E402

vrma_path, out_path = sys.argv[sys.argv.index("--") + 1:][:2]
os.makedirs(os.path.dirname(out_path), exist_ok=True)

scene = bpy.context.scene
armature = next(o for o in scene.objects if o.type == "ARMATURE")
bpy.context.view_layer.objects.active = armature
armature.select_set(True)
bpy.ops.import_scene.vrma(filepath=vrma_path)
first, last = (int(round(f)) for f in armature.animation_data.action.frame_range)

# Per frame, the deformation each bone applies to the mesh (pose @ rest^-1).
rest_inv = {b.name: b.matrix_local.inverted() for b in armature.data.bones}
deform = []
for frame in range(first, last + 1):
    scene.frame_set(frame)
    deform.append({n: armature.pose.bones[n].matrix @ m for n, m in rest_inv.items()})

armature = bake_deform_animation(deform, first)
export_animation_fbx(armature, "BodyOnly", out_path)
print("VRMA frames", first, last, "fps", scene.render.fps, "wrote:", out_path, os.path.getsize(out_path))
