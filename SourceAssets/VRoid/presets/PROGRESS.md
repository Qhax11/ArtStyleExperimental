# VRoid preset export progress

Exports: `pNNN.vrm` = round NNN of the outfit pass (ride-along: one preset per list per round).
Generator: `SourceAssets/Scripts/vroid_multi_round.py` (predicts clicks; batch ends with list captures).
Duplicate check: `python SourceAssets/Scripts/vrm_signatures.py p0*.vrm` (texture hash per category).

Verified list sizes: neck 18, arm 16, socks 34, shoes 59, bottoms 54.
Not verified: tops (assumed 100, probably ~80; watch for repeated Tops signatures), dress 37, hair ~40.

Done (p001-p067):
- tops 1-67, bottoms 1-54 (done), neck 1-18 (done), arm 1-16 (done), socks 1-34 (done), shoes 1-59 (done).
- p052-p056 bottoms are duplicates (list end); 54 exported in p057.
- Hair rode along in p001-p011 with unreliable indices; hair needs its own pass.
- test_dress.vrm: one dress.

Next: `python vroid_multi_round.py 68 6 outfit tops=67` (already generated into multi.json),
continue until Tops signatures repeat, then:
- dress pass (d001...): dresses (dress replaces top and bottom),
- hair pass, accessories (thick glasses, top hat, hat, witch hat, army cap),
- sample model costumes A-Z (G and O done earlier).

Findings for processing:
- material names are renumbered per export (not preset ids); categories by name: Tops, Bottoms,
  Onepiece (some bottoms/tops), Shoes, Accessory (neck); arm items appear as extra Tops materials.
- most socks are body texture (Body_00_SKIN), not meshes: extract by diffing body textures.
- after export: split per category in Blender, dedupe by texture hash, group same-mesh texture
  variants, run fix_cloth_fbx.py, import, DA_*, icons, catalog, scroll box UI, play test.

VRoid model: evrar.vroid is open with presets applied; do NOT save it.
Click model: list opens with the selected row at y=681 (when below the first view),
wheel tick = 37.87 px, list end offset = 117.5*rows - 607.5.

## 2026-11-08: export finished
- Verified list sizes: tops 82 (p001-p082), bottoms 54, dress 33 (d001-d033), neck 18, arm 16,
  socks 34 (body texture), shoes 59, hair 37 (h001-h037; checked with vrm_hair_sig.py, all unique).
- acc_all.vrm: thick glasses, silk hat, straw hat, witch hat, work cap.
- Processing and import: see ROADMAP.md "VRoid toplu içerik".
