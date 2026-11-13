#include "DressUp/Game/DressUpGameMode.h"

#include "DressUp/Core/DressUpProjectSettings.h"

#include "Camera/CameraActor.h"
#include "DressUp/Character/DressUpCharacter.h"
#include "DressUp/Core/DressUpData.h"
#include "DressUp/UI/DressUpFinal.h"
#include "DressUp/UI/DressUpMenu.h"
#include "DressUp/Core/DressUpSettings.h"
#include "DressUp/UI/DressUpPanel.h"
#include "DressUp/Character/OutfitComponent.h"
#include "DressUp/Core/DressUpSound.h"
#include "EngineUtils.h"
#include "HAL/FileManager.h"
#include "Misc/DateTime.h"
#include "Misc/Paths.h"
#include "TimerManager.h"
#include "UnrealClient.h"

DEFINE_LOG_CATEGORY_STATIC(LogDressUpGame, Log, All);

ADressUpGameMode::ADressUpGameMode()
{
	PlayerControllerClass = ADressUpPlayerController::StaticClass();
	// The player never controls a body; the camera is a level actor.
	DefaultPawnClass = nullptr;
}

ADressUpPlayerController::ADressUpPlayerController()
{
	bShowMouseCursor = true;
}

void ADressUpPlayerController::BeginPlay()
{
	Super::BeginPlay();
	if (IsLocalController())
	{
		GetWorldTimerManager().SetTimerForNextTick(this, &ADressUpPlayerController::StartDressUp);
	}
	if (UDressUpSettingsSubsystem* SettingsSystem = UDressUpSettingsSubsystem::Get(this))
	{
		SettingsSystem->ApplyAudio(this);
		SettingsSystem->StartMusic(this);
	}
}

void ADressUpPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();
	// Escape stops play in the editor, so P opens the menu there too.
	for (const FKey& Key : {EKeys::Escape, EKeys::P})
	{
		FInputKeyBinding& Binding = InputComponent->BindKey(Key, IE_Pressed, this, &ADressUpPlayerController::TogglePauseMenu);
		Binding.bExecuteWhenPaused = true;
	}
}

void ADressUpPlayerController::TogglePauseMenu()
{
	if (NamePrompt && NamePrompt->GetVisibility() == ESlateVisibility::Visible)
	{
		NamePrompt->Close();
		return;
	}
	if (PauseMenu && PauseMenu->IsInViewport())
	{
		// Escape first closes the settings pop-up, then the menu.
		if (!PauseMenu->CloseSettings())
		{
			ClosePauseMenu();
		}
		return;
	}
	if (!PauseMenu)
	{
		UClass* LoadedClass = UDressUpProjectSettings::Get()->PauseMenuClass.LoadSynchronous();
		if (!LoadedClass)
		{
			return;
		}
		PauseMenu = CreateWidget<UDressUpPauseMenu>(this, LoadedClass);
	}
	PauseMenu->AddToViewport(10);
	SetPause(true);
}

void ADressUpPlayerController::ClosePauseMenu()
{
	if (PauseMenu)
	{
		PauseMenu->CloseSettings();
		PauseMenu->RemoveFromParent();
	}
	SetPause(false);
}

void ADressUpPlayerController::AskPlayerName()
{
	if (!NamePrompt)
	{
		NamePrompt = UDressUpNamePrompt::Create(this);
	}
	if (NamePrompt)
	{
		NamePrompt->Ask([WeakThis = TWeakObjectPtr<ADressUpPlayerController>(this)]()
		{
			const UDressUpSettingsSubsystem* SettingsSystem = WeakThis.IsValid() ? UDressUpSettingsSubsystem::Get(WeakThis.Get()) : nullptr;
			if (SettingsSystem && WeakThis->Panel)
			{
				WeakThis->Panel->SetPlayerName(SettingsSystem->GetPlayerName());
			}
		});
	}
}

