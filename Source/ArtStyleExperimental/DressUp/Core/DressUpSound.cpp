#include "DressUp/Core/DressUpSound.h"

#include "DressUp/Core/DressUpProjectSettings.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"

void DressUp::PlaySound(const UObject* WorldContext, const TCHAR* Name)
{
	if (!WorldContext)
	{
		return;
	}
	const TSoftObjectPtr<USoundBase>* Sound = UDressUpProjectSettings::Get()->Sounds.Find(FName(Name));
	if (USoundBase* Loaded = Sound ? Sound->LoadSynchronous() : nullptr)
	{
		UGameplayStatics::PlaySound2D(WorldContext, Loaded);
	}
}
