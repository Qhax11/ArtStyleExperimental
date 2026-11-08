"""Draw the drag-to-rotate hint icon: a mouse with its left button lit, over a two-way turn arrow.

Usage: python make_rotate_icon.py <out.png>
"""
import math
import sys

from PIL import Image, ImageDraw

SCALE = 4
SIZE = 256 * SCALE
DARK = (90, 35, 64, 255)
ACCENT = (169, 63, 108, 255)
BODY = (242, 196, 211, 255)


def p(v):
    return v * SCALE


im = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
d = ImageDraw.Draw(im)

# Mouse body, left button, button divider, wheel.
box = (p(88), p(14), p(168), p(138))
d.rounded_rectangle(box, radius=p(38), fill=BODY, outline=DARK, width=p(7))
mask = Image.new("L", (SIZE, SIZE), 0)
ImageDraw.Draw(mask).rounded_rectangle((p(92), p(18), p(164), p(134)), radius=p(34), fill=255)
left = Image.new("L", (SIZE, SIZE), 0)
ImageDraw.Draw(left).rectangle((p(92), p(18), p(128), p(66)), fill=255)
lit = Image.new("RGBA", (SIZE, SIZE), ACCENT)
im.paste(lit, (0, 0), Image.composite(mask, Image.new("L", (SIZE, SIZE), 0), left))
d = ImageDraw.Draw(im)
d.line((p(128), p(16), p(128), p(66)), fill=DARK, width=p(6))
d.line((p(90), p(66), p(166), p(66)), fill=DARK, width=p(6))

# Turn arrow: the lower part of an ellipse, with a head at each end following the curve.
cx, cy, rx, ry = p(128), p(138), p(100), p(84)
START, END = 28, 152
radius = p(17) / 2
for i in range(START * 4, END * 4 + 1):
    a = math.radians(i / 4)
    x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
    d.ellipse((x - radius, y - radius, x + radius, y + radius), fill=ACCENT)
for angle, way in ((START, -1), (END, 1)):
    a = math.radians(angle)
    x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
    tx, ty = way * -rx * math.sin(a), way * ry * math.cos(a)
    length = math.hypot(tx, ty)
    tx, ty = tx / length, ty / length
    tip = (x + tx * p(34), y + ty * p(34))
    left = (x - ty * p(27), y + tx * p(27))
    right = (x + ty * p(27), y - tx * p(27))
    d.polygon([tip, left, right], fill=ACCENT)

im.resize((256, 256), Image.LANCZOS).save(sys.argv[1])
