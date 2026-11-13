// Project Settings > Game > Dress Up: every asset the code needs, so no path is written in code.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "DressUpProjectSettings.generated.h"

class UDressUpBody;
class UDressUpCatalog;
class UDressUpColorButton;
class UDressUpFinalScreen;
class UDressUpItemButton;
class UDressUpMainMenu;
class UDressUpNamePrompt;
class UDressUpPanel;
class UDressUpPauseMenu;
class UDressUpTabButton;
class USoundBase;
class USoundClass;
class UWorld;

/** Saved in Config/DefaultGame.ini. */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Dress Up"))
class ARTSTYLEEXPERIMENTAL_API UDressUpProjectSettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	static const UDressUpProjectSettings* Get() { return GetDefault<UDressUpProjectSettings>(); }

	virtual FName GetCategoryName() const override { return TEXT("Game"); }

	// --- Data ---

	/** Items, tabs, palette, poses, messages and scenes. */
	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Data")
	TSoftObjectPtr<UDressUpCatalog> Catalog;

	/** The character's body. */
	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Data")
	TSoftObjectPtr<UDressUpBody> Body;

	// --- Levels ---

	/** Opened by the title screen's start button. */
	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Levels")
	TSoftObjectPtr<UWorld> GameLevel;

	/** Opened by the pause menu's "back to menu". */
	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Levels")
	TSoftObjectPtr<UWorld> MenuLevel;

	// --- Interface ---

	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Interface")
	TSoftClassPtr<UDressUpPanel> PanelClass;

	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Interface")
	TSoftClassPtr<UDressUpItemButton> ItemButtonClass;

	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Interface")
	TSoftClassPtr<UDressUpColorButton> ColorButtonClass;

	/** Text chips: wardrobe tabs, poses, scenes. */
	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Interface")
	TSoftClassPtr<UDressUpTabButton> TabButtonClass;

	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Interface")
	TSoftClassPtr<UDressUpPauseMenu> PauseMenuClass;

	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Interface")
	TSoftClassPtr<UDressUpFinalScreen> FinalScreenClass;

	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Interface")
	TSoftClassPtr<UDressUpMainMenu> MainMenuClass;

	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Interface")
	TSoftClassPtr<UDressUpNamePrompt> NamePromptClass;

	// --- Audio ---

	/** Looping background track. SourceAssets/Audio/music/SOURCE.txt says where it is from. */
	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Audio")
	TSoftObjectPtr<USoundBase> Music;

	/** Sound effects by name, as the code asks for them: UI_Click, UI_Tab, Top_On, Finish... */
	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Audio")
	TMap<FName, TSoftObjectPtr<USoundBase>> Sounds;

	/** Volume sliders: master scales the others. */
	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Audio")
	TSoftObjectPtr<USoundClass> MasterSoundClass;

	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Audio")
	TSoftObjectPtr<USoundClass> MusicSoundClass;

	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly, Category = "Audio")
	TSoftObjectPtr<USoundClass> EffectsSoundClass;
};
