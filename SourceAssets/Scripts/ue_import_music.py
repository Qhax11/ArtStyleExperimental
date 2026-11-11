"""Unreal editor Python (run with the `py` console command): imports SourceAssets/Audio/music/LofiLoop.ogg
as /Game/DressUp/Audio/Music/MUS_Lofi, looping, routed to SC_Music. Report: Saved/DressUpImport/music_import.txt.
"""
import os

import unreal

PROJECT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
SOURCE = os.path.join(PROJECT, "SourceAssets", "Audio", "music", "LofiLoop.ogg")
DEST = "/Game/DressUp/Audio/Music"
NAME = "MUS_Lofi"

task = unreal.AssetImportTask()
task.filename = SOURCE
task.destination_path = DEST
task.destination_name = NAME
task.replace_existing = True
task.automated = True
task.save = False
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

report = os.path.join(PROJECT, "Saved", "DressUpImport", "music_import.txt")
sound = unreal.load_asset(f"{DEST}/{NAME}.{NAME}")
if sound is None:
    text = f"FAIL imported={list(task.imported_object_paths)}"
else:
    sound.set_editor_property("looping", True)
    sound.set_editor_property("sound_class_object", unreal.load_asset("/Game/DressUp/Audio/SC_Music.SC_Music"))
    unreal.EditorAssetLibrary.save_loaded_asset(sound)
    text = f"OK {type(sound).__name__} {sound.get_editor_property('duration'):.2f}s looping={sound.get_editor_property('looping')}"
with open(report, "w", encoding="utf-8") as f:
    f.write(text + "\n")
unreal.log("Music import: " + text)
