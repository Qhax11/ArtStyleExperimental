"""Display names of the VRoid items, chosen by eye from their icons.

Items with colour variants have no colour in their name. Run it to check the list against the
item assets (every item named, no name used twice, numbers in wardrobe order) and write
Saved/DressUpImport/catalog_names.json, which the Unreal side reads to set UDressUpItem.DisplayName.
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# Items made before the VRoid batch.
EARLIER = {"Top_Tshirt": "Beyaz tişört", "Top_HoodieG": "Mavi kapüşonlu", "Bottom_Shorts": "Siyah şort",
           "Bottom_ShortsG": "Desenli şort", "Dress_BlackO": "Siyah elbise", "Socks_O": "Beyaz çorap",
           "Shoes_Sneakers": "Spor ayakkabı", "Shoes_MaryJaneO": "Siyah bağcıklı", "Hair_Default": "Kısa saç",
           "Hair_Long": "Uzun saç", "Glasses_Thin": "İnce çerçeveli gözlük", "Hat_Cap": "Kep"}

TOP = {
    1: "Beyaz uzun kollu bluz", 2: "Beyaz kolsuz bluz", 3: "Donut desenli kapüşonlu", 4: "Beyaz yelekli frak",
    5: "Siyah uzun ceket", 6: "Kırmızı-siyah kostüm ceketi", 7: "Mavi kollu korse", 8: "Siyah kısa ceket",
    9: "Pastel renkli ceket", 10: "Pastel kısa ceket", 11: "Gri kemerler", 12: "Teknolojik yelek",
    13: "Teknolojik kısa üst", 14: "Kırmızı Çin ceketi", 15: "Bambu desenli Çin bluzu", 16: "Pembe işlemeli bluz",
    17: "Vampir pelerinli ceket", 18: "Siyah smokin", 19: "Beyaz fırfırlı askılı", 20: "Beyaz fırfırlı bluz",
    21: "Mor kruvaze ceket", 22: "Mor kravatlı beyaz gömlek", 23: "Mor kravatlı kısa gömlek",
    24: "Mor kravatlı dar gömlek", 25: "Gri hırka", 26: "Krem blazer ve gri yelek", 27: "Gri kravatlı krem blazer",
    28: "Açık önlü krem blazer", 29: "Kısa krem blazer", 30: "Fiyonklu beyaz gömlek", 31: "Fiyonklu kısa gömlek",
    32: "Fiyonklu dar gömlek", 33: "Fiyonklu düğmeli gömlek", 34: "Kurdeleli krem blazer", 35: "Kurdeleli uzun blazer",
    36: "Kurdeleli açık blazer", 37: "Kurdeleli kısa blazer", 38: "Eşofman üstü", 39: "Kırmızı eşofman üstü",
    40: "Düğmeli okul ceketi", 41: "Kısa okul ceketi", 42: "Denizci üstü", 43: "Kısa denizci üstü",
    44: "Uzun kollu süveter yelek", 45: "Kısa kollu süveter yelek", 46: "Bej trençkot", 47: "Beyaz örgü kazak",
    48: "Kısa beyaz örgü kazak", 49: "Lacivert balıkçı yaka kolsuz", 50: "Omzu açık kısa bluz",
    51: "Çiçekli Hawaii gömleği", 52: "Lacivert blazer", 53: "Uzun kollu gömlek", 54: "Kısa kollu beyaz gömlek",
    55: "Kapüşonlu", 56: "Tişört",
}
BOTTOM = {
    1: "Gri bol pantolon", 2: "Beyaz kısa şort", 3: "Mavi detaylı şort", 4: "Beyaz dar pantolon",
    5: "Ekose paçalı balon şort", 6: "Siyah mini şort", 7: "Kemerli siyah pantolon", 8: "Kemerli gri kargo şort",
    9: "Fırfırlı fantezi etek", 10: "Altın işlemeli etekli şort", 11: "Teknolojik dar pantolon",
    12: "Krem paçalı teknolojik pantolon", 13: "Mavi teknolojik etek", 14: "Tek bacağı mavi teknolojik pantolon",
    15: "Kırmızı paçalı siyah kapri", 16: "Bambu desenli mini etek", 17: "Pembe işlemeli etek",
    18: "İşlemeli siyah kapri", 19: "Düğmeli siyah şort", 20: "Gri kumaş pantolon", 21: "Düğmeli siyah etek",
    22: "Fırfırlı siyah mini etek", 23: "Mor bermuda", 24: "Ekose pantolon", 25: "Pileli etek",
    26: "Çizgili spor şort", 27: "Kısa siyah spor tayt", 28: "Çizgili kapri tayt", 29: "Çizgili spor tayt",
    30: "Lacivert denizci şortu", 31: "Haki pantolon", 32: "Bej ekose pantolon", 33: "Kemerli uzun pileli etek",
    34: "Yırtık kot şort", 35: "Dar kumaş pantolon", 36: "Duble paça siyah şort", 37: "Siyah bermuda",
}
DRESS = {
    1: "Beyaz sade elbise", 2: "Çikolatalı tatlı elbise", 3: "Pembe tatlı elbise", 4: "Mavi hizmetçi elbisesi",
    5: "Kırmızı puantiyeli gece elbisesi", 6: "Lacivert straplez gece elbisesi", 7: "Sarı dantelli gece elbisesi",
    8: "Pembe parti elbisesi", 9: "Siyah teknolojik tulum", 10: "Siyah zırhlı kostüm", 11: "Yeşil peri elbisesi",
    12: "Beyaz fantezi elbise", 13: "Mor fantezi elbise", 14: "Kırmızı Çin elbisesi", 15: "Siyah gotik elbise",
    16: "Siyah yakalı elbise", 17: "Gri kimono", 18: "Lacivert çiçekli kimono", 19: "Krem çiçekli kimono",
    20: "Okul üniforması elbise", 21: "Beyaz kolsuz elbise", 22: "Krem kolsuz elbise", 23: "Lacivert kolsuz elbise",
    24: "Kot gömlekli beyaz elbise", 25: "Açık mavi gömlekli krem elbise", 26: "Beyaz gömlekli lacivert elbise",
    27: "Uzun kollu uzun elbise", 28: "Önlüklü uzun elbise", 29: "Önlüklü kısa elbise",
}
SHOES = {
    1: "Beyaz bilek botu", 2: "Beyaz cırtlı spor ayakkabı", 3: "Beyaz uzun çizme", 4: "Kalın tabanlı spor ayakkabı",
    5: "Kahverengi bağcıklı çizme", 6: "Pembe tombul spor ayakkabı", 7: "Siyah-beyaz bağcıklı ayakkabı",
    8: "Siyah-beyaz tokalı ayakkabı", 9: "Mavi bantlı ayakkabı", 10: "Siyah bağcıklı bot", 11: "Kırmızı topuklu",
    12: "Lacivert bantlı topuklu", 13: "Altın topuklu ve bacak ısıtıcı", 14: "Pembe topuklu ve bacak ısıtıcı",
    15: "Siyah kayışlı bot", 16: "Gri teknolojik bot", 17: "Siyah teknolojik bot", 18: "Altın tokalı siyah ayakkabı",
    19: "Siyah işlemeli çizme", 20: "Kahverengi topuklu bot", 21: "Lacivert kıvrık bot", 22: "Kahverengi kısa bot",
    23: "Yeşil sarmaşıklı sandalet", 24: "Kalın tabanlı bilek botu", 25: "Siyah-kırmızı ayakkabı",
    26: "Kurdeleli siyah-beyaz ayakkabı", 27: "Pembe bantlı topuklu", 28: "Gri detaylı siyah ayakkabı",
    29: "Kırmızı işlemeli ayakkabı", 30: "Siyah tokalı çizme", 31: "Siyah kurdeleli bot", 32: "Siyah tokalı ayakkabı",
    33: "Siyah kurdeleli ayakkabı", 34: "Bacağa bağlı siyah ayakkabı", 35: "Bej platform sandalet",
    36: "Mor çiçekli takunya", 37: "Loafer", 38: "Lacivert bağcıklı bot", 39: "Siyah babet", 40: "Tokalı terlik",
    41: "Platform sandalet", 42: "Beyaz sandalet", 43: "Siyah sandalet", 44: "Beyaz kapalı sandalet",
    45: "Yüksek bilekli kanvas", 46: "Yüksek bilekli basket ayakkabısı",
}
HAIR = {
    1: "Yuvarlak kısa saç", 2: "Uzun katlı saç", 3: "Yan örgülü küt saç", 4: "Kısa katlı saç", 5: "Tepesi tutamlı kısa saç",
    6: "Kedi kulaklı saç", 7: "Perçemsiz küt saç", 8: "Dağınık kısa saç", 9: "Dalgalı kısa saç", 10: "Uzun çift kuyruk",
    11: "Anten perçemli kısa saç", 12: "Uzun düz saç", 13: "Yuvarlak katlı saç", 14: "Alçak at kuyruğu",
    15: "Orta boy küt saç", 16: "Kısa çift örgü", 17: "Omuz boyu düz saç", 18: "Kabarık dağınık saç", 19: "Düz küt saç",
    20: "Dalgalı orta boy saç", 21: "Kısa düz saç", 22: "Çok uzun katlı saç", 23: "Halka perçemli kısa saç",
    24: "Yan perçemli kısa saç", 25: "Topuzlu örgülü saç", 26: "Anten perçemli uzun saç", 27: "Yan tutamlı kısa saç",
    28: "Çift topuz", 29: "Küt çift topuz", 30: "Dalgalı çift kuyruk", 31: "Düz çift kuyruk", 32: "Perçemli kısa saç",
    33: "At kuyruğu", 34: "Dalgalı at kuyruğu", 35: "Uzun çift örgü", 36: "Yana ayrık kısa saç", 37: "Perçemli uzun saç",
}
NECK = {
    1: "Altın mücevherli kolye", 2: "Yakalı gri kravat", 3: "İnci kolye", 4: "Siyah kayışlı yaka", 5: "Siyah fiyonk",
    6: "Kravat", 7: "Kurdele", 8: "Teknolojik göğüslük", 9: "Pembe kravatlı göğüslük", 10: "Ekose fiyonk",
    11: "Geniş desenli kravat",
}
ARM = {
    1: "Beyaz kol bandı", 2: "Kahverengi bileklik", 3: "Çiçekli kol süsü", 4: "Küçük kol süsü", 5: "Mavi bilezik",
    6: "Deri bileklik", 7: "Siyah eldiven", 8: "Siyah bileklik", 9: "Altın kol süsü", 10: "Siyah kol bandı",
    11: "Beyaz manşet", 12: "Kol bandı", 13: "Siyah kalın eldiven", 14: "Beyaz fırfırlı manşet",
}
OTHER = {"Glasses_Thick": "Kalın çerçeveli gözlük", "Hat_Silk": "Silindir şapka", "Hat_Straw": "Geniş kenarlı şapka",
         "Hat_Witch": "Cadı şapkası", "Hat_Work": "Asker kepi"}


# Versions of one design share a name, numbered in wardrobe order: "X", "X 2", "X 3".
# These override the tables above, and may rename earlier items too.
SIMILAR = {
    "Donut desenli kapüşonlu": "Top_HoodieG Top_003",
    "Süveter yelek": "Top_044 Top_045",
    "Beyaz örgü kazak": "Top_047 Top_048",
    "Mor kravatlı beyaz gömlek": "Top_022 Top_023 Top_024",
    "Fiyonklu beyaz gömlek": "Top_030 Top_031 Top_032 Top_033",
    "Gri kravatlı krem blazer": "Top_027 Top_028 Top_029",
    "Kurdeleli krem blazer": "Top_034 Top_035 Top_036 Top_037",
    "Denizci üstü": "Top_042 Top_043",
    "Okul ceketi": "Top_040 Top_041",
    "Eşofman üstü": "Top_038 Top_039",
    "Pastel renkli ceket": "Top_009 Top_010",
    "Siyah şort": "Bottom_Shorts Bottom_036",
    "Siyah bermuda": "Bottom_019 Bottom_037",
    "Çizgili spor tayt": "Bottom_026 Bottom_027 Bottom_028 Bottom_029",
    "Ekose pantolon": "Bottom_024 Bottom_032",
    "Teknolojik pantolon": "Bottom_011 Bottom_012 Bottom_014",
    "Pileli etek": "Bottom_025 Bottom_033",
    "Önlüklü elbise": "Dress_028 Dress_029",
    "Siyah teknolojik kostüm": "Dress_009 Dress_010",
    "Siyah-beyaz ayakkabı": "Shoes_007 Shoes_008",
    "Topuklu ve bacak ısıtıcı": "Shoes_013 Shoes_014",
    "Siyah bağcıklı": "Shoes_MaryJaneO Shoes_034",
    "Beyaz sandalet": "Shoes_042 Shoes_044",
    "Kahverengi bot": "Shoes_022 Shoes_020",
    "Teknolojik bot": "Shoes_016 Shoes_017",
    "Yuvarlak kısa saç": "Hair_V01 Hair_V21",
    "Küt saç": "Hair_V19 Hair_V07 Hair_V15",
    "Dağınık kısa saç": "Hair_V08 Hair_V18",
    "Dalgalı kısa saç": "Hair_V09 Hair_V20 Hair_Default",
    "Anten perçemli kısa saç": "Hair_V23 Hair_V11",
    "Çift topuz": "Hair_V28 Hair_V29",
    "At kuyruğu": "Hair_V33 Hair_V34",
    "Uzun katlı saç": "Hair_V02 Hair_V22",
    "Uzun düz saç": "Hair_V12 Hair_V37 Hair_Long",
    "Çift kuyruk": "Hair_V10 Hair_V31 Hair_V30",
    "Çift örgü": "Hair_V16 Hair_V35",
    "Kravat": "Neck_006 Neck_011",
    "Teknolojik göğüslük": "Neck_008 Neck_009",
    "Siyah eldiven": "Arm_007 Arm_013",
    "Kol bandı": "Arm_010 Arm_012",
    "Beyaz manşet": "Arm_014 Arm_011",
}


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from catalog_order import ORDER
    wardrobe = [name for group in ORDER.values() for name in group]

    names = dict(OTHER)
    for prefix, table in (("Top", TOP), ("Bottom", BOTTOM), ("Dress", DRESS), ("Shoes", SHOES), ("Neck", NECK), ("Arm", ARM)):
        names.update({f"{prefix}_{n:03d}": text for n, text in table.items()})
    names.update({f"Hair_V{n:02d}": text for n, text in HAIR.items()})

    data = os.path.join(ROOT, "Content", "DressUp", "Data")
    items = {f[3:-7] for f in os.listdir(os.path.join(data, "VRoid")) if f.startswith("DA_") and f.endswith(".uasset")}
    missing = sorted(items - set(names))
    unknown = sorted(set(names) - items)

    earlier = dict(EARLIER)
    out_of_order = []
    for base, members in SIMILAR.items():
        members = members.split()
        positions = [wardrobe.index(m) for m in members]
        if positions != sorted(positions):
            out_of_order.append(base)
        for i, member in enumerate(members):
            text = base if i == 0 else f"{base} {i + 1}"
            if member in names:
                names[member] = text
            elif member in earlier:
                earlier[member] = text
            else:
                unknown.append(member)
    every = list(names.values()) + list(earlier.values())
    repeated = sorted({n for n in every if every.count(n) > 1})
    if missing or unknown or repeated or out_of_order:
        raise SystemExit(f"missing={missing} unknown={unknown} repeated={repeated} out_of_order={out_of_order}")

    paths = {f"/Game/DressUp/Data/VRoid/DA_{k}.DA_{k}": v for k, v in names.items()}
    paths.update({f"/Game/DressUp/Data/DA_{k}.DA_{k}": v for k, v in earlier.items()})
    out = os.path.join(ROOT, "Saved", "DressUpImport", "catalog_names.json")
    json.dump(paths, open(out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(len(paths), "names,", sum(len(m.split()) for m in SIMILAR.values()), "in numbered groups")


if __name__ == "__main__":
    main()
