// The painted background.

#pragma once

#include "CoreMinimal.h"
#include "DressUp/Scene/DressUpSceneActor.h"
#include "DressUpBackdrop.generated.h"

class ACameraActor;
class UMaterialInstanceDynamic;
class UStaticMeshComponent;

/**
 * A picture card far behind the character that fills Camera's view. It is sized and placed in
 * the editor only (when the actor is built or moved) and saved with the level; in play only the
 * picture changes.
 *
 * The camera keeps its vertical field of view, so a wider window sees more at the sides. The card
 * is made wide enough for windows up to CoverAspect, keeping the picture's shape; the extra
 * height this needs is cropped from the top, so the painted ground stays at the bottom of the
 * screen.
 *
 * The card's mesh and material are set on the component in the level: a plane (+Z facing, UVs
 * over its XY square) and an unlit material with a texture parameter and a brightness parameter.
 */
UCLASS()
class ARTSTYLEEXPERIMENTAL_API ADressUpBackdrop : public ADressUpSceneActor
{
	GENERATED_BODY()

public:
	ADressUpBackdrop();

	/** The view the picture fills. */
	UPROPERTY(EditInstanceOnly, BlueprintReadOnly, Category = "Backdrop")
	TObjectPtr<ACameraActor> Camera;

	/** Widest window shape (width / height) the picture still covers. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Backdrop", meta = (ClampMin = "1"))
	float CoverAspect = 2.0f;

	/** How far in front of the camera the card stands, cm. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Backdrop", meta = (ClampMin = "10"))
	float Distance = 1500.0f;

	/** Extra size, so the finale camera stays covered too. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Backdrop", meta = (ClampMin = "1"))
	float Overscan = 1.05f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Backdrop")
	FName PictureParameter = TEXT("Picture");

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Backdrop")
	FName BrightnessParameter = TEXT("Brightness");

protected:
	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void ApplyScene(const UDressUpScene* Scene) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Backdrop")
	TObjectPtr<UStaticMeshComponent> Card;

private:
	/** Sizes the card for the camera and places it in front of it. Editor only. */
	void FitToCamera();

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> CardMaterial;
};
