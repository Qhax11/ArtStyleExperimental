"""Chroma-key item captures (green backdrop) into transparent 256px icons.

Usage: python make_icons.py <capture_dir> <out_dir>
Each <capture_dir>/<Name>.png becomes <out_dir>/T_Icon_<Name>.png.
"""
import sys, os, glob
from PIL import Image

SIZE = 256
PAD = 0.08


def key(im):
    im = im.convert('RGB')
    W, H = im.size
    src = im.load()
    out = Image.new('RGBA', im.size)
    dst = out.load()
    for y in range(H):
        for x in range(W):
            r, g, b = src[x, y]
            m = max(r, b)
            # how "green" the pixel is: 0 = not green, 1 = pure backdrop
            if g <= 80:
                t = 0.0
            else:
                ratio = g / max(m, 1)
                t = min(max((ratio - 1.15) / (1.6 - 1.15), 0.0), 1.0)
            a = int(round(255 * (1 - t)))
            if a and g > m:
                g = m  # despill: clamp green to the other channels
            dst[x, y] = (r, g, b, a)
    return out


def main(src_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(src_dir, '*.png'))):
        name = os.path.splitext(os.path.basename(f))[0]
        im = Image.open(f)
        W, H = im.size
        im = im.crop(((W - H) // 2, 0, (W + H) // 2, H))  # centre square, drops the axis gizmo
        rgba = key(im)
        bbox = rgba.getchannel('A').point(lambda a: 255 if a > 40 else 0).getbbox()
        if not bbox:
            print('empty', name)
            continue
        rgba = rgba.crop(bbox)
        w, h = rgba.size
        side = int(max(w, h) * (1 + 2 * PAD))
        canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
        canvas.paste(rgba, ((side - w) // 2, (side - h) // 2))
        canvas = canvas.resize((SIZE, SIZE), Image.LANCZOS)
        canvas.save(os.path.join(out_dir, f'T_Icon_{name}.png'))
        print('ok', name, bbox)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
