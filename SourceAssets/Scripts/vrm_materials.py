"""Print the clothing material names of VRM files (reads the glTF JSON chunk, no Blender)."""
import json, struct, sys, re

def materials(path):
    with open(path, 'rb') as f:
        magic, ver, length = struct.unpack('<III', f.read(12))
        clen, ctype = struct.unpack('<II', f.read(8))
        doc = json.loads(f.read(clen))
    names = [m.get('name', '') for m in doc.get('materials', [])]
    keep = [n for n in names if not re.search(r'_(FACE|EYE|SKIN|HAIR)', n)]
    return sorted(set(re.sub(r' \(Instance\)', '', n) for n in keep))

if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(p, ' | '.join(materials(p)))