void ADressUpPlayerController::DressUpForgetName()
{
	if (UDressUpSettingsSubsystem* SettingsSystem = UDressUpSettingsSubsystem::Get(this))
	{
		SettingsSystem->SetPlayerName(FString());
	}
	if (Panel)
	{
		Panel->SetPlayerName(FString());
	}
}

void ADressUpPlayerController::StartDressUp()
{
	UWorld* World = GetWorld();

	for (TActorIterator<ACameraActor> It(World); It; ++It)
	{
		if (It->ActorHasTag(FinalCameraTag))
		{
			FinalCamera = *It;
		}
		else if (!SceneCamera)
		{
			SceneCamera = *It;
		}
	}
	if (SceneCamera)
	{
		SetViewTarget(SceneCamera);
	}

	TActorIterator<ADressUpCharacter> CharacterIt(World);
	if (!CharacterIt)
	{
		UE_LOG(LogDressUpGame, Warning, TEXT("No ADressUpCharacter in the level"));
		return;
	}
	DressUpCharacter = *CharacterIt;
	DefaultRotation = DressUpCharacter->GetActorRotation();

	if (UClass* LoadedPanelClass = UDressUpProjectSettings::Get()->PanelClass.LoadSynchronous())
	{
		Panel = CreateWidget<UDressUpPanel>(this, LoadedPanelClass);
		Panel->Setup(DressUpCharacter->GetOutfit(), DressUpCharacter->GetCatalog());
		Panel->AddToViewport();

		// Game and UI: clicks on widgets stay in the UI, clicks on the scene reach the
		// controller so the character can be turned by dragging.
		FInputModeGameAndUI InputMode;
		InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
		InputMode.SetHideCursorDuringCapture(false);
		SetInputMode(InputMode);
	}
	SetShowMouseCursor(true);

	// The menu asks first; this covers starting the level directly, as in the editor.
	if (const UDressUpSettingsSubsystem* SettingsSystem = UDressUpSettingsSubsystem::Get(this))
	{
		if (!SettingsSystem->HasPlayerName())
		{
			AskPlayerName();
		}
		else if (Panel)
		{
			Panel->SetPlayerName(SettingsSystem->GetPlayerName());
		}
	}
	UE_LOG(LogDressUpGame, Log, TEXT("Dress-up UI ready"));
}

void ADressUpPlayerController::PlayerTick(float DeltaTime)
{
	Super::PlayerTick(DeltaTime);
	if (GalleryOutfits.IsEmpty())
	{
		UpdateRotation(DeltaTime);
	}
}

void ADressUpPlayerController::UpdateRotation(float DeltaTime)
{
	if (!DressUpCharacter)
	{
		return;
	}
	float MouseX = 0.0f;
	float MouseY = 0.0f;
	const bool bHasMouse = GetMousePosition(MouseX, MouseY);
	if (bHasMouse && IsInputKeyDown(EKeys::LeftMouseButton))
	{
		if (bDragging)
		{
			// Dragging right turns the character to its left, like spinning a turntable.
			DragYaw -= (MouseX - LastMouseX) * RotateDegreesPerPixel;
		}
		bDragging = true;
		LastMouseX = MouseX;
	}
	else
	{
		if (bDragging)
		{
			// Return by the shorter way round.
			DragYaw = FRotator::NormalizeAxis(DragYaw);
		}
		bDragging = false;
		DragYaw = FMath::FInterpTo(DragYaw, 0.0f, DeltaTime, ReturnSpeed);
	}
	DressUpCharacter->SetActorRotation(DefaultRotation + FRotator(0.0f, DragYaw, 0.0f));
}

