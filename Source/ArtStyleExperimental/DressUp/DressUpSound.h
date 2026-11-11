// Interface and wardrobe sound effects. The sounds are made by SourceAssets/Scripts/make_sfx.py and
// imported to /Game/DressUp/Audio/SFX on SC_Effects by ue_import_sfx.py.

#pragma once

#include "CoreMinimal.h"

namespace DressUp
{
	/** Plays /Game/DressUp/Audio/SFX/SFX_<Name> in 2D. Does nothing if the sound is missing. */
	ARTSTYLEEXPERIMENTAL_API void PlaySound(const UObject* WorldContext, const TCHAR* Name);

	/** Soft pop for buttons that have no sound of their own. */
	inline void PlayClick(const UObject* WorldContext) { PlaySound(WorldContext, TEXT("UI_Click")); }
}
