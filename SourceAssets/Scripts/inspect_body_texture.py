"""Report on a VRM body texture's alpha and save its alpha mask as a grayscale PNG.

Run headless:
  blender --background --python inspect_body_texture.py -- <input.vrm> <alpha_mask.png>
"""
import sys

import bpy
import numpy as np

vrm_path, mask_path = sys.argv[sys.argv.index("--") + 1:][:2]
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj)
bpy.ops.import_scene.vrm(filepath=vrm_path)

mat = next(m for m in bpy.data.materials
           if "_Body_00_SKIN" in m.name and not m.name.startswith("MToon Outline"))
mtoon = mat.vrm_addon_extension.mtoon1
image = mtoon.pbr_metallic_roughness.base_color_texture.index.source
print("TEX material:", mat.name, "alpha_mode:", mtoon.alpha_mode, "cutoff:", mtoon.alpha_cutoff)
print("TEX image:", image.name, image.size[0], image.size[1])

w, h = image.size
px = np.array(image.pixels[:], dtype=np.float32).reshape(h, w, 4)
alpha = px[..., 3]
print(f"TEX alpha: min={alpha.min():.3f} max={alpha.max():.3f} "
      f"transparent(<0.5)={(alpha < 0.5).mean() * 100:.1f}% opaque(>=0.5)={(alpha >= 0.5).mean() * 100:.1f}%")

hidden = alpha < 0.5
if hidden.any():
    rgb = px[..., :3][hidden]
    luma = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    print(f"TEX hidden rgb: mean={rgb.mean(axis=0).round(3).tolist()} "
          f"dark(<0.1)={(luma < 0.1).mean() * 100:.1f}% "
          f"skin_like={((rgb[:, 0] > rgb[:, 2] + 0.05) & (luma > 0.2)).mean() * 100:.1f}%")

mask = bpy.data.images.new("alpha_mask", w, h, alpha=False)
out = np.ones((h, w, 4), dtype=np.float32)
out[..., 0] = out[..., 1] = out[..., 2] = alpha
mask.pixels.foreach_set(out.ravel())
mask.filepath_raw = mask_path
mask.file_format = "PNG"
mask.save()
print("TEX mask saved:", mask_path)
