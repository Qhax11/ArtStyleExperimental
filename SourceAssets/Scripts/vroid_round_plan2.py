"""Plan VRoid export rounds with deterministic list scrolling.

VRoid resets a list to the top whenever it is opened, and a wheel scroll of k ticks from
that reset state always moves the list by k * TICK pixels (until the list end). So every
view of a list is "reset + k ticks". Each round:

  1. selection: per category, open the list, scroll its planned k, click the next tile
  2. export the VRM
  3. capture: per category, open the list, scroll the k planned for the *following* tile,
     and capture. The selected tile's frame in that capture gives its true position in that
     same view, which also works when the list end limits the scroll.

Usage:
  python vroid_round_plan2.py init <mode> <cat>=<index> ...   set the last exported index
  python vroid_round_plan2.py <round> <mode> <capture> ...     captures in the order printed
                                                               by the previous round

Prints the round's batch actions (JSON) on stdout and a status per category on stderr.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vroid_list_locator as loc  # noqa: E402

OUT_DIR = r"D:\Projects\ArtStyleExperimental\SourceAssets\VRoid\presets"
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vroid_rounds_state2.json")
TICK = 37.87
ROW = 117.5
ICONS = {"tops": 112, "bottoms": 148, "dress": 185, "neck": 221, "arm": 258,
         "socks": 367, "shoes": 403, "hair": 76}
FIRST_ROW = {"hair": 145.0}  # screen y of the first row's centre at the reset view
DEFAULT_FIRST_ROW = 182.0
REGION = {"hair": (50, 88, 226, 740)}
DEFAULT_REGION = (50, 125, 226, 740)
VIEW_TOP = {"hair": 90.0}
MODES = {
    "outfit": ["tops", "bottoms", "neck", "arm", "socks", "shoes"],
    "dress": ["dress", "neck", "arm", "socks", "shoes", "hair"],
}
TARGET_Y = 420.0  # where a planned tile should sit in its view
# Presets per list, counted earlier (socks and shoes stop when the selection stops advancing).
LIMITS = {"tops": 100, "bottoms": 66, "dress": 37, "neck": 18, "arm": 16}


def first_row(cat):
    return FIRST_ROW.get(cat, DEFAULT_FIRST_ROW)


def region(cat):
    return REGION.get(cat, DEFAULT_REGION)


def k_for(cat, index):
    """Ticks that bring tile `index` near TARGET_Y (assuming the list end is not reached)."""
    y = first_row(cat) + ROW * (index // 2)
    return max(0, int(round((y - TARGET_Y) / TICK)))


def predicted_y(cat, index, k):
    return first_row(cat) + ROW * (index // 2) - TICK * k


def tile_present(path, cat, x, y):
    """True when the capture shows a tile (grey box) around screen point (x, y)."""
    x0, y0, x1, y1 = region(cat)
    im = np.asarray(Image.open(path).convert("L"), dtype=float)
    h, w = im.shape
    sx, sy = (x1 - x0) / w, (y1 - y0) / h
    cx, cy = int((x - x0) / sx), int((y - y0) / sy)
    patch = im[max(cy - 15, 0):cy + 15, max(cx - 25, 0):cx + 25]
    return patch.size > 0 and patch.mean() < 251


def click(x, y, summary):
    return {"action": "left_click", "coordinate": [round(x), round(y)], "action_summary": summary}


def wait(s):
    return {"action": "wait", "duration": s}


def open_list(cat, k):
    acts = []
    if cat == "hair":
        acts += [click(150, 35, "Opens the Hairstyle tab"), wait(2)]
    y = ICONS[cat]
    acts += [{"action": "mouse_move", "coordinate": [18, y]}, wait(0.3),
             click(18, y, f"Opens the {cat} list"), wait(0.4),
             click(18, y, "Clicks the same list icon again"),
             {"action": "mouse_move", "coordinate": [130, 420]}, wait(1.5)]
    if k:
        acts += [{"action": "scroll", "coordinate": [130, 420], "scroll_direction": "down",
                  "scroll_amount": k}, wait(2)]
    return acts


def export_actions(path):
    return [
        wait(1),
        click(1383, 35, "Opens the export menu"), wait(1.5),
        click(1287, 51, "Opens the Export as VRM screen"), wait(3),
        click(1343, 167, "Opens the VRM export settings"), wait(2),
        {"action": "scroll", "coordinate": [722, 500], "scroll_direction": "down", "scroll_amount": 50},
        wait(1),
        click(722, 582, "Confirms the VRM export"), wait(15),
        click(408, 316, "Focuses the file name field"),
        {"action": "key", "text": "ctrl+a", "action_summary": "Selects the file name text"},
        {"action": "type", "text": path, "action_summary": "Types the export file path"},
        {"action": "key", "text": "Return", "action_summary": "Saves the VRM file"}, wait(6),
        click(18, 35, "Closes the export screen"), wait(3),
    ]


def outfit_tab():
    return [click(297, 35, "Opens the Outfit tab"), wait(2)]


def main():
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    if sys.argv[1] == "init":
        mode = sys.argv[2]
        st = state.setdefault(mode, {})
        for item in sys.argv[3:]:
            cat, idx = item.split("=")
            st[cat] = {"index": int(idx), "k_view": 0, "done": False}
        json.dump(state, open(STATE, "w"), indent=1)
        print(json.dumps(state[mode]))
        return

    rnd, mode = int(sys.argv[1]), sys.argv[2]
    cats = MODES[mode]
    st = state[mode]
    paths = sys.argv[3:]
    assert len(paths) == len(cats)

    selections = {}
    for cat, path in zip(cats, paths):
        c = st[cat]
        if c["done"]:
            continue
        loc.VIEW_TOP = VIEW_TOP.get(cat, 133.0)
        found = loc.analyse(path, region(cat))["selected"]
        idx, k = c["index"], c["k_view"]
        col = idx % 2
        if found and found[0] == loc.COLS[col]:
            y_sel = found[1]
            how = "frame"
        else:
            y_sel = predicted_y(cat, idx, k)
            how = "predicted" if not found else f"predicted (frame at {found})"
        nxt = idx + 1
        ny = y_sel + (ROW if col == 1 else 0)
        nx = loc.COLS[nxt % 2]
        limit = LIMITS.get(cat)
        if limit is not None and nxt > limit:
            c["done"] = True
            print(f"{cat}: DONE at index {idx} (list has {limit})", file=sys.stderr)
            continue
        if c.get("last_sel") == [idx, round(y_sel)] and c.get("repeat", 0) >= 1:
            c["done"] = True
            print(f"{cat}: DONE, selection did not advance", file=sys.stderr)
            continue
        if c.get("last_sel") == [idx, round(y_sel)]:
            c["repeat"] = c.get("repeat", 0) + 1
        sel_k = k
        if ny + 35 > loc.VIEW_BOTTOM:
            extra = int(np.ceil((ny - 600) / TICK))
            sel_k = k + extra
            ny -= TICK * extra
        elif not tile_present(path, cat, nx, ny):
            c["done"] = True
            print(f"{cat}: DONE after index {idx} (no tile at {nx:.0f},{ny:.0f})", file=sys.stderr)
            continue
        selections[cat] = (sel_k, nx, ny)
        c["last_sel"] = [nxt, None]
        c["index"] = nxt
        c["k_view"] = 0
        print(f"{cat}: select index {nxt} at ({nx:.0f},{ny:.0f}) k={sel_k} ({how})", file=sys.stderr)
    json.dump(state, open(STATE, "w"), indent=1)

    actions = []
    order = (["hair"] if "hair" in selections else []) + [c for c in cats if c != "hair" and c in selections]
    in_outfit = False
    for cat in order:
        k, x, y = selections[cat]
        if cat != "hair" and not in_outfit:
            actions += outfit_tab()
            in_outfit = True
        actions += open_list(cat, k)
        actions += [click(x, y, f"Selects the next {cat} preset"), wait(3 if cat == "hair" else 2)]
    prefix = "p" if mode == "outfit" else "d"
    actions += export_actions(os.path.join(OUT_DIR, f"{prefix}{rnd:03d}.vrm"))
    capture_order = [c for c in cats if c != "hair"] + (["hair"] if "hair" in cats else [])
    actions += outfit_tab()
    for cat in capture_order:
        c = st[cat]
        k = 0 if c["done"] else c["k_view"]
        actions += open_list(cat, k)
        actions[-1:] = actions[-1:]  # keep
        actions += [{"action": "mouse_move", "coordinate": [700, 450]}, wait(0.8),
                    {"action": "zoom", "region": list(region(cat)), "scale": 0.5}]
    print("capture order: " + " ".join(capture_order), file=sys.stderr)
    print(json.dumps(actions, separators=(",", ":")))


if __name__ == "__main__":
    main()
