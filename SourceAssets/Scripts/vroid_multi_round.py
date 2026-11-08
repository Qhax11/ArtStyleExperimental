"""Generate several VRoid export rounds in one batch, predicting every click.

Model (measured on VRoid Studio 2.16):
  * opening a list shows the selected tile; when its row is below the first view the row
    sits at screen y = 681 (SEL_Y), i.e. the list offset is 182 + 117.5*row - 681;
  * a wheel scroll of k ticks after opening adds 37.87*k pixels;
  * the offset never exceeds M = 117.5*rows - 607.5 (end of the list).

Usage:
  python vroid_multi_round.py <first_round> <rounds> <mode> <cat>=<selected_index> ...
Prints the batch actions (JSON) and, on stderr, the planned index per category and round.
The batch ends with a capture of every list for verification.
"""
import json
import math
import os
import sys

OUT_DIR = r"D:\Projects\ArtStyleExperimental\SourceAssets\VRoid\presets"
ICONS = {"hair": 76, "tops": 112, "bottoms": 148, "dress": 185, "neck": 221, "arm": 258, "socks": 367, "shoes": 403}
COLS = (91, 169)
FIRST, ROW, TICK, SEL_Y = 182.0, 117.5, 37.87, 681.0
# Number of presets (tiles are 1..N after the "none" tile 0); None = not counted yet.
COUNTS = {"hair": None, "tops": 82, "bottoms": 54, "dress": 33, "neck": 18, "arm": 16, "socks": 34, "shoes": 59}


FIRSTS = {"hair": 145.0}


def max_offset(cat):
    n = COUNTS.get(cat)
    if n is None:
        return float("inf")
    rows = n // 2 + 1
    return ROW * rows - 607.5 - (FIRST - FIRSTS.get(cat, FIRST))


def plan_click(cat, selected, target):
    m = max_offset(cat)
    first = FIRSTS.get(cat, FIRST)
    r_sel, r_t = selected // 2, target // 2
    y_sel_top = first + ROW * r_sel
    off = 0.0 if y_sel_top + 50 <= 738 else min(y_sel_top - SEL_Y, m)
    y = first + ROW * r_t - off
    k = 0
    if y + 35 > 738:
        k = math.ceil((y - 600) / TICK)
        off2 = min(off + TICK * k, m)
        y = first + ROW * r_t - off2
    return k, COLS[target % 2], round(y)


def click(x, y, s):
    return {"action": "left_click", "coordinate": [x, y], "action_summary": s}


def wait(s):
    return {"action": "wait", "duration": s}


def open_list(cat):
    y = ICONS[cat]
    tab = [click(150, 35, "Opens the Hairstyle tab"), wait(2)] if cat == "hair" else []
    return tab + [{"action": "mouse_move", "coordinate": [18, y]}, wait(0.3),
            click(18, y, f"Opens the {cat} list"), wait(0.4),
            click(18, y, "Clicks the same list icon again"),
            {"action": "mouse_move", "coordinate": [130, 420]}, wait(1.5)]


def export(path):
    return [click(1383, 35, "Opens the export menu"), wait(1.5),
            click(1287, 51, "Opens the Export as VRM screen"), wait(3),
            click(1343, 167, "Opens the VRM export settings"), wait(2),
            {"action": "scroll", "coordinate": [722, 500], "scroll_direction": "down", "scroll_amount": 50},
            wait(1), click(722, 582, "Confirms the VRM export"), wait(15),
            click(408, 316, "Focuses the file name field"),
            {"action": "key", "text": "ctrl+a", "action_summary": "Selects the file name text"},
            {"action": "type", "text": path, "action_summary": "Types the export file path"},
            {"action": "key", "text": "Return", "action_summary": "Saves the VRM file"}, wait(6),
            click(18, 35, "Closes the export screen"), wait(3)]


def main():
    first, rounds, mode = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    cur = {}
    for item in sys.argv[4:]:
        cat, idx = item.split("=")
        cur[cat] = int(idx)
    prefix = {"outfit": "p", "dress": "d", "hair": "h"}[mode]
    actions = []
    for j in range(rounds):
        rnd = first + j
        line = []
        for cat, sel in cur.items():
            n = COUNTS.get(cat)
            t = sel + 1
            if n is not None and t > n:
                continue
            k, x, y = plan_click(cat, sel, t)
            actions += open_list(cat)
            if k:
                actions += [{"action": "scroll", "coordinate": [130, 420], "scroll_direction": "down",
                             "scroll_amount": k}, wait(2)]
            actions += [click(x, y, f"Selects {cat} preset {t}"), wait(4 if cat == "hair" else 2)]
            cur[cat] = t
            line.append(f"{cat}={t}@k{k}({x},{y})")
        actions += [wait(1)] + export(os.path.join(OUT_DIR, f"{prefix}{rnd:03d}.vrm"))
        print(f"round {rnd}: " + " ".join(line), file=sys.stderr)
    for cat in cur:
        actions += open_list(cat) + [{"action": "mouse_move", "coordinate": [700, 450]}, wait(0.8),
                                     {"action": "zoom", "region": [50, 88 if cat == "hair" else 125, 226, 740], "scale": 0.5}]
    print("state after: " + " ".join(f"{c}={i}" for c, i in cur.items()), file=sys.stderr)
    print(json.dumps(actions, separators=(",", ":")))


if __name__ == "__main__":
    main()
