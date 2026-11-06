#include "DressUp/DressUpGameMode.h"

#include "Camera/CameraActor.h"
#include "DressUp/DressUpCharacter.h"
#include "DressUp/DressUpPanel.h"
#include "EngineUtils.h"
#include "TimerManager.h"

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

	TActorIterator<ACameraActor> SceneCamera(World);
	if (SceneCamera)
	{
		SetViewTarget(*SceneCamera);
	}

	TActorIterator<ADressUpCharacter> DressUpCharacter(World);
	if (!DressUpCharacter)
	{
		UE_LOG(LogDressUpGame, Warning, TEXT("No ADressUpCharacter in the level"));
		return;
	}

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
