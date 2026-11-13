// The ground under and around the character.

#pragma once

#include "CoreMinimal.h"
#include "DressUp/Scene/DressUpSceneActor.h"
#include "DressUpGround.generated.h"

class UStaticMeshComponent;

/**
 * A real ground surface in place of the backdrop's painted ground: it takes shadows and has its
 * own texture, from the scene. Place and scale it in the level so its far edge meets a natural
 * line in the painting, such as where a path meets the grass. The mesh is set on the component.
 */
UCLASS()
class ARTSTYLEEXPERIMENTAL_API ADressUpGround : public ADressUpSceneActor
{
	GENERATED_BODY()

public:
	ADressUpGround();

protected:
	virtual void ApplyScene(const UDressUpScene* Scene) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Ground")
	TObjectPtr<UStaticMeshComponent> Surface;
};
