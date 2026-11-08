"""Inventory of VRoid preset exports: unique garments by geometry, variants by texture.

For every file, every material of a garment category is described by
  category, geometry hash (POSITION bytes of the primitives using it), texture hash.
Garments with the same geometry in the same category are one mesh; their different
textures are variants. Materials that appear in the reference export (the base outfit
every export carries unless replaced) are still listed, the first file that has them wins.

Usage: python vrm_inventory.py <presets_dir> <out.json>
"""
import glob
import hashlib
import json
import os
import re
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vrm_signatures import load, image_bytes  # noqa: E402

CATS = ("Tops", "Bottoms", "Onepiece", "Shoes", "Accessory", "_HAIR", "HairBack")


def material_category(name):
    if "HairBack" in name:
        return "Hair"
    if "_HAIR" in name:
        return "Hair"
    for c in ("Tops", "Bottoms", "Onepiece", "Shoes", "Accessory"):
        if c in name:
            return c
    return None


def describe(path):
    doc, data, bin_off = load(path)
    prims = {}
    for mi, mesh in enumerate(doc["meshes"]):
        for pi, p in enumerate(mesh["primitives"]):
            prims.setdefault(p.get("material"), []).append((mesh.get("name", ""), p))
    out = []
    for i, m in enumerate(doc.get("materials", [])):
        cat = material_category(m.get("name", ""))
        if cat is None or i not in prims:
            continue
        h = hashlib.md5()
        nv = 0
        meshes = set()
        for mesh_name, p in prims[i]:
            acc = doc["accessors"][p["attributes"]["POSITION"]]
            bv = doc["bufferViews"][acc["bufferView"]]
            s = bin_off + bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
            h.update(data[s:s + acc["count"] * 12])
            nv += acc["count"]
            meshes.add(mesh_name)
        tex = m.get("pbrMetallicRoughness", {}).get("baseColorTexture", {}).get("index")
        th = hashlib.md5(image_bytes(doc, data, bin_off, tex)).hexdigest()[:8] if tex is not None else "none"
        out.append({"material": m["name"], "category": cat, "geo": h.hexdigest()[:10],
                    "verts": nv, "tex": th, "meshes": sorted(meshes)})
    return out


def main(src, out_path):
    files = sorted(glob.glob(os.path.join(src, "*.vrm")),
                   key=lambda f: (os.path.basename(f)[0], os.path.basename(f)))
    garments = OrderedDict()  # (category, geo) -> {variants: {tex: first file}}
    per_file = {}
    for f in files:
        name = os.path.basename(f)
        if not re.match(r"^(p|d|h)\d{3}\.vrm$|^acc_all\.vrm$", name):
            continue
        desc = describe(f)
        per_file[name] = desc
        for d in desc:
            key = f'{d["category"]}|{d["geo"]}'
            g = garments.setdefault(key, {"category": d["category"], "geo": d["geo"], "verts": d["verts"],
                                         "variants": OrderedDict()})
            g["variants"].setdefault(d["tex"], {"file": name, "material": d["material"]})
    counts = {}
    for g in garments.values():
        c = counts.setdefault(g["category"], [0, 0])
        c[0] += 1
        c[1] += len(g["variants"])
    print("category: meshes / variants")
    for c, (m, v) in sorted(counts.items()):
        print(f"  {c}: {m} / {v}")
    json.dump({"garments": list(garments.values()), "files": per_file}, open(out_path, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
