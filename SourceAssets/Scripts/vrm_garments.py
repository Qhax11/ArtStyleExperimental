"""Per-material geometry of VRoid exports, for sorting garment materials into slots.

For every garment material: name tag, texture hash, index count and the bounding box of
the vertices its faces use (metres, VRM space: y up, x left/right, z forward).

Usage: python vrm_garments.py <file.vrm> [...]
"""
import hashlib
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vrm_signatures import load, image_bytes  # noqa: E402

COMP = {5121: ("B", 1), 5123: ("H", 2), 5125: ("I", 4)}


def accessor_array(doc, data, bin_off, index, comps):
    acc = doc["accessors"][index]
    bv = doc["bufferViews"][acc["bufferView"]]
    s = bin_off + bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    if comps == 1:
        fmt, size = COMP[acc["componentType"]]
        stride = bv.get("byteStride", size)
        return [struct.unpack_from("<" + fmt, data, s + i * stride)[0] for i in range(acc["count"])]
    stride = bv.get("byteStride", 12)
    return [struct.unpack_from("<3f", data, s + i * stride) for i in range(acc["count"])]


def tag(name):
    for t in ("HairBack", "_HAIR", "Tops", "Bottoms", "Onepiece", "Shoes", "Accessory", "Body", "FaceMouth", "EyeIris",
              "EyeHighlight", "Face", "EyeWhite", "Eyelash", "Eyeline", "Brow"):
        if t in name:
            return t.strip("_")
    return "?"


def garments(path):
    doc, data, bin_off = load(path)
    pos_cache = {}
    out = []
    for mesh in doc["meshes"]:
        for p in mesh["primitives"]:
            mi = p.get("material")
            if mi is None:
                continue
            m = doc["materials"][mi]
            t = tag(m["name"])
            if t not in ("Tops", "Bottoms", "Onepiece", "Shoes", "Accessory", "HAIR", "HairBack", "Body"):
                continue
            pi = p["attributes"]["POSITION"]
            if pi not in pos_cache:
                pos_cache[pi] = accessor_array(doc, data, bin_off, pi, 3)
            pos = pos_cache[pi]
            idx = accessor_array(doc, data, bin_off, p["indices"], 1)
            used = set(idx)
            xs = [pos[i][0] for i in used]
            ys = [pos[i][1] for i in used]
            zs = [pos[i][2] for i in used]
            tex = m.get("pbrMetallicRoughness", {}).get("baseColorTexture", {}).get("index")
            th = hashlib.md5(image_bytes(doc, data, bin_off, tex)).hexdigest()[:8] if tex is not None else "none"
            out.append({
                "material": m["name"], "tag": t, "tex": th, "mesh": mesh.get("name", ""),
                "indices": len(idx), "verts": len(used),
                "x": (min(xs), max(xs)), "y": (min(ys), max(ys)), "z": (min(zs), max(zs)),
                "alpha": m.get("alphaMode", "OPAQUE"),
            })
    return out


if __name__ == "__main__":
    for f in sys.argv[1:]:
        print(os.path.basename(f))
        for g in garments(f):
            print(f"  {g['tag']:9s} {g['tex']} idx={g['indices']:6d} x=[{g['x'][0]:+.2f},{g['x'][1]:+.2f}] "
                  f"y=[{g['y'][0]:.2f},{g['y'][1]:.2f}] z=[{g['z'][0]:+.2f},{g['z'][1]:+.2f}] {g['alpha']} {g['material']}")
