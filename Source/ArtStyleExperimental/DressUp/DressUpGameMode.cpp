#include "DressUp/DressUpGameMode.h"

#include "Camera/CameraActor.h"
#include "DressUp/DressUpCharacter.h"
#include "DressUp/DressUpData.h"
#include "DressUp/DressUpFinal.h"
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

	if (UClass* LoadedPanelClass = PanelClass.LoadSynchronous())
	{
		Panel = CreateWidget<UDressUpPanel>(this, LoadedPanelClass);
		Panel->Setup(DressUpCharacter->GetOutfit(), DressUpCharacter->GetCatalog());
		Panel->AddToViewport();

		// The panel itself is not focusable; buttons take focus when clicked.
		FInputModeUIOnly InputMode;
		InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
		SetInputMode(InputMode);
	}
	SetShowMouseCursor(true);
	UE_LOG(LogDressUpGame, Log, TEXT("Dress-up UI ready"));
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
