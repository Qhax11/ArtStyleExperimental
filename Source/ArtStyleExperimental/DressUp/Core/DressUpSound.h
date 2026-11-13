// Interface and wardrobe sound effects. The sounds are made by SourceAssets/Scripts/make_sfx.py,
// imported on SC_Effects by ue_import_sfx.py and listed by name in Project Settings > Dress Up.

#pragma once

#include "CoreMinimal.h"

namespace DressUp
{
	/** Plays the sound listed as Name in Project Settings > Dress Up > Sounds, in 2D. Does nothing if there is none. */
	ARTSTYLEEXPERIMENTAL_API void PlaySound(const UObject* WorldContext, const TCHAR* Name);

	/** Soft pop for buttons that have no sound of their own. */
	inline void PlayClick(const UObject* WorldContext) { PlaySound(WorldContext, TEXT("UI_Click")); }
}
