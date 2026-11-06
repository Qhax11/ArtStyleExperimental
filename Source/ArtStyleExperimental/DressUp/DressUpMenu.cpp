#include "DressUp/DressUpMenu.h"

#include "Components/Button.h"
#include "Components/CheckBox.h"
#include "Components/Slider.h"
#include "DressUp/DressUpGameMode.h"
#include "DressUp/DressUpSettings.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"

namespace
{
	void QuitGame(UUserWidget* Widget)
	{
		UKismetSystemLibrary::QuitGame(Widget, Widget->GetOwningPlayer(), EQuitPreference::Quit, false);
	}
}

// --- Pop-up ---

void UDressUpPopup::NativeConstruct()
{
	Super::NativeConstruct();
	CloseBtn->OnClicked.AddUniqueDynamic(this, &UDressUpPopup::HandleClose);
}

void UDressUpPopup::Open()
{
	SetVisibility(ESlateVisibility::Visible);
}

void UDressUpPopup::Close()
{
	SetVisibility(ESlateVisibility::Collapsed);
}

void UDressUpPopup::HandleClose()
{
	Close();
}

// --- Settings ---

void UDressUpSettingsPanel::NativeConstruct()
{
	Super::NativeConstruct();
	if (const UDressUpSettingsSubsystem* SettingsSystem = UDressUpSettingsSubsystem::Get(this))
	{
		MasterSlider->SetValue(SettingsSystem->GetVolume(EDressUpVolume::Master));
		MusicSlider->SetValue(SettingsSystem->GetVolume(EDressUpVolume::Music));
		EffectsSlider->SetValue(SettingsSystem->GetVolume(EDressUpVolume::Effects));
		if (FullscreenCheck)
		{
			FullscreenCheck->SetIsChecked(SettingsSystem->IsFullscreen());
		}
	}
	MasterSlider->OnValueChanged.AddUniqueDynamic(this, &UDressUpSettingsPanel::HandleMaster);
	MusicSlider->OnValueChanged.AddUniqueDynamic(this, &UDressUpSettingsPanel::HandleMusic);
	EffectsSlider->OnValueChanged.AddUniqueDynamic(this, &UDressUpSettingsPanel::HandleEffects);
	if (FullscreenCheck)
	{
		FullscreenCheck->OnCheckStateChanged.AddUniqueDynamic(this, &UDressUpSettingsPanel::HandleFullscreen);
	}
}

void UDressUpSettingsPanel::HandleMaster(float Value)
{
	if (UDressUpSettingsSubsystem* SettingsSystem = UDressUpSettingsSubsystem::Get(this))
	{
		SettingsSystem->SetVolume(EDressUpVolume::Master, Value);
	}
}

void UDressUpSettingsPanel::HandleMusic(float Value)
{
	if (UDressUpSettingsSubsystem* SettingsSystem = UDressUpSettingsSubsystem::Get(this))
	{
		SettingsSystem->SetVolume(EDressUpVolume::Music, Value);
	}
}

void UDressUpSettingsPanel::HandleEffects(float Value)
{
	if (UDressUpSettingsSubsystem* SettingsSystem = UDressUpSettingsSubsystem::Get(this))
	{
		SettingsSystem->SetVolume(EDressUpVolume::Effects, Value);
	}
}

void UDressUpSettingsPanel::HandleFullscreen(bool bChecked)
{
	if (UDressUpSettingsSubsystem* SettingsSystem = UDressUpSettingsSubsystem::Get(this))
	{
		SettingsSystem->SetFullscreen(bChecked);
	}
}

// --- Main menu ---

void UDressUpMainMenu::NativeConstruct()
{
	Super::NativeConstruct();
	StartBtn->OnClicked.AddUniqueDynamic(this, &UDressUpMainMenu::HandleStart);
	SettingsBtn->OnClicked.AddUniqueDynamic(this, &UDressUpMainMenu::HandleSettings);
	CreditsBtn->OnClicked.AddUniqueDynamic(this, &UDressUpMainMenu::HandleCredits);
	QuitBtn->OnClicked.AddUniqueDynamic(this, &UDressUpMainMenu::HandleQuit);
	Settings->Close();
	Credits->Close();
}

void UDressUpMainMenu::HandleStart()
{
	UGameplayStatics::OpenLevelBySoftObjectPtr(this, GameLevel);
}

void UDressUpMainMenu::HandleSettings()
{
	Credits->Close();
	Settings->Open();
}

void UDressUpMainMenu::HandleCredits()
{
	Settings->Close();
	Credits->Open();
}

void UDressUpMainMenu::HandleQuit()
{
	QuitGame(this);
}

// --- Pause menu ---

void UDressUpPauseMenu::NativeConstruct()
{
	Super::NativeConstruct();
	ResumeBtn->OnClicked.AddUniqueDynamic(this, &UDressUpPauseMenu::HandleResume);
	SettingsBtn->OnClicked.AddUniqueDynamic(this, &UDressUpPauseMenu::HandleSettings);
	MainMenuBtn->OnClicked.AddUniqueDynamic(this, &UDressUpPauseMenu::HandleMainMenu);
	QuitBtn->OnClicked.AddUniqueDynamic(this, &UDressUpPauseMenu::HandleQuit);
	Settings->Close();
}

bool UDressUpPauseMenu::CloseSettings()
{
	if (Settings && Settings->GetVisibility() == ESlateVisibility::Visible)
	{
		Settings->Close();
		return true;
	}
	return false;
}

void UDressUpPauseMenu::HandleResume()
{
	if (ADressUpPlayerController* Controller = Cast<ADressUpPlayerController>(GetOwningPlayer()))
	{
		Controller->ClosePauseMenu();
	}
}

void UDressUpPauseMenu::HandleSettings()
{
	Settings->Open();
}

void UDressUpPauseMenu::HandleMainMenu()
{
	if (APlayerController* Controller = GetOwningPlayer())
	{
		Controller->SetPause(false);
	}
	UGameplayStatics::OpenLevelBySoftObjectPtr(this, MenuLevel);
}

void UDressUpPauseMenu::HandleQuit()
{
	QuitGame(this);
}
