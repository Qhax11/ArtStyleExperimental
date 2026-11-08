"""Turn items.json (classify_presets.py) plus the hair and accessory exports into build jobs.

Usage: python make_jobs.py <presets_dir> <items.json> <jobs.json>
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vrm_signatures import load  # noqa: E402

ACCESSORIES = {
    "Glasses_Thick": ["GlassesHiFrame", "GlassesHiLens"],
    "Hat_Silk": ["SilkHat"],
    "Hat_Straw": ["StrawHat"],
    "Hat_Witch": ["WitchHat"],
    "Hat_Work": ["WorkCap"],
}


def main(src, items_path, out_path):
    jobs = {}

    def add(file, item):
        jobs.setdefault(file, []).append(item)

    for it in json.load(open(items_path)):
        add(it["mesh"]["file"], {"name": it["id"], "kind": "cloth", "materials": it["mesh"]["materials"]})
    for f in sorted(os.listdir(src)):
        m = re.match(r"^h(\d{3})\.vrm$", f)
        if m:
            doc, _, _ = load(os.path.join(src, f))
            mats = [x["name"] for x in doc["materials"] if "_HAIR" in x["name"]]
            add(f, {"name": f"Hair_V{int(m.group(1)):02d}", "kind": "hair", "materials": mats})
    doc, _, _ = load(os.path.join(src, "acc_all.vrm"))
    names = [x["name"] for x in doc["materials"]]
    for item, frags in ACCESSORIES.items():
        mats = [n for n in names if any(fr in n for fr in frags)]
        add("acc_all.vrm", {"name": item, "kind": "rigid", "materials": mats})
    out = [{"vrm": os.path.abspath(os.path.join(src, f)), "items": items} for f, items in sorted(jobs.items())]
    json.dump(out, open(out_path, "w"), indent=1)
    print(len(out), "files,", sum(len(j["items"]) for j in out), "items")


if __name__ == "__main__":
    main(*sys.argv[1:4])
