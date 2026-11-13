// A fixed place in the set for a prop.

#pragma once

#include "CoreMinimal.h"
#include "DressUp/Scene/DressUpSceneActor.h"
#include "DressUpPropSlot.generated.h"

class UStaticMeshComponent;

/**
 * Stands where a prop goes (the podium, a flower clump on the left...). It keeps its place in
 * every scene; the scene only says which mesh it shows, by SlotName, or leaves it empty.
 */
UCLASS()
class ARTSTYLEEXPERIMENTAL_API ADressUpPropSlot : public ADressUpSceneActor
{
	GENERATED_BODY()

public:
	ADressUpPropSlot();

	/** Key in UDressUpScene::Props, e.g. "Podium" or "LeftFlowers". */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Prop")
	FName SlotName;

protected:
	virtual void ApplyScene(const UDressUpScene* Scene) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Prop")
	TObjectPtr<UStaticMeshComponent> Mesh;
};
