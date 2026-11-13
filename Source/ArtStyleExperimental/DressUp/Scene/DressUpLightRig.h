// Sets the level's sun and sky light for the scene.

#pragma once

#include "CoreMinimal.h"
#include "DressUp/Scene/DressUpSceneActor.h"
#include "DressUpLightRig.generated.h"

class ADirectionalLight;
class ASkyLight;

/** Points the level's lights at the scene's lighting. The light actors stay ordinary lights. */
UCLASS()
class ARTSTYLEEXPERIMENTAL_API ADressUpLightRig : public ADressUpSceneActor
{
	GENERATED_BODY()

public:
	ADressUpLightRig();

	UPROPERTY(EditInstanceOnly, BlueprintReadOnly, Category = "Lighting")
	TObjectPtr<ADirectionalLight> Sun;

	UPROPERTY(EditInstanceOnly, BlueprintReadOnly, Category = "Lighting")
	TObjectPtr<ASkyLight> Sky;

protected:
	virtual void ApplyScene(const UDressUpScene* Scene) override;
};
