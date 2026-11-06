// Player settings (volumes, fullscreen), saved to disk and applied in every level.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "DressUpSettings.generated.h"

class USoundClass;

UENUM(BlueprintType)
enum class EDressUpVolume : uint8
{
	Master,
	Music,
	Effects
};

UCLASS()
class ARTSTYLEEXPERIMENTAL_API UDressUpSettingsSave : public USaveGame
{
	GENERATED_BODY()

public:
	UPROPERTY()
	float MasterVolume = 1.0f;

	UPROPERTY()
	float MusicVolume = 0.8f;

	UPROPERTY()
	float EffectsVolume = 1.0f;

	UPROPERTY()
	bool bFullscreen = true;
};

/**
 * Holds the settings for the whole game session. Volumes are written to the sound classes
 * (SC_Music and SC_Effects sit under SC_Master), so music and effects added later only
 * need the right sound class.
 */
UCLASS()
class ARTSTYLEEXPERIMENTAL_API UDressUpSettingsSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;

	UFUNCTION(BlueprintPure, Category = "Settings")
	float GetVolume(EDressUpVolume Channel) const;

	/** Sets a volume (0..1), applies it and saves. */
	UFUNCTION(BlueprintCallable, Category = "Settings")
	void SetVolume(EDressUpVolume Channel, float Value);

	UFUNCTION(BlueprintPure, Category = "Settings")
	bool IsFullscreen() const { return Settings ? Settings->bFullscreen : true; }

	UFUNCTION(BlueprintCallable, Category = "Settings")
	void SetFullscreen(bool bFullscreen);

	/** Writes the volumes into the sound classes. Called on start and whenever a volume changes. */
	UFUNCTION(BlueprintCallable, Category = "Settings", meta = (WorldContext = "WorldContext"))
	void ApplyAudio(const UObject* WorldContext);

	static UDressUpSettingsSubsystem* Get(const UObject* WorldContext);

	UPROPERTY(EditAnywhere, Category = "Settings")
	TSoftObjectPtr<USoundClass> MasterClass = TSoftObjectPtr<USoundClass>(FSoftObjectPath(TEXT("/Game/DressUp/Audio/SC_Master.SC_Master")));

	UPROPERTY(EditAnywhere, Category = "Settings")
	TSoftObjectPtr<USoundClass> MusicClass = TSoftObjectPtr<USoundClass>(FSoftObjectPath(TEXT("/Game/DressUp/Audio/SC_Music.SC_Music")));

	UPROPERTY(EditAnywhere, Category = "Settings")
	TSoftObjectPtr<USoundClass> EffectsClass = TSoftObjectPtr<USoundClass>(FSoftObjectPath(TEXT("/Game/DressUp/Audio/SC_Effects.SC_Effects")));

private:
	void Save();
	void ApplyFullscreen();

	UPROPERTY()
	TObjectPtr<UDressUpSettingsSave> Settings;

	TWeakObjectPtr<const UObject> LastWorldContext;

	static constexpr const TCHAR* SlotName = TEXT("DressUpSettings");
};