void ADressUpPlayerController::Finish()
{
	if (bFinished || !DressUpCharacter)
	{
		return;
	}
	bFinished = true;
	DressUp::PlaySound(this, TEXT("Finish"));
	if (Panel)
	{
		Panel->SetVisibility(ESlateVisibility::Collapsed);
	}

	FDressUpFinalPose Pose;
	const UDressUpCatalog* Catalog = DressUpCharacter->GetCatalog();
	if (Catalog && Catalog->FinalPoses.Num() > 0)
	{
		Pose = Catalog->FinalPoses[FMath::RandRange(0, Catalog->FinalPoses.Num() - 1)];
	}
	else if (const UDressUpBody* BodyData = DressUpCharacter->GetBody())
	{
		Pose.Anim = BodyData->FinalPose;
	}
	DressUpCharacter->PlayFinalPose(Pose);

	if (FinalCamera)
	{
		SetViewTargetWithBlend(FinalCamera, CameraBlendTime, VTBlend_EaseInOut, 2.0f);
	}
	GetWorldTimerManager().SetTimer(MessageTimer, this, &ADressUpPlayerController::ShowFinalScreen, MessageDelay, false);
}

void ADressUpPlayerController::ShowFinalScreen()
{
	UClass* LoadedClass = UDressUpProjectSettings::Get()->FinalScreenClass.LoadSynchronous();
	if (!bFinished || !LoadedClass)
	{
		return;
	}
	const FText Message = DressUp::PickMessage(DressUpCharacter->GetCatalog(), DressUpCharacter->GetOutfit());
	FinalScreen = CreateWidget<UDressUpFinalScreen>(this, LoadedClass);
	FinalScreen->Setup(Message, this);
	FinalScreen->AddToViewport(1);
}

FString ADressUpPlayerController::PhotoDirectory()
{
	const FString Profile = FPlatformMisc::GetEnvironmentVariable(TEXT("USERPROFILE"));
	if (!Profile.IsEmpty())
	{
		return FPaths::Combine(Profile, TEXT("Pictures"), TEXT("Dolap"));
	}
	return FPaths::Combine(FPaths::ScreenShotDir(), TEXT("Dolap"));
}

void ADressUpPlayerController::TakePhoto()
{
	DressUp::PlaySound(this, TEXT("Photo"));
	const FString Directory = PhotoDirectory();
	IFileManager::Get().MakeDirectory(*Directory, true);
	const FString Name = FString::Printf(TEXT("Dolap_%s.png"), *FDateTime::Now().ToString(TEXT("%Y%m%d_%H%M%S")));
	const FString Path = FPaths::Combine(Directory, Name);

	// Without UI: the photo shows only the character and the scene.
	FScreenshotRequest::RequestScreenshot(Path, false, false);
	UE_LOG(LogDressUpGame, Log, TEXT("Photo requested: %s"), *Path);
	if (FinalScreen)
	{
		FinalScreen->ShowStatus(FText::Format(NSLOCTEXT("DressUp", "PhotoSaved", "Fotoğraf kaydedildi: {0}"), FText::FromString(FPaths::ConvertRelativePathToFull(Path))));
	}
}

void ADressUpPlayerController::Replay()
{
	GetWorldTimerManager().ClearTimer(MessageTimer);
	if (FinalScreen)
	{
		FinalScreen->RemoveFromParent();
		FinalScreen = nullptr;
	}
	if (DressUpCharacter)
	{
		DressUpCharacter->ReturnToIdle();
		DressUpCharacter->GetOutfit()->ResetToDefault();
	}
	if (SceneCamera)
	{
		SetViewTargetWithBlend(SceneCamera, CameraBlendTime, VTBlend_EaseInOut, 2.0f);
	}
	if (Panel)
	{
		Panel->SetVisibility(ESlateVisibility::SelfHitTestInvisible);
	}
	bFinished = false;
}

// --- Main menu level ---

ADressUpMenuGameMode::ADressUpMenuGameMode()
{
	PlayerControllerClass = ADressUpMenuController::StaticClass();
	DefaultPawnClass = nullptr;
}

ADressUpMenuController::ADressUpMenuController()
{
	bShowMouseCursor = true;
}

