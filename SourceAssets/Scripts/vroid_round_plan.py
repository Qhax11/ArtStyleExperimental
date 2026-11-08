"""Plan the next VRoid export round from list captures.

Each round selects the next preset in every category list, exports a VRM, and captures
the lists again. Captures come in CATEGORIES order. Prints the computer-use batch actions
as JSON, followed by a status line per category on stderr.

Usage:
  python vroid_round_plan.py <round> <mode> <capture> [<capture> ...]

mode "outfit": categories tops, bottoms, neck, arm, socks, shoes, hair.
mode "dress":  categories dress, neck, arm, socks, shoes, hair.
Round numbers become file names: outfit p<NNN>.vrm, dress d<NNN>.vrm.
State of finished categories is kept in vroid_rounds_state.json next to this script.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vroid_list_locator as loc  # noqa: E402

OUT_DIR = r"D:\Projects\ArtStyleExperimental\SourceAssets\VRoid\presets"
OUTFIT_ICONS = {"tops": 112, "bottoms": 148, "dress": 185, "neck": 221, "arm": 258,
                "socks": 367, "shoes": 403}
LIST_REGION = (50, 125, 226, 740)
HAIR_REGION = (50, 88, 226, 740)
MODES = {
    "outfit": ["tops", "bottoms", "neck", "arm", "socks", "shoes", "hair"],
    "dress": ["dress", "neck", "arm", "socks", "shoes", "hair"],
}
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vroid_rounds_state.json")


def click(x, y, summary):
    return {"action": "left_click", "coordinate": [round(x), round(y)], "action_summary": summary}


def icon(y, summary):
    """Category icons ignore a click that arrives with the pointer from far away."""
    return [{"action": "mouse_move", "coordinate": [18, y]}, {"action": "wait", "duration": 0.3},
            click(18, y, summary), {"action": "wait", "duration": 0.4},
            click(18, y, "Clicks the same list icon again")]


def wait(s):
    return {"action": "wait", "duration": s}


def drag_actions(thumb=None, rows=2.5):
    """Scroll the list down a little. The wheel distance varies; the next capture finds the tile."""
    return [wait(1.5), {"action": "mouse_move", "coordinate": [130, 420]}, wait(1),
            {"action": "scroll", "coordinate": [130, 420], "scroll_direction": "down", "scroll_amount": 3},
            wait(1.5)]


def list_offset(before, after):
    """Screen pixels the list content moved up between two captures of the same list."""
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(before).convert("L"), dtype=float)
    ia = Image.open(before)
    b = np.asarray(Image.open(after).convert("L").resize(ia.size), dtype=float)
    h, w = a.shape
    a, b = a[:, : int(w * 0.85)], b[:, : int(w * 0.85)]
    best = None
    for d in range(-int(h * 0.6), int(h * 0.6) + 1):
        if d >= 0:
            pa, pb = a[d:], b[: h - d]
        else:
            pa, pb = a[: h + d], b[-d:]
        e = ((pa - pb) ** 2).mean()
        if best is None or e < best[1]:
            best = (d, e)
    sy = (HAIR_REGION[3] - HAIR_REGION[1]) / h
    return best[0] * sy, best[1]


def plan_hair(state, capture):
    """Hair sets show no selection frame, so the position is tracked in the state file."""
    hs = state.setdefault("hair", {"index": 1, "col": 1, "y": 145.0, "capture": capture,
                                   "dragged": False, "done": False})
    if hs["dragged"]:
        moved, err = list_offset(hs["capture"], capture)
        hs["y"] -= moved
        hs["last_move"] = [round(float(moved), 1), round(float(err), 1)]
        if abs(moved) < 3:
            hs["stuck"] = hs.get("stuck", 0) + 1
    loc.VIEW_TOP = 90.0
    seen = loc.analyse(capture, HAIR_REGION)["selected"]
    if seen:
        hs["stuck"] = 0
        hs["col"] = loc.COLS.index(seen[0])
        hs["y"] = seen[1]
    hs["capture"] = capture
    hs["dragged"] = False
    if hs["done"]:
        return ("done", None, None)
    col = 1 - hs["col"]
    y = hs["y"] + (loc.ROW if col == 0 else 0)
    if y + 30 > loc.VIEW_BOTTOM:
        if hs.get("stuck", 0) >= 2:
            hs["done"] = True
            return ("done", None, None)
        hs["dragged"] = True
        return ("scroll", None, None)
    hs["index"] += 1
    hs["col"], hs["y"] = col, y
    if y > loc.VIEW_BOTTOM - 2.2 * loc.ROW:
        hs["dragged"] = True
    return ("click", [loc.COLS[col], min(y, loc.VIEW_BOTTOM - 30)], hs["dragged"])


def analyse(cat, path):
    if cat == "hair":
        loc.VIEW_TOP = 90.0
        result = loc.analyse(path, HAIR_REGION)
    else:
        loc.VIEW_TOP = 133.0
        result = loc.analyse(path, LIST_REGION)
    return result


def main():
    rnd, mode = int(sys.argv[1]), sys.argv[2]
    cats = MODES[mode]
    paths = sys.argv[3:]
    assert len(paths) == len(cats), f"need {len(cats)} captures"
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    done = set(state.get(mode + "_done", []))

    plans = {}
    for cat, path in zip(cats, paths):
        if cat == "hair":
            plans[cat] = plan_hair(state, path)
            print(f"hair: {plans[cat][0]} state={state['hair']}", file=sys.stderr)
            continue
        r = analyse(cat, path)
        if cat in done:
            plans[cat] = ("done", None, None)
        elif r["next"]:
            plans[cat] = ("click", r["next"], r["thumb"] if r.get("scroll") else None)
        elif r.get("scroll") and r["thumb"]:
            plans[cat] = ("scroll", None, r["thumb"])
        elif r["selected"]:
            done.add(cat)
            plans[cat] = ("done", None, None)
        else:
            plans[cat] = ("lost", None, None)
        print(f"{cat}: {plans[cat][0]} sel={r['selected']} next={r['next']} thumb={r['thumb']}",
              file=sys.stderr)
    state[mode + "_done"] = sorted(done)
    json.dump(state, open(STATE, "w"))

    actions = []
    # Hair first: the round starts on the Hairstyle tab.
    kind, target, drag = plans["hair"]
    if kind == "click":
        actions += [click(*target, "Selects the next hairstyle"), wait(3)]
    if drag or kind == "scroll":
        # Hair thumb: found in the last hair capture.
        loc.VIEW_TOP = 90.0
        actions += drag_actions()
    actions += [click(297, 35, "Opens the Outfit tab"), wait(2)]
    for cat in cats:
        if cat == "hair":
            continue
        kind, target, thumb = plans[cat]
        if kind in ("done", "lost"):
            continue
        actions += icon(OUTFIT_ICONS[cat], f"Opens the {cat} list") + [wait(1.2)]
        if kind == "click":
            actions += [click(*target, f"Selects the next {cat} preset"), wait(1.5)]
        if thumb:
            loc.VIEW_TOP = 133.0
            actions += drag_actions(thumb)

    prefix = "p" if mode == "outfit" else "d"
    path = os.path.join(OUT_DIR, f"{prefix}{rnd:03d}.vrm")
    actions += [
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
        {"action": "key", "text": "Return", "action_summary": "Saves the VRM file"}, wait(5),
        click(18, 35, "Closes the export screen"), wait(3),
    ]
    for cat in cats:
        if cat == "hair":
            continue
        actions += icon(OUTFIT_ICONS[cat], f"Opens the {cat} list") + [
                    {"action": "mouse_move", "coordinate": [700, 450]}, wait(1.5),
                    {"action": "zoom", "region": list(LIST_REGION), "scale": 0.5}]
    actions += [click(150, 35, "Opens the Hairstyle tab"), wait(2)] + icon(76, "Opens the hairstyle sets list") + [
                {"action": "mouse_move", "coordinate": [700, 450]}, wait(1.5),
                {"action": "zoom", "region": list(HAIR_REGION), "scale": 0.5}]
    # Only the part before the export changes from round to round.
    cut = next(i for i, a in enumerate(actions) if a.get("action_summary") == "Opens the export menu")
    head = actions[: cut - 1]
    open(os.path.join(os.path.dirname(STATE), "plan_full.json"), "w").write(json.dumps(actions))
    print(json.dumps(head, separators=(",", ":")))


if __name__ == "__main__":
    main()
