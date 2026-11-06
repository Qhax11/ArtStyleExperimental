#include "DressUp/DressUpGameMode.h"

#include "Camera/CameraActor.h"
#include "DressUp/DressUpCharacter.h"
#include "DressUp/DressUpData.h"
#include "DressUp/DressUpFinal.h"
#include "DressUp/DressUpMenu.h"
#include "DressUp/DressUpSettings.h"
#include "DressUp/DressUpPanel.h"
#include "DressUp/OutfitComponent.h"
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
		UClass* LoadedClass = PauseMenuClass.LoadSynchronous();
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

	if (UClass* LoadedPanelClass = PanelClass.LoadSynchronous())
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
	UE_LOG(LogDressUpGame, Log, TEXT("Dress-up UI ready"));
}

void ADressUpPlayerController::PlayerTick(float DeltaTime)
{
	Super::PlayerTick(DeltaTime);
	UpdateRotation(DeltaTime);
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
	UClass* LoadedClass = FinalScreenClass.LoadSynchronous();
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
	}
}

void ADressUpMenuController::ShowMenu()
{
	if (TActorIterator<ACameraActor> Camera(GetWorld()); Camera)
	{
		SetViewTarget(*Camera);
	}
	if (UClass* LoadedClass = MenuClass.LoadSynchronous())
	{
		Menu = CreateWidget<UDressUpMainMenu>(this, LoadedClass);
		Menu->AddToViewport();
	}
	FInputModeUIOnly InputMode;
	InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
	SetInputMode(InputMode);
	SetShowMouseCursor(true);
}
