// Game mode and player controller for the dress-up level: fixed camera, mouse, UI.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/PlayerController.h"
#include "DressUpGameMode.generated.h"

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

	UFUNCTION(BlueprintPure, Category = "Dress Up")
	UDressUpPanel* GetPanel() const { return Panel; }

protected:
	virtual void BeginPlay() override;

private:
	/** Runs one tick after BeginPlay so the character has finished its own setup. */
	void StartDressUp();

	UPROPERTY()
	TObjectPtr<UDressUpPanel> Panel;
};
