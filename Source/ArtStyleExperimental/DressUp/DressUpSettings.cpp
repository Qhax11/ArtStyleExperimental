#include "DressUp/DressUpSettings.h"

#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/GameUserSettings.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundClass.h"

void UDressUpSettingsSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	Settings = Cast<UDressUpSettingsSave>(UGameplayStatics::LoadGameFromSlot(SlotName, 0));
	if (!Settings)
	{
		Settings = Cast<UDressUpSettingsSave>(UGameplayStatics::CreateSaveGameObject(UDressUpSettingsSave::StaticClass()));
	}
#if !WITH_EDITOR
	// In the editor the window belongs to the editor, so fullscreen is left alone.
	ApplyFullscreen();
#endif
}

UDressUpSettingsSubsystem* UDressUpSettingsSubsystem::Get(const UObject* WorldContext)
{
	const UWorld* World = WorldContext ? WorldContext->GetWorld() : nullptr;
	const UGameInstance* GameInstance = World ? World->GetGameInstance() : nullptr;
	return GameInstance ? GameInstance->GetSubsystem<UDressUpSettingsSubsystem>() : nullptr;
}

float UDressUpSettingsSubsystem::GetVolume(EDressUpVolume Channel) const
{
	if (!Settings)
	{
		return 1.0f;
	}
	switch (Channel)
	{
	case EDressUpVolume::Music:
		return Settings->MusicVolume;
	case EDressUpVolume::Effects:
		return Settings->EffectsVolume;
	default:
		return Settings->MasterVolume;
	}
}

void UDressUpSettingsSubsystem::SetVolume(EDressUpVolume Channel, float Value)
{
	if (!Settings)
	{
		return;
	}
	Value = FMath::Clamp(Value, 0.0f, 1.0f);
	switch (Channel)
	{
	case EDressUpVolume::Music:
		Settings->MusicVolume = Value;
		break;
	case EDressUpVolume::Effects:
		Settings->EffectsVolume = Value;
		break;
	default:
		Settings->MasterVolume = Value;
		break;
	}
	ApplyAudio(LastWorldContext.Get());
	Save();
}

void UDressUpSettingsSubsystem::SetFullscreen(bool bFullscreen)
{
	if (!Settings)
	{
		return;
	}
	Settings->bFullscreen = bFullscreen;
	ApplyFullscreen();
	Save();
}

void UDressUpSettingsSubsystem::SetPlayerName(const FString& Name)
{
	if (!Settings)
	{
		return;
	}
	Settings->PlayerName = Name.TrimStartAndEnd();
	Save();
}

void UDressUpSettingsSubsystem::ApplyAudio(const UObject* WorldContext)
{
	if (!Settings)
	{
		return;
	}
	if (WorldContext)
	{
		LastWorldContext = WorldContext;
	}
	// Child classes are scaled by their parent, so master turns music and effects down too.
	const TPair<TSoftObjectPtr<USoundClass>, float> Channels[] = {
		{MasterClass, Settings->MasterVolume},
		{MusicClass, Settings->MusicVolume},
		{EffectsClass, Settings->EffectsVolume},
	};
	for (const TPair<TSoftObjectPtr<USoundClass>, float>& Channel : Channels)
	{
		if (USoundClass* Class = Channel.Key.LoadSynchronous())
		{
			Class->Properties.Volume = Channel.Value;
		}
	}
}

void UDressUpSettingsSubsystem::ApplyFullscreen()
{
	if (UGameUserSettings* UserSettings = UGameUserSettings::GetGameUserSettings())
	{
		UserSettings->SetFullscreenMode(Settings->bFullscreen ? EWindowMode::WindowedFullscreen : EWindowMode::Windowed);
		UserSettings->ApplySettings(false);
	}
}

void UDressUpSettingsSubsystem::Save()
{
	UGameplayStatics::SaveGameToSlot(Settings, SlotName, 0);
}
