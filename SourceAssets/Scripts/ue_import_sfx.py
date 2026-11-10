"""Unreal editor Python (run with the `py` console command): imports SourceAssets/Audio/sfx/*.wav as
/Game/DressUp/Audio/SFX/SFX_<Name>, replacing older imports, and routes them to SC_Effects so the
effects volume slider controls them. Writes a short report to Saved/DressUpImport/sfx_import.txt.
"""
import glob
import os

import unreal

PROJECT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
SOURCE = os.path.join(PROJECT, "SourceAssets", "Audio", "sfx")
DEST = "/Game/DressUp/Audio/SFX"
EFFECTS = unreal.load_asset("/Game/DressUp/Audio/SC_Effects.SC_Effects")

tasks = []
for path in sorted(glob.glob(os.path.join(SOURCE, "SFX_*.wav"))):
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = DEST
    task.replace_existing = True
    task.automated = True
    task.save = False
    tasks.append(task)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)

lines = []
for task in tasks:
    name = os.path.splitext(os.path.basename(task.filename))[0]
    sound = unreal.load_asset(f"{DEST}/{name}.{name}")
    if sound is None:
        lines.append(f"FAIL {name}")
        continue
    sound.set_editor_property("sound_class_object", EFFECTS)
    unreal.EditorAssetLibrary.save_loaded_asset(sound)
    lines.append(f"OK {name} {sound.get_editor_property('duration'):.2f}s")

report = os.path.join(PROJECT, "Saved", "DressUpImport", "sfx_import.txt")
with open(report, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
unreal.log("SFX import: " + ", ".join(lines))
