// Player settings (volumes, fullscreen, name), saved to disk and applied in every level.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "DressUpSettings.generated.h"

class UAudioComponent;
class USoundBase;
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

	/** Empty until the player has given a name. */
	UPROPERTY()
	FString PlayerName;
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

	UFUNCTION(BlueprintPure, Category = "Settings")
	FString GetPlayerName() const { return Settings ? Settings->PlayerName : FString(); }

	UFUNCTION(BlueprintPure, Category = "Settings")
	bool HasPlayerName() const { return !GetPlayerName().IsEmpty(); }

	/** Trims and saves the name. An empty name means the game asks again. */
	UFUNCTION(BlueprintCallable, Category = "Settings")
	void SetPlayerName(const FString& Name);

	/** Writes the volumes into the sound classes. Called on start and whenever a volume changes. */
	UFUNCTION(BlueprintCallable, Category = "Settings", meta = (WorldContext = "WorldContext"))
	void ApplyAudio(const UObject* WorldContext);

	static UDressUpSettingsSubsystem* Get(const UObject* WorldContext);

	/**
	 * Starts the background music if it is not playing yet. It lives on across level changes
	 * (menu to game and back) and keeps playing in the pause menu.
	 */
	UFUNCTION(BlueprintCallable, Category = "Settings", meta = (WorldContext = "WorldContext"))
	void StartMusic(const UObject* WorldContext);

private:
	void Save();
	void ApplyFullscreen();

	UPROPERTY()
	TObjectPtr<UDressUpSettingsSave> Settings;

	UPROPERTY()
	TObjectPtr<UAudioComponent> MusicComponent;

	TWeakObjectPtr<const UObject> LastWorldContext;

	static constexpr const TCHAR* SlotName = TEXT("DressUpSettings");
};
