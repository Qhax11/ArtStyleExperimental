"""Per-category texture signatures of VRoid VRM exports (no Blender).

For every material it hashes the base colour image bytes. Prints, per file, a short hash per
category (Tops, Bottoms, Shoes, Accessory, Onepiece, Body), so repeated presets show up.
"""
import hashlib, json, re, struct, sys
from collections import defaultdict

def load(path):
    with open(path, 'rb') as f:
        data = f.read()
    clen = struct.unpack('<I', data[12:16])[0]
    doc = json.loads(data[20:20 + clen])
    bin_off = 20 + clen + 8
    return doc, data, bin_off

def image_bytes(doc, data, bin_off, tex_index):
    img = doc['images'][doc['textures'][tex_index]['source']]
    bv = doc['bufferViews'][img['bufferView']]
    s = bin_off + bv.get('byteOffset', 0)
    return data[s:s + bv['byteLength']]

def signatures(path):
    doc, data, bin_off = load(path)
    cats = defaultdict(list)
    for m in doc.get('materials', []):
        name = m.get('name', '')
        cat = next((c for c in ('Tops', 'Bottoms', 'Shoes', 'Onepiece', 'Accessory', 'Body_00_SKIN', '_HAIR') if c in name), None)
        if not cat:
            continue
        tex = m.get('pbrMetallicRoughness', {}).get('baseColorTexture', {}).get('index')
        h = hashlib.md5(image_bytes(doc, data, bin_off, tex)).hexdigest()[:6] if tex is not None else '------'
        cats[cat].append(h)
    return {k: '+'.join(sorted(v)) for k, v in cats.items()}

if __name__ == '__main__':
    prev = {}
    for p in sys.argv[1:]:
        s = signatures(p)
        same = [k for k in s if prev.get(k) == s[k]]
        print(p.split('/')[-1], ' '.join(f'{k[:4]}={v}' for k, v in sorted(s.items())), ' SAME:' + ','.join(same) if same else '')
        prev = s
