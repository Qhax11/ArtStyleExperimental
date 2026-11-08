#include "DressUp/DressUpMenu.h"

#include "Components/Button.h"
#include "Components/CheckBox.h"
#include "Components/EditableTextBox.h"
#include "Components/Slider.h"
#include "Components/TextBlock.h"
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

// --- Name prompt ---

UDressUpNamePrompt* UDressUpNamePrompt::Create(APlayerController* Owner)
{
	const TSoftClassPtr<UDressUpNamePrompt> PromptClass(FSoftObjectPath(TEXT("/Game/DressUp/UI/WBP_NamePrompt.WBP_NamePrompt_C")));
	UClass* LoadedClass = PromptClass.LoadSynchronous();
	if (!Owner || !LoadedClass)
	{
		return nullptr;
	}
	UDressUpNamePrompt* Prompt = CreateWidget<UDressUpNamePrompt>(Owner, LoadedClass);
	Prompt->AddToViewport(20);
	return Prompt;
}

void UDressUpNamePrompt::NativeConstruct()
{
	Super::NativeConstruct();
	NameInput->OnTextChanged.AddUniqueDynamic(this, &UDressUpNamePrompt::HandleTextChanged);
	NameInput->OnTextCommitted.AddUniqueDynamic(this, &UDressUpNamePrompt::HandleTextCommitted);
	ConfirmBtn->OnClicked.AddUniqueDynamic(this, &UDressUpNamePrompt::HandleConfirm);
}

void UDressUpNamePrompt::Ask(TFunction<void()> InOnConfirmed)
{
	OnConfirmed = MoveTemp(InOnConfirmed);
	const UDressUpSettingsSubsystem* SettingsSystem = UDressUpSettingsSubsystem::Get(this);
	const FText Current = FText::FromString(SettingsSystem ? SettingsSystem->GetPlayerName() : FString());
	NameInput->SetText(Current);
	HandleTextChanged(Current);
	Open();
	NameInput->SetKeyboardFocus();
}

void UDressUpNamePrompt::HandleTextChanged(const FText& Text)
{
	const FString Name = Text.ToString();
	if (Name.Len() > MaxNameLength)
	{
		NameInput->SetText(FText::FromString(Name.Left(MaxNameLength)));
	}
	ConfirmBtn->SetIsEnabled(!Name.TrimStartAndEnd().IsEmpty());
}

void UDressUpNamePrompt::HandleTextCommitted(const FText& Text, ETextCommit::Type CommitType)
{
	if (CommitType == ETextCommit::OnEnter)
	{
		HandleConfirm();
	}
}

void UDressUpNamePrompt::HandleConfirm()
{
	const FString Name = NameInput->GetText().ToString().TrimStartAndEnd();
	if (Name.IsEmpty())
	{
		return;
	}
	if (UDressUpSettingsSubsystem* SettingsSystem = UDressUpSettingsSubsystem::Get(this))
	{
		SettingsSystem->SetPlayerName(Name);
	}
	Close();
	if (OnConfirmed)
	{
		OnConfirmed();
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
	const UDressUpSettingsSubsystem* SettingsSystem = UDressUpSettingsSubsystem::Get(this);
	if (SettingsSystem && SettingsSystem->HasPlayerName())
	{
		OpenGame();
		return;
	}
	if (!NamePrompt)
	{
		NamePrompt = UDressUpNamePrompt::Create(GetOwningPlayer());
	}
	if (!NamePrompt)
	{
		OpenGame();
		return;
	}
	Settings->Close();
	Credits->Close();
	NamePrompt->Ask([WeakThis = TWeakObjectPtr<UDressUpMainMenu>(this)]()
	{
		if (WeakThis.IsValid())
		{
			WeakThis->OpenGame();
		}
	});
}

void UDressUpMainMenu::OpenGame()
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
	if (NameBtn)
	{
		NameBtn->OnClicked.AddUniqueDynamic(this, &UDressUpPauseMenu::HandleChangeName);
	}
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

void UDressUpPauseMenu::HandleChangeName()
{
	if (ADressUpPlayerController* Controller = Cast<ADressUpPlayerController>(GetOwningPlayer()))
	{
		Controller->AskPlayerName();
	}
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
