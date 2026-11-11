#include "DressUp/DressUpSound.h"

#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"

void DressUp::PlaySound(const UObject* WorldContext, const TCHAR* Name)
{
	if (!WorldContext)
	{
		return;
	}
	const FString Asset = FString::Printf(TEXT("SFX_%s"), Name);
	const TSoftObjectPtr<USoundBase> Sound(FSoftObjectPath(FString::Printf(TEXT("/Game/DressUp/Audio/SFX/%s.%s"), *Asset, *Asset)));
	if (USoundBase* Loaded = Sound.LoadSynchronous())
	{
		UGameplayStatics::PlaySound2D(WorldContext, Loaded);
	}
}
