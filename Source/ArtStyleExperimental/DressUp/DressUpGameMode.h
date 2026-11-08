// Game mode and player controller for the dress-up level: fixed camera, mouse, UI, finale.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/PlayerController.h"
#include "DressUpGameMode.generated.h"

class ACameraActor;
class UDressUpItem;
class ADressUpCharacter;
class UDressUpFinalScreen;
class UDressUpMainMenu;
class UDressUpPanel;
class UDressUpPauseMenu;

UCLASS()
class ARTSTYLEEXPERIMENTAL_API ADressUpGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	ADressUpGameMode();
};

UCLASS()
class ARTSTYLEEXPERIMENTAL_API ADressUpPlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	ADressUpPlayerController();

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	TSoftClassPtr<UDressUpPanel> PanelClass = TSoftClassPtr<UDressUpPanel>(FSoftObjectPath(TEXT("/Game/DressUp/UI/WBP_DressUp.WBP_DressUp_C")));

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	TSoftClassPtr<UDressUpPauseMenu> PauseMenuClass = TSoftClassPtr<UDressUpPauseMenu>(FSoftObjectPath(TEXT("/Game/DressUp/UI/WBP_Pause.WBP_Pause_C")));

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	TSoftClassPtr<UDressUpFinalScreen> FinalScreenClass = TSoftClassPtr<UDressUpFinalScreen>(FSoftObjectPath(TEXT("/Game/DressUp/UI/WBP_Final.WBP_Final_C")));

	/** Camera actors with this tag frame the finale. Without one the scene camera stays. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	FName FinalCameraTag = TEXT("FinalCamera");

	/** Seconds between pressing Finish and the message appearing. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	float MessageDelay = 2.0f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	float CameraBlendTime = 1.2f;

	/** Degrees the character turns per pixel of horizontal mouse drag on the scene. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up|Rotate")
	float RotateDegreesPerPixel = 0.4f;

	/** How quickly the character turns back to face the camera after the mouse is released. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up|Rotate")
	float ReturnSpeed = 5.0f;

	UFUNCTION(BlueprintPure, Category = "Dress Up")
	UDressUpPanel* GetPanel() const { return Panel; }

	/** Hides the wardrobe, plays a final pose, moves the camera in and shows the message. */
	UFUNCTION(BlueprintCallable, Category = "Dress Up")
	void Finish();

	/** Saves the current frame, without UI, to the Pictures/Dolap folder. */
	UFUNCTION(BlueprintCallable, Category = "Dress Up")
	void TakePhoto();

	/** Back to the wardrobe with the starting outfit. */
	UFUNCTION(BlueprintCallable, Category = "Dress Up")
	void Replay();

	/** Opens the pause menu, or closes it (and its settings pop-up first). Bound to Escape, and P for the editor. */
	UFUNCTION(BlueprintCallable, Category = "Dress Up")
	void TogglePauseMenu();

	UFUNCTION(BlueprintCallable, Category = "Dress Up")
	void ClosePauseMenu();

	/** Console shortcuts for testing the finale. */
	UFUNCTION(Exec)
	void DressUpFinish() { Finish(); }

	UFUNCTION(Exec)
	void DressUpPhoto() { TakePhoto(); }

	UFUNCTION(Exec)
	void DressUpReplay() { Replay(); }

	/**
	 * Test shortcut: takes everything off and puts on the named items, e.g.
	 * "DressUpWear DA_Top_001 tint=3 DA_Bottom_004:2" (":N" picks variant N, "tint=N" tints the
	 * item before it with palette colour N). "nopanel" hides the wardrobe for clean screenshots.
	 */
	UFUNCTION(Exec)
	void DressUpWear(const FString& Items);

	/**
	 * Test shortcut: puts every catalog item on in turn (one item per slot per outfit, so many
	 * at once) and saves a front and a back photo of each outfit to Saved/Gallery.
	 * The outfits are listed in the log as "GALLERY <n>: <items>".
	 */
	UFUNCTION(Exec)
	void DressUpGallery();

protected:
	virtual void BeginPlay() override;
	virtual void SetupInputComponent() override;
	virtual void PlayerTick(float DeltaTime) override;

private:
	/** Runs one tick after BeginPlay so the character has finished its own setup. */
	void StartDressUp();

	void ShowFinalScreen();

	static FString PhotoDirectory();

	/** One gallery step: dress, then photograph front and back on timers. */
	void GalleryStep();

	TArray<TArray<TObjectPtr<UDressUpItem>>> GalleryOutfits;
	int32 GalleryIndex = 0;
	FTimerHandle GalleryTimer;

	/** Turns the character while the left mouse button drags on the scene, and eases it back when released. */
	void UpdateRotation(float DeltaTime);

	UPROPERTY()
	TObjectPtr<UDressUpPanel> Panel;

	UPROPERTY()
	TObjectPtr<UDressUpFinalScreen> FinalScreen;

	UPROPERTY()
	TObjectPtr<UDressUpPauseMenu> PauseMenu;

	UPROPERTY()
	TObjectPtr<ADressUpCharacter> DressUpCharacter;

	UPROPERTY()
	TObjectPtr<ACameraActor> SceneCamera;

	UPROPERTY()
	TObjectPtr<ACameraActor> FinalCamera;

	FTimerHandle MessageTimer;
	bool bFinished = false;

	/** The character's facing when the game starts: towards the camera. */
	FRotator DefaultRotation = FRotator::ZeroRotator;

	/** Yaw added by dragging, in degrees. Eases back to zero after release. */
	float DragYaw = 0.0f;
	float LastMouseX = 0.0f;
	bool bDragging = false;
};

/** Game mode of the title screen level. */
UCLASS()
class ARTSTYLEEXPERIMENTAL_API ADressUpMenuGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	ADressUpMenuGameMode();
};

/** Shows the main menu over the level camera. */
UCLASS()
class ARTSTYLEEXPERIMENTAL_API ADressUpMenuController : public APlayerController
{
	GENERATED_BODY()

public:
	ADressUpMenuController();

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Menu")
	TSoftClassPtr<UDressUpMainMenu> MenuClass = TSoftClassPtr<UDressUpMainMenu>(FSoftObjectPath(TEXT("/Game/DressUp/UI/WBP_Menu.WBP_Menu_C")));

protected:
	virtual void BeginPlay() override;

private:
	void ShowMenu();

	UPROPERTY()
	TObjectPtr<UDressUpMainMenu> Menu;
};
