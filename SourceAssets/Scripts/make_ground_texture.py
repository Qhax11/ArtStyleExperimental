"""Turns the painted ground of a backdrop into a seamless top-down ground texture.

  python make_ground_texture.py <backdrop.png> <out.png> [--horizon 0.69] [--top 0.84] [--size 1024]

The painting shows the ground in perspective. A trapezoid of it (from --top down to the bottom
edge, narrowing towards the horizon like a real ground rectangle would) is mapped back to a
square, then the square is made to tile: it is blended with a copy shifted by half its size,
so its edges match the opposite edges.

--horizon  height of the painting's eye level, as a fraction of the image height (where the
           bases of distant trees sit)
--top      how far up the painted ground the texture reaches; closer to the horizon gives more
           ground but a blurrier far edge
"""
import argparse

import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("dst")
ap.add_argument("--horizon", type=float, default=0.69)
ap.add_argument("--top", type=float, default=0.84)
ap.add_argument("--size", type=int, default=1024)
args = ap.parse_args()

img = Image.open(args.src).convert("RGB")
w, h = img.size
yh = args.horizon * h
y_far = args.top * h
y_near = h - 1
# A ground rectangle as wide as the image at the bottom edge appears narrower further away.
shrink = (y_far - yh) / (y_near - yh)
half = w / 2
quad = [  # far-left, far-right, near-right, near-left in the painting
    (half - half * shrink, y_far), (half + half * shrink, y_far), (w - 1, y_near), (0, y_near),
]
n = args.size
square = [(0, 0), (n, 0), (n, n), (0, n)]


def perspective_coeffs(dst, src):
    """Coefficients for Image.transform: map output (dst) points to input (src) points."""
    rows = []
    for (x, y), (u, v) in zip(dst, src):
        rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        rows.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    a = np.array(rows, dtype=float)
    b = np.array(src, dtype=float).reshape(8)
    return np.linalg.solve(a, b)


flat = img.transform((n, n), Image.Transform.PERSPECTIVE, perspective_coeffs(square, quad), Image.Resampling.BICUBIC)
a = np.asarray(flat, dtype=np.float32)

# Seamless: blend with a copy rolled by half, weighting each by how far it is from its own edges.
shifted = np.roll(np.roll(a, n // 2, axis=0), n // 2, axis=1)
t = np.linspace(0, 1, n)
edge = np.minimum(t, 1 - t) * 2  # 0 at the edges, 1 in the middle
wa = np.outer(edge, edge)[..., None]
wb = np.roll(np.roll(wa, n // 2, axis=0), n // 2, axis=1)
out = (a * wa + shifted * wb) / np.maximum(wa + wb, 1e-4)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(args.dst)
print("GROUND", args.dst, n, "shrink", round(shrink, 3))
