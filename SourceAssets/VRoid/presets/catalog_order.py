"""Wardrobe order: similar items sit next to each other, grouped by kind, then look.

The order was chosen by eye from the item icons. Run it to validate the list against the item
assets on disk and write Saved/DressUpImport/catalog_order.json, which the Unreal side reads
to fill DA_Catalog.AllItems.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def nums(prefix, text):
    return [f"{prefix}_{n}" for n in text.split()]


ORDER = {
    "Top": [
        # Tees and casual shirts
        "Top_Tshirt", *nums("Top", "056 054 051"),
        # Hoodies
        "Top_HoodieG", *nums("Top", "003 055"),
        # Knits and sweater vests
        *nums("Top", "047 048 044 045"),
        # Sleeveless, frills, blouses
        *nums("Top", "002 049 019 020 050 016"),
        # Plain shirts, shirt and tie, shirt and bow
        *nums("Top", "001 053 022 023 024 030 031 032 033"),
        # Cardigan, blazers with tie, blazers with ribbon, dark jackets
        *nums("Top", "025 026 027 028 029 034 035 036 037 052 018"),
        # Sailor, school jackets, track jackets
        *nums("Top", "042 043 040 041 038 039"),
        # Coat and wrap
        *nums("Top", "046 021"),
        # Chinese style
        *nums("Top", "014 015"),
        # Formal fantasy
        *nums("Top", "004 006 017"),
        # Dark coat and crop
        *nums("Top", "005 008"),
        # Colourful fantasy
        *nums("Top", "007 009 010"),
        # Tech pieces
        *nums("Top", "012 013 011"),
    ],
    "Bottom": [
        # Short shorts
        "Bottom_Shorts", *nums("Bottom", "036 034 006 002"),
        # Patterned and cargo shorts
        "Bottom_ShortsG", *nums("Bottom", "003 005 008"),
        # Knee length
        *nums("Bottom", "019 037 015 018 023"),
        # Sporty
        *nums("Bottom", "026 027 028 030"),
        # Long trousers
        *nums("Bottom", "001 020 035 029 007 004 024 032 031"),
        # Tech trousers, tech and fantasy skirts
        *nums("Bottom", "011 012 014 013 010 009"),
        # Skirts
        *nums("Bottom", "017 016 025 033 021 022"),
    ],
    "Socks": ["Socks_O"],
    "Dress": [
        # Plain sleeveless, then with a shirt over
        *nums("Dress", "001 021 022 023 024 025 026"),
        # Long blue, maids, black frills, uniform
        *nums("Dress", "027 028 004 029"), "Dress_BlackO", *nums("Dress", "016 015 020"),
        # Party
        *nums("Dress", "008 005 006 007"),
        # Sweet
        *nums("Dress", "002 003"),
        # Fantasy
        *nums("Dress", "011 012 013 014"),
        # Kimono
        *nums("Dress", "017 018 019"),
        # Tech suits
        *nums("Dress", "009 010"),
    ],
    "Shoes": [
        # Sneakers and chunky trainers
        "Shoes_Sneakers", *nums("Shoes", "004 045 046 006 002 001 024"),
        # Loafers and flat lace-ups
        *nums("Shoes", "037 039 028 033 032 018 025 026 007 008"),
        # Heels and straps
        *nums("Shoes", "011 012 009 029 027"),
        # Leg warmers over heels, ribbons up the leg
        *nums("Shoes", "013 014"), "Shoes_MaryJaneO", *nums("Shoes", "034 023"),
        # Sandals
        *nums("Shoes", "042 044 043 041 040 035 036"),
        # Ankle boots
        *nums("Shoes", "022 020 021 038 010 015 031"),
        # Tech boots, tall boots
        *nums("Shoes", "016 017 030 019 005 003"),
    ],
    "Hair": [
        # Smooth short and bob
        *nums("Hair", "V01 V21 V04 V24 V13 V19 V07 V15 V36 V03"),
        # Short with tufts, messy and layered
        *nums("Hair", "V05 V23 V11 V32 V08 V18 V09 V20"), "Hair_Default",
        # Ears and buns
        *nums("Hair", "V06 V28 V29 V25"),
        # Side locks and ponytails
        *nums("Hair", "V27 V14 V33 V34"),
        # Long straight
        *nums("Hair", "V17 V02 V12 V37"), "Hair_Long", *nums("Hair", "V22 V26"),
        # Twin tails and braids
        *nums("Hair", "V10 V31 V30 V16 V35"),
    ],
    "Accessory": [
        "Glasses_Thin", "Glasses_Thick",
        "Hat_Cap", "Hat_Work", "Hat_Straw", "Hat_Silk", "Hat_Witch",
        # Ties, ribbons and bows, necklaces, chest harnesses
        *nums("Neck", "006 011 002 004 007 005 010 003 001 008 009"),
        # Gloves, bands, cuffs, small pieces
        *nums("Arm", "007 013 010 012 002 008 006 014 011 005 001 009 003 004"),
    ],
}


def main():
    data = os.path.join(ROOT, "Content", "DressUp", "Data")
    paths = {}
    for folder, base in ((data, "/Game/DressUp/Data"), (os.path.join(data, "VRoid"), "/Game/DressUp/Data/VRoid")):
        for f in os.listdir(folder):
            if f.startswith("DA_") and f.endswith(".uasset") and f[:-7] not in ("DA_Catalog", "DA_Body_evrar"):
                paths[f[3:-7]] = f"{base}/{f[:-7]}.{f[:-7]}"
    order = [name for group in ORDER.values() for name in group]
    missing = sorted(set(paths) - set(order))
    unknown = sorted(set(order) - set(paths))
    repeated = sorted({n for n in order if order.count(n) > 1})
    if missing or unknown or repeated:
        raise SystemExit(f"missing={missing}\nunknown={unknown}\nrepeated={repeated}")
    out = os.path.join(ROOT, "Saved", "DressUpImport", "catalog_order.json")
    json.dump([paths[n] for n in order], open(out, "w"), separators=(",", ":"))
    print(len(order), "items:", {k: len(v) for k, v in ORDER.items()})


if __name__ == "__main__":
    main()
