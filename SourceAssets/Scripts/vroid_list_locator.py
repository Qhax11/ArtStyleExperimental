"""Find the selected tile in captures of VRoid Studio item lists and plan the next click.

VRoid lists are two-column grids. The selected tile has a blue frame. Given a capture of
the list area, this prints the selected tile and where to click for the next tile, in
screen coordinates, and whether the list should be scrolled before the following round.

Usage:
  python vroid_list_locator.py [--view <top> <bottom>] <x0> <y0> <x1> <y1> <capture.jpg> [<capture.jpg> ...]

<x0..y1> is the screen region the captures were zoomed from. Each capture is reported as
one JSON line: {"file", "selected": [x, y] | null, "next": [x, y] | null, "thumb": [x, y0, y1]}.
"""
import json
import sys

import numpy as np
from PIL import Image

ROW = 117.5           # screen pixels between tile rows
COLS = (91.0, 169.0)  # screen x of the two tile columns
TILE_H = 100.0        # tile height on screen
VIEW_TOP, VIEW_BOTTOM = 133.0, 738.0  # visible list area on screen
SCROLL_X = 219.0


def blue_mask(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (b > 170) & (b - r > 40) & (g > r)


EDGES = ((56.0, 128.0), (134.0, 205.0))  # screen x of each column's tile frame


def analyse(path, region):
    x0, y0, x1, y1 = region
    im = np.asarray(Image.open(path).convert("RGB"), dtype=int)
    h, w = im.shape[:2]
    sx, sy = (x1 - x0) / w, (y1 - y0) / h
    mask = blue_mask(im)

    def edge_column(x):
        c = (x - x0) / sx
        lo, hi = int(np.floor(c - 1.5)), int(np.ceil(c + 1.5))
        return mask[:, max(lo, 0):min(hi + 1, w)].any(axis=1)

    best = None
    for col, (ex0, ex1) in enumerate(EDGES):
        both = edge_column(ex0) & edge_column(ex1)
        runs, start = [], None
        for i, v in enumerate(list(both) + [False]):
            if v and start is None:
                start = i
            if not v and start is not None:
                runs.append((start, i - 1))
                start = None
        for a, b in runs:
            length = (b - a + 1) * sy
            if length < 35:
                continue
            top, bottom = y0 + a * sy, y0 + (b + 1) * sy
            # A frame cut by the view edge: place the centre from the uncut end.
            if top <= VIEW_TOP + 4 and length < TILE_H - 8:
                cy = bottom - TILE_H / 2
            elif bottom >= VIEW_BOTTOM - 4 and length < TILE_H - 8:
                cy = top + TILE_H / 2
            else:
                cy = (top + bottom) / 2
            if best is None or length > best[0]:
                best = (length, col, cy)

    # Scroll thumb: the longest grey run near the scrollbar column.
    thumb = None
    tx = int((SCROLL_X - x0) / sx)
    if 0 <= tx < w:
        col = im[:, max(tx - 1, 0):tx + 2, :].mean(axis=(1, 2)); grey = (col > 195) & (col < 229)
        runs, start = [], None
        for i, v in enumerate(list(grey) + [False]):
            if v and start is None:
                start = i
            if not v and start is not None:
                runs.append((start, i - 1))
                start = None
        if runs:
            a, b = max(runs, key=lambda r: r[1] - r[0])
            thumb = [SCROLL_X, round(y0 + a * sy, 1), round(y0 + b * sy, 1)]

    result = {"file": path, "selected": None, "next": None, "thumb": thumb}
    if best:
        _, col, cy = best
        result["selected"] = [COLS[col], round(cy, 1)]
        if col == 0:
            nx, ny = COLS[1], cy
        else:
            nx, ny = COLS[0], cy + ROW
        # Click inside the visible part of the next tile.
        vis_top = max(ny - TILE_H / 2, VIEW_TOP)
        vis_bottom = min(ny + TILE_H / 2, VIEW_BOTTOM)
        if vis_bottom - vis_top >= 30:
            result["next"] = [nx, round((vis_top + vis_bottom) / 2, 1)]
        result["scroll"] = bool(ny > VIEW_BOTTOM - 2.2 * ROW)
    return result


def main():
    global VIEW_TOP, VIEW_BOTTOM
    args = sys.argv[1:]
    if args[0] == "--view":
        VIEW_TOP, VIEW_BOTTOM = float(args[1]), float(args[2])
        args = args[3:]
    region = [float(v) for v in args[:4]]
    for path in args[4:]:
        print(json.dumps(analyse(path, region)))


if __name__ == "__main__":
    main()
