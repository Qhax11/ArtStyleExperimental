// Base of the actors that show a part of the current scene.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DressUpSceneActor.generated.h"

class UDressUpScene;

/**
 * Place one in the level for each part of the set (backdrop, ground, a prop slot, the effect,
 * the light rig). In play it follows UDressUpSceneSubsystem; in the editor it shows
 * PreviewScene, so the set can be arranged while seeing a real scene.
 */
UCLASS(Abstract)
class ARTSTYLEEXPERIMENTAL_API ADressUpSceneActor : public AActor
{
	GENERATED_BODY()

public:
	ADressUpSceneActor();

	/** Shown in the editor only. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Scene")
	TObjectPtr<UDressUpScene> PreviewScene;

protected:
	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	/** Shows this actor's part of Scene. Scene may be null: then show nothing. */
	virtual void ApplyScene(const UDressUpScene* Scene) {}

	/** For Blueprint subclasses that add their own touches. */
	UFUNCTION(BlueprintImplementableEvent, Category = "Scene")
	void OnSceneApplied(const UDressUpScene* Scene);

private:
	UFUNCTION()
	void HandleSceneChanged(UDressUpScene* Scene);

	void Show(const UDressUpScene* Scene);
};
