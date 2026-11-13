// The scene's drifting effect: petals, leaves, snow.

#pragma once

#include "CoreMinimal.h"
#include "DressUp/Scene/DressUpSceneActor.h"
#include "DressUpSceneEffect.generated.h"

class UNiagaraComponent;

/** Plays the scene's Niagara system where it stands; stops when the scene has none. */
UCLASS()
class ARTSTYLEEXPERIMENTAL_API ADressUpSceneEffect : public ADressUpSceneActor
{
	GENERATED_BODY()

public:
	ADressUpSceneEffect();

protected:
	virtual void ApplyScene(const UDressUpScene* Scene) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Effect")
	TObjectPtr<UNiagaraComponent> Effect;
};
