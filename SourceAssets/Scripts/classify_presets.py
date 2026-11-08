"""Sort the garment materials of every VRoid preset export into game items.

Every export carries one preset per list (tops, bottoms, neck, arm, shoes, ...), all in one
mesh, and VRoid's material names do not say which list a material came from. Materials are
sorted by where their vertices sit on the T-posed body, with the name tag as a hint:

  shoes   tag Shoes
  neck    tag Accessory not sharing its template number with a Tops material, or a small
          untagged piece around the neck
  arm     most vertices out on the arms
  bottom  nothing above the waist (leg-only pieces without a Bottoms tag become socks)
  top     the rest; in dress exports (d*.vrm) top and bottom pieces form the dress

Items are deduplicated by their texture set. Items of one slot whose materials have the
same index counts share a mesh: the first becomes the mesh, the others texture variants.

Usage: python classify_presets.py <presets_dir> <out.json>
"""
import hashlib
import json
import os
import re
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vrm_garments import accessor_array, tag  # noqa: E402
from vrm_signatures import load, image_bytes  # noqa: E402

WAIST = 1.04      # metres; bottoms end below this
ARM_X = 0.24      # |x| beyond this is on the arms in the T-pose


def materials(path):
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
            pi = p["attributes"]["POSITION"]
            if pi not in pos_cache:
                pos_cache[pi] = accessor_array(doc, data, bin_off, pi, 3)
            pos = pos_cache[pi]
            idx = accessor_array(doc, data, bin_off, p["indices"], 1)
            used = [pos[i] for i in set(idx)]
            n = len(used)
            tex = m.get("pbrMetallicRoughness", {}).get("baseColorTexture", {}).get("index")
            th = hashlib.md5(image_bytes(doc, data, bin_off, tex)).hexdigest()[:10] if tex is not None else "none"
            out.append({
                "material": m["name"], "tag": t, "tex": th, "indices": len(idx), "mesh": mesh.get("name", ""),
                "f_arm": sum(1 for v in used if abs(v[0]) > ARM_X) / n,
                "f_above_waist": sum(1 for v in used if v[1] > WAIST) / n,
                "ymax": max(v[1] for v in used), "ymin": min(v[1] for v in used),
                "xmax": max(abs(v[0]) for v in used),
                "neckish": all(abs(v[0]) < 0.16 and 1.0 < v[1] < 1.45 for v in used),
            })
    return out


def template(name):
    m = re.match(r"N00_(\d{3}_\d{2})_", name)
    return m.group(1) if m else None


# Last export round of each outfit list; later rounds keep that preset on.
FINAL_ROUND = {"Neck": 18, "Arm": 16, "Shoes": 59, "Bottom": 57}


def classify_file(name, mats, constants):
    dress_mode = name.startswith("d")
    rnd = 1000 if dress_mode else int(name[1:4])
    clear_top_templates = {template(m["material"]) for m in mats
                           if m["tag"] == "Tops" and m["f_above_waist"] > 0.5}
    slots = {}
    for m in mats:
        t = m["tag"]
        if t not in ("Tops", "Bottoms", "Onepiece", "Shoes", "Accessory"):
            continue
        if t == "Accessory" and not m["material"].startswith("N00"):
            continue  # VRoid accessory-tab items (hats, glasses): handled separately
        fixed = next((s for s, texs in constants.items() if m["tex"] in texs), None)
        if fixed:
            slot = fixed
        elif t == "Shoes":
            slot = "Shoes"
        elif t == "Accessory":
            slot = "Neck"
        elif m["f_arm"] > 0.6 and m["f_above_waist"] > 0.9 and not (t == "Tops" and m["f_arm"] < 0.9):
            slot = "Arm"
        elif t == "Bottoms" or m["f_above_waist"] < 0.05 or (
                m["f_above_waist"] < 0.3 and m["ymax"] < 1.12
                and template(m["material"]) not in clear_top_templates):
            slot = "Socks" if (m["ymax"] < 0.65 and t != "Bottoms") else "Bottom"
        elif m["neckish"] and t != "Tops":
            slot = "Neck"
        else:
            slot = "Top"
        if not fixed and rnd > FINAL_ROUND.get(slot, 10**6):
            slot = "Top"  # a list that ended keeps its preset; anything new belongs to the top
        if dress_mode and slot in ("Top", "Bottom", "Arm"):
            slot = "Dress"
        slots.setdefault(slot, []).append(m)
    if not dress_mode:
        for s, r in FINAL_ROUND.items():
            if rnd == r:
                constants[s] = {m["tex"] for m in slots.get(s, [])}
    return slots


def main(src, out_path):
    names = sorted((f for f in os.listdir(src) if re.match(r"^[pd]\d{3}\.vrm$", f)),
                   key=lambda f: (f[0] == "d", f))
    constants = {}
    items = OrderedDict()   # (slot, texture set) -> item
    report = []
    for name in names:
        mats = materials(os.path.join(src, name))
        slots = classify_file(name, mats, constants)
        report.append(f"{name}: " + " ".join(f"{s}={len(v)}" for s, v in sorted(slots.items())))
        for slot, ms in slots.items():
            key = (slot, tuple(sorted(m["tex"] for m in ms)))
            if key in items:
                continue
            # Slot order: by index count, so a variant's slot i matches the mesh's slot i.
            ms = sorted(ms, key=lambda m: (m["indices"], m["material"]))
            items[key] = {"slot": slot, "file": name,
                          "materials": [m["material"] for m in ms],
                          "textures": [m["tex"] for m in ms],
                          "shape": [m["indices"] for m in ms],
                          "tags": [m["tag"] for m in ms]}
    # Group into meshes with texture variants.
    meshes = OrderedDict()
    for it in items.values():
        key = (it["slot"], tuple(it["shape"]))
        meshes.setdefault(key, []).append(it)
    out = []
    counters = {}
    for (slot, shape), group in meshes.items():
        counters[slot] = counters.get(slot, 0) + 1
        out.append({"id": f"{slot}_{counters[slot]:03d}", "slot": slot, "mesh": group[0],
                    "variants": group})
    summary = {}
    for o in out:
        s = summary.setdefault(o["slot"], [0, 0])
        s[0] += 1
        s[1] += len(o["variants"])
    print("\n".join(report))
    print("slot: meshes / items with variants")
    for s, (a, b) in sorted(summary.items()):
        print(f"  {s}: {a} / {b}")
    json.dump(out, open(out_path, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
