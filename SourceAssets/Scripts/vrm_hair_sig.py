"""Hair geometry signature of VRoid VRM exports: hair textures are shared between hairstyles,
so hash the vertex data of primitives that use a _HAIR material instead."""
import hashlib, sys
from vrm_signatures import load

def hair_sig(path):
    doc, data, bin_off = load(path)
    mats = {i for i, m in enumerate(doc.get('materials', [])) if '_HAIR' in m.get('name', '')}
    h = hashlib.md5()
    nverts = 0
    for mesh in doc['meshes']:
        for p in mesh['primitives']:
            if p.get('material') not in mats:
                continue
            acc = doc['accessors'][p['attributes']['POSITION']]
            bv = doc['bufferViews'][acc['bufferView']]
            s = bin_off + bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
            h.update(data[s:s + acc['count'] * 12])
            nverts += acc['count']
    return h.hexdigest()[:8], nverts

if __name__ == '__main__':
    seen = {}
    for p in sys.argv[1:]:
        sig, n = hair_sig(p)
        print(p, sig, n, 'DUP of ' + seen[sig] if sig in seen else '')
        seen.setdefault(sig, p)
