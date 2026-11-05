"""Save a VRM's body texture with its alpha cut-outs removed.

VRoid hides the body under clothes by cutting alpha in the body texture; the colour
data stays intact. Removing the cut-outs brings the base layer back.

Run headless:
  blender --background --python make_body_texture_opaque.py -- <input.vrm> <output.png>
"""
import sys

import bpy
import numpy as np

vrm_path, out_path = sys.argv[sys.argv.index("--") + 1:][:2]
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj)
bpy.ops.import_scene.vrm(filepath=vrm_path)

mat = next(m for m in bpy.data.materials
           if "_Body_00_SKIN" in m.name and not m.name.startswith("MToon Outline"))
source = mat.vrm_addon_extension.mtoon1.pbr_metallic_roughness.base_color_texture.index.source
w, h = source.size
px = np.array(source.pixels[:], dtype=np.float32).reshape(h, w, 4)
px[..., 3] = 1.0

result = bpy.data.images.new("T_Body_Opaque", w, h, alpha=True)
result.colorspace_settings.name = "sRGB"
result.pixels.foreach_set(px.ravel())
result.filepath_raw = out_path
result.file_format = "PNG"
result.save()
print("OPAQUE saved:", out_path, w, h)
