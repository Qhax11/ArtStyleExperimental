// Main menu, pause menu and their pop-ups (settings, credits). Layout lives in Widget Blueprints.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "DressUpMenu.generated.h"

class UButton;
class UCheckBox;
class UEditableTextBox;
class USlider;
class UTextBlock;

/** A pop-up card with a close button. The credits card is just this, its text set in the designer. */
UCLASS(Abstract)
class ARTSTYLEEXPERIMENTAL_API UDressUpPopup : public UUserWidget
{
	GENERATED_BODY()

public:
	void Open();
	void Close();

protected:
	virtual void NativeConstruct() override;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> CloseBtn;

private:
	UFUNCTION()
	void HandleClose();
};

/** Volume sliders and the fullscreen box. Changes are applied and saved at once. */
UCLASS(Abstract)
class ARTSTYLEEXPERIMENTAL_API UDressUpSettingsPanel : public UDressUpPopup
{
	GENERATED_BODY()

protected:
	virtual void NativeConstruct() override;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<USlider> MasterSlider;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<USlider> MusicSlider;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<USlider> EffectsSlider;

	UPROPERTY(meta = (BindWidgetOptional))
	TObjectPtr<UCheckBox> FullscreenCheck;

private:
	UFUNCTION()
	void HandleMaster(float Value);

	UFUNCTION()
	void HandleMusic(float Value);

	UFUNCTION()
	void HandleEffects(float Value);

	UFUNCTION()
	void HandleFullscreen(bool bChecked);
};

/** Asks for the player's name. Saves it when confirmed; the close button leaves it as it was. */
UCLASS(Abstract)
class ARTSTYLEEXPERIMENTAL_API UDressUpNamePrompt : public UDressUpPopup
{
	GENERATED_BODY()

public:
	/** Creates the prompt and adds it to the viewport, above the menus. */
	static UDressUpNamePrompt* Create(APlayerController* Owner);

	/** Opens with the current name filled in. OnConfirmed runs after a new name is saved. */
	void Ask(TFunction<void()> InOnConfirmed);

	static constexpr int32 MaxNameLength = 20;

protected:
	virtual void NativeConstruct() override;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UEditableTextBox> NameInput;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> ConfirmBtn;

private:
	UFUNCTION()
	void HandleTextChanged(const FText& Text);

	UFUNCTION()
	void HandleTextCommitted(const FText& Text, ETextCommit::Type CommitType);

	UFUNCTION()
	void HandleConfirm();

	TFunction<void()> OnConfirmed;
};

/** The name floating above the character's head. */
UCLASS(Abstract)
class ARTSTYLEEXPERIMENTAL_API UDressUpNameTag : public UUserWidget
{
	GENERATED_BODY()

public:
	void SetName(const FString& Name);

protected:
	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UTextBlock> NameText;
};

/** The title screen: start, settings, credits, quit. The pop-ups are child widgets, hidden at start. */
UCLASS(Abstract)
class ARTSTYLEEXPERIMENTAL_API UDressUpMainMenu : public UUserWidget
{
	GENERATED_BODY()

public:
	/** Level opened by the start button. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Menu")
	TSoftObjectPtr<UWorld> GameLevel = TSoftObjectPtr<UWorld>(FSoftObjectPath(TEXT("/Game/DressUp/Maps/LVL_DressUp.LVL_DressUp")));

protected:
	virtual void NativeConstruct() override;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> StartBtn;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> SettingsBtn;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> CreditsBtn;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> QuitBtn;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UDressUpPopup> Settings;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UDressUpPopup> Credits;

private:
	UFUNCTION()
	void HandleStart();

	UFUNCTION()
	void HandleSettings();

	UFUNCTION()
	void HandleCredits();

	void OpenGame();

	UPROPERTY()
	TObjectPtr<UDressUpNamePrompt> NamePrompt;

	UFUNCTION()
	void HandleQuit();
};

/** The in-game pause card, opened with Escape. */
UCLASS(Abstract)
class ARTSTYLEEXPERIMENTAL_API UDressUpPauseMenu : public UUserWidget
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Menu")
	TSoftObjectPtr<UWorld> MenuLevel = TSoftObjectPtr<UWorld>(FSoftObjectPath(TEXT("/Game/DressUp/Maps/LVL_MainMenu.LVL_MainMenu")));

	/** Closes the settings pop-up if it is open. Returns true when it was. */
	bool CloseSettings();

protected:
	virtual void NativeConstruct() override;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> ResumeBtn;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> SettingsBtn;

	UPROPERTY(meta = (BindWidgetOptional))
	TObjectPtr<UButton> NameBtn;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> MainMenuBtn;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> QuitBtn;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UDressUpPopup> Settings;

private:
	UFUNCTION()
	void HandleResume();

	UFUNCTION()
	void HandleSettings();

	UFUNCTION()
	void HandleChangeName();

	UFUNCTION()
	void HandleMainMenu();

	UFUNCTION()
	void HandleQuit();
};
