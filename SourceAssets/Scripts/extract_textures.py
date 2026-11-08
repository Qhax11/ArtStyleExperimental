"""Write the textures every built item needs, and the material data for Unreal.

Textures are saved once per content hash as <out>/tex/T_P_<hash>.png, at most 1024 px.
<out>/materials.json lists, per item, its slots and variants:
  {"name": "Top_005", "slot": "Top", "kind": "cloth",
   "variants": [[{"tex": hash, "normal": hash|null, "shade": [r, g, b], "cutoff": 0.5}, ...], ...]}
Variant 0 is the mesh's own look.

Usage: python extract_textures.py <presets_dir> <items.json> <jobs.json> <out_dir>
"""
import hashlib
import io
import json
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vrm_signatures import load, image_bytes  # noqa: E402

MAX = 1024
_docs = {}


def doc_of(path):
    if path not in _docs:
        _docs.clear()
        _docs[path] = load(path)
    return _docs[path]


def save_tex(doc, data, bin_off, tex_index, out_dir):
    raw = image_bytes(doc, data, bin_off, tex_index)
    h = hashlib.md5(raw).hexdigest()[:10]
    path = os.path.join(out_dir, "tex", f"T_P_{h}.png")
    if not os.path.exists(path):
        im = Image.open(io.BytesIO(raw))
        if max(im.size) > MAX:
            f = MAX / max(im.size)
            im = im.resize((max(1, int(im.size[0] * f)), max(1, int(im.size[1] * f))), Image.LANCZOS)
        im.save(path)
    return h


def material_info(path, name, out_dir):
    doc, data, bin_off = doc_of(path)
    m = next(x for x in doc["materials"] if x["name"] == name)
    tex = m["pbrMetallicRoughness"]["baseColorTexture"]["index"]
    info = {"tex": save_tex(doc, data, bin_off, tex, out_dir), "normal": None,
            "cutoff": m.get("alphaCutoff", 0.5), "alpha": m.get("alphaMode", "OPAQUE"),
            "shade": [1.0, 1.0, 1.0]}
    mt = m.get("extensions", {}).get("VRMC_materials_mtoon", {})
    if "shadeColorFactor" in mt:
        info["shade"] = mt["shadeColorFactor"]
    nt = m.get("normalTexture", {}).get("index")
    if nt is not None:
        img = doc["images"][doc["textures"][nt]["source"]]
        if "NoneNormal" not in img.get("name", ""):
            info["normal"] = save_tex(doc, data, bin_off, nt, out_dir)
    return info


def main(src, items_path, jobs_path, out_dir):
    os.makedirs(os.path.join(out_dir, "tex"), exist_ok=True)
    out = []
    for it in json.load(open(items_path)):
        variants = []
        for v in it["variants"]:
            path = os.path.join(src, v["file"])
            variants.append([material_info(path, n, out_dir) for n in v["materials"]])
        out.append({"name": it["id"], "slot": it["slot"], "kind": "cloth", "variants": variants})
    for job in json.load(open(jobs_path)):
        for item in job["items"]:
            if item["kind"] == "cloth":
                continue
            slot = "Hair" if item["kind"] == "hair" else item["name"].split("_")[0]
            out.append({"name": item["name"], "slot": slot, "kind": item["kind"],
                        "variants": [[material_info(job["vrm"], n, out_dir) for n in item["materials"]]]})
    json.dump(out, open(os.path.join(out_dir, "materials.json"), "w"), indent=1)
    print(len(out), "items,", len(os.listdir(os.path.join(out_dir, "tex"))), "textures")


if __name__ == "__main__":
    main(*sys.argv[1:5])