void ADressUpMenuController::BeginPlay()
{
	Super::BeginPlay();
	if (IsLocalController())
	{
		GetWorldTimerManager().SetTimerForNextTick(this, &ADressUpMenuController::ShowMenu);
	}
	if (UDressUpSettingsSubsystem* SettingsSystem = UDressUpSettingsSubsystem::Get(this))
	{
		SettingsSystem->ApplyAudio(this);
		SettingsSystem->StartMusic(this);
	}
}

void ADressUpMenuController::ShowMenu()
{
	if (TActorIterator<ACameraActor> Camera(GetWorld()); Camera)
	{
		SetViewTarget(*Camera);
	}
	if (UClass* LoadedClass = UDressUpProjectSettings::Get()->MainMenuClass.LoadSynchronous())
	{
		Menu = CreateWidget<UDressUpMainMenu>(this, LoadedClass);
		Menu->AddToViewport();
	}
	FInputModeUIOnly InputMode;
	InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
	SetInputMode(InputMode);
	SetShowMouseCursor(true);
}

void ADressUpPlayerController::DressUpWear(const FString& Items)
{
	if (!DressUpCharacter)
	{
		return;
	}
	UOutfitComponent* Outfit = DressUpCharacter->GetOutfit();
	const UDressUpCatalog* Catalog = DressUpCharacter->GetCatalog();
	if (!Outfit || !Catalog)
	{
		return;
	}
	TArray<FString> Names;
	Items.ParseIntoArrayWS(Names);
	Outfit->ApplyOutfit(FDressUpOutfit());
	bool bShowPanel = true;
	for (const FString& Entry : Names)
	{
		if (Entry.Equals(TEXT("nopanel"), ESearchCase::IgnoreCase))
		{
			bShowPanel = false;
			continue;
		}
		if (Entry.StartsWith(TEXT("tint=")))
		{
			const int32 PaletteIndex = FCString::Atoi(*Entry.Mid(5));
			if (Catalog->Palette.IsValidIndex(PaletteIndex))
			{
				Outfit->SetColorForLastSlot(Catalog->Palette[PaletteIndex]);
			}
			continue;
		}
		FString Name = Entry;
		FString VariantText;
		Entry.Split(TEXT(":"), &Name, &VariantText);
		const TObjectPtr<UDressUpItem>* Found = Catalog->AllItems.FindByPredicate([&Name](const UDressUpItem* Item)
		{
			return Item && Item->GetName() == Name;
		});
		if (!Found)
		{
			UE_LOG(LogDressUpGame, Warning, TEXT("DressUpWear: no item %s"), *Name);
			continue;
		}
		Outfit->Equip(*Found);
		if (!VariantText.IsEmpty())
		{
			Outfit->SetSlotVariant((*Found)->Slot, FCString::Atoi(*VariantText));
		}
	}
	if (Panel)
	{
		Panel->SetVisibility(bShowPanel ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
	}
}

void ADressUpPlayerController::DressUpGallery()
{
	const UDressUpCatalog* Catalog = DressUpCharacter ? DressUpCharacter->GetCatalog() : nullptr;
	if (!Catalog)
	{
		return;
	}
	// Items per slot, in catalog order. Dresses get their own outfits, as they block top and bottom.
	TMap<EDressUpSlot, TArray<UDressUpItem*>> BySlot;
	for (UDressUpItem* Item : Catalog->AllItems)
	{
		if (Item)
		{
			BySlot.FindOrAdd(Item->Slot).Add(Item);
		}
	}
	auto Build = [&BySlot](const TArray<EDressUpSlot>& Driving, const TArray<EDressUpSlot>& Riding, TArray<TArray<TObjectPtr<UDressUpItem>>>& Out)
	{
		int32 Count = 0;
		for (EDressUpSlot Slot : Driving)
		{
			Count = FMath::Max(Count, BySlot.FindOrAdd(Slot).Num());
		}
		for (int32 Index = 0; Index < Count; ++Index)
		{
			TArray<TObjectPtr<UDressUpItem>>& Outfit = Out.AddDefaulted_GetRef();
			for (EDressUpSlot Slot : Driving)
			{
				const TArray<UDressUpItem*>& Items = BySlot.FindOrAdd(Slot);
				if (Items.IsValidIndex(Index))
				{
					Outfit.Add(Items[Index]);
				}
			}
			for (EDressUpSlot Slot : Riding)
			{
				const TArray<UDressUpItem*>& Items = BySlot.FindOrAdd(Slot);
				if (Items.Num() > 0)
				{
					Outfit.Add(Items[Index % Items.Num()]);
				}
			}
		}
	};
	GalleryOutfits.Reset();
	Build({EDressUpSlot::Top, EDressUpSlot::Bottom, EDressUpSlot::Shoes, EDressUpSlot::Necklace, EDressUpSlot::Gloves, EDressUpSlot::Hair, EDressUpSlot::Socks},
		{}, GalleryOutfits);
	Build({EDressUpSlot::Dress, EDressUpSlot::Glasses, EDressUpSlot::Hat}, {EDressUpSlot::Shoes, EDressUpSlot::Hair}, GalleryOutfits);
	GalleryIndex = 0;
	if (Panel)
	{
		Panel->SetVisibility(ESlateVisibility::Collapsed);
	}
	UE_LOG(LogDressUpGame, Log, TEXT("GALLERY start: %d outfits"), GalleryOutfits.Num());
	GalleryStep();
}

void ADressUpPlayerController::GalleryStep()
{
	if (!DressUpCharacter || !GalleryOutfits.IsValidIndex(GalleryIndex))
	{
		UE_LOG(LogDressUpGame, Log, TEXT("GALLERY done"));
		GalleryOutfits.Reset();
		if (Panel)
		{
			Panel->SetVisibility(ESlateVisibility::Visible);
		}
		return;
	}
	UOutfitComponent* Outfit = DressUpCharacter->GetOutfit();
	Outfit->ApplyOutfit(FDressUpOutfit());
	FString Names;
	for (UDressUpItem* Item : GalleryOutfits[GalleryIndex])
	{
		Outfit->Equip(Item);
		Names += Item->GetName() + TEXT(" ");
	}
	UE_LOG(LogDressUpGame, Log, TEXT("GALLERY %d: %s"), GalleryIndex, *Names);
	DressUpCharacter->SetActorRotation(DefaultRotation);

	const FString Directory = FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("Gallery"));
	IFileManager::Get().MakeDirectory(*Directory, true);
	const int32 Index = GalleryIndex;
	FTimerDelegate Front = FTimerDelegate::CreateWeakLambda(this, [this, Directory, Index]()
	{
		FScreenshotRequest::RequestScreenshot(FPaths::Combine(Directory, FString::Printf(TEXT("G%03d_front.png"), Index)), false, false);
		FTimerDelegate Back = FTimerDelegate::CreateWeakLambda(this, [this, Directory, Index]()
		{
			if (DressUpCharacter)
			{
				DressUpCharacter->SetActorRotation(DefaultRotation + FRotator(0.0f, 180.0f, 0.0f));
			}
			FTimerDelegate Shot = FTimerDelegate::CreateWeakLambda(this, [this, Directory, Index]()
			{
				FScreenshotRequest::RequestScreenshot(FPaths::Combine(Directory, FString::Printf(TEXT("G%03d_back.png"), Index)), false, false);
				++GalleryIndex;
				GetWorldTimerManager().SetTimer(GalleryTimer, this, &ADressUpPlayerController::GalleryStep, 0.3f, false);
			});
			GetWorldTimerManager().SetTimer(GalleryTimer, Shot, 0.4f, false);
		});
		GetWorldTimerManager().SetTimer(GalleryTimer, Back, 0.3f, false);
	});
	GetWorldTimerManager().SetTimer(GalleryTimer, Front, 0.8f, false);
}
