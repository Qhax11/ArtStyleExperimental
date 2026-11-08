"""Combine materials.json, coverage.json and the icons into the Unreal import manifest.

Adds per item: Unreal slot, display name, hidden body regions, blocked slots, icon path,
and a swatch colour per variant (the most common opaque colour of its largest texture).

Usage: python make_manifest.py <built_dir>
Writes <built_dir>/manifest.json.
"""
import json
import os
import sys
from collections import Counter

from PIL import Image

SLOTS = {"Top": "Top", "Bottom": "Bottom", "Dress": "Dress", "Shoes": "Shoes", "Neck": "Necklace",
         "Arm": "Gloves", "Hair": "Hair", "Glasses": "Glasses", "Hat": "Hat"}
NAMES = {"Top": "Üst", "Bottom": "Alt", "Dress": "Elbise", "Shoes": "Ayakkabı", "Neck": "Yaka süsü",
         "Arm": "Kol süsü", "Hair": "Saç"}
SPECIAL = {"Glasses_Thick": "Kalın gözlük", "Hat_Silk": "Silindir şapka", "Hat_Straw": "Hasır şapka",
           "Hat_Witch": "Cadı şapkası", "Hat_Work": "Kep"}
BLOCKS = {"Dress": ["Top", "Bottom"]}
# Regions each slot may hide. A top never hides the legs, shoes never hide the thighs, and so on,
# so a long coat cannot make the legs vanish under a separate bottom.
ALLOWED = {
    "Top": {"Chest", "Belly", "UpperArm", "LowerArm"},
    "Bottom": {"Hips", "Thigh", "Calf"},
    "Dress": {"Chest", "Belly", "Hips", "UpperArm", "LowerArm", "Thigh"},
    "Shoes": {"Foot", "Ankle", "Calf"},
    "Neck": set(), "Arm": {"LowerArm", "Hand"},
}

# Rays from the crotch and the soles mostly miss the garment even when it covers them.
THRESHOLD = {"Hips": 0.75, "Foot": 0.7}


def swatch(path):
    im = Image.open(path).convert("RGBA")
    im.thumbnail((128, 128))
    px = [p for p in im.getdata() if p[3] > 200]
    if not px:
        return [1, 1, 1, 1]
    q = Counter((r // 24, g // 24, b // 24) for r, g, b, _ in px)
    key = q.most_common(1)[0][0]
    sel = [p for p in px if (p[0] // 24, p[1] // 24, p[2] // 24) == key]
    avg = [sum(p[i] for p in sel) / len(sel) / 255 for i in range(3)]
    # sRGB to linear for FLinearColor.
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in avg]
    return [round(c, 4) for c in lin] + [1]


def main(built):
    mats = json.load(open(os.path.join(built, "materials.json")))
    cover = json.load(open(os.path.join(built, "coverage.json"))) if os.path.exists(
        os.path.join(built, "coverage.json")) else {}
    counters = {}
    out = []
    for it in mats:
        slot = it["slot"]
        counters[slot] = counters.get(slot, 0) + 1
        name = SPECIAL.get(it["name"]) or f"{NAMES.get(slot, slot)} {counters[slot]}"
        shares = cover.get(it["name"], {}).get("shares", {})
        hidden = [r for r, share in shares.items()
                  if r in ALLOWED.get(slot, set()) and share >= THRESHOLD.get(r, 0.96)]
        variants = []
        for v in it["variants"]:
            biggest = v[-1]["tex"]  # slots are sorted by index count, the last is the largest
            variants.append({"swatch": swatch(os.path.join(built, "tex", f"T_P_{biggest}.png")), "slots": v})
        out.append({"name": it["name"], "slot": SLOTS[slot], "kind": it["kind"], "display": name,
                    "hidden": hidden, "blocked": BLOCKS.get(slot, []), "variants": variants,
                    "icon": os.path.join(built, "icons", f"T_Icon_{it['name']}.png")})
    json.dump(out, open(os.path.join(built, "manifest.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(len(out), "items,", sum(len(o["variants"]) for o in out), "looks")


if __name__ == "__main__":
    main(sys.argv[1])
