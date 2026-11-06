// Game mode and player controller for the dress-up level: fixed camera, mouse, UI, finale.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/PlayerController.h"
#include "DressUpGameMode.generated.h"

class ACameraActor;
class ADressUpCharacter;
class UDressUpFinalScreen;
class UDressUpPanel;

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
	TSoftClassPtr<UDressUpFinalScreen> FinalScreenClass = TSoftClassPtr<UDressUpFinalScreen>(FSoftObjectPath(TEXT("/Game/DressUp/UI/WBP_Final.WBP_Final_C")));

	/** Camera actors with this tag frame the finale. Without one the scene camera stays. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	FName FinalCameraTag = TEXT("FinalCamera");

	/** Seconds between pressing Finish and the message appearing. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	float MessageDelay = 2.0f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	float CameraBlendTime = 1.2f;

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

	/** Console shortcuts for testing the finale. */
	UFUNCTION(Exec)
	void DressUpFinish() { Finish(); }

	UFUNCTION(Exec)
	void DressUpPhoto() { TakePhoto(); }

	UFUNCTION(Exec)
	void DressUpReplay() { Replay(); }

protected:
	virtual void BeginPlay() override;

private:
	/** Runs one tick after BeginPlay so the character has finished its own setup. */
	void StartDressUp();

	void ShowFinalScreen();

	static FString PhotoDirectory();

	UPROPERTY()
	TObjectPtr<UDressUpPanel> Panel;

	UPROPERTY()
	TObjectPtr<UDressUpFinalScreen> FinalScreen;

	UPROPERTY()
	TObjectPtr<ADressUpCharacter> DressUpCharacter;

	UPROPERTY()
	TObjectPtr<ACameraActor> SceneCamera;

	UPROPERTY()
	TObjectPtr<ACameraActor> FinalCamera;

	FTimerHandle MessageTimer;
	bool bFinished = false;
};
