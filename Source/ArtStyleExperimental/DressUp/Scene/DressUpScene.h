// A place to dress up for: what the scene actors in the level show while it is picked.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "DressUpScene.generated.h"

class UMaterialInterface;
class UNiagaraSystem;
class UStaticMesh;
class UTexture2D;

/** Sun and sky light of a scene. The sun should come from where the backdrop painting's light does. */
USTRUCT(BlueprintType)
struct FDressUpSceneLighting
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lighting")
	FRotator SunRotation = FRotator(-40.0f, 30.0f, 0.0f);

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lighting")
	FLinearColor SunColor = FLinearColor::White;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lighting", meta = (ClampMin = "0"))
	float SunIntensity = 6.0f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lighting")
	FLinearColor SkyColor = FLinearColor::White;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lighting", meta = (ClampMin = "0"))
	float SkyIntensity = 1.5f;
};

/**
 * One scene (spring, summer...). Picking it changes everything at once, in the same frame: the
 * scene actors placed in the level (backdrop, ground, prop slots, effect, light rig) each take
 * their part from here. Nothing is loaded or spawned, so the switch is instant.
 */
UCLASS(BlueprintType)
class ARTSTYLEEXPERIMENTAL_API UDressUpScene : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Scene")
	FText DisplayName;

	/** Shown with the finale, e.g. "Bu ilkbahar böyle giyindim". */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Scene", meta = (MultiLine = true))
	FText Caption;

	/** Small picture for the scene button. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Scene")
	TObjectPtr<UTexture2D> Thumbnail = nullptr;

	/** Painted background, 16:9, see ADressUpBackdrop. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Backdrop")
	TObjectPtr<UTexture2D> Backdrop = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Backdrop", meta = (ClampMin = "0"))
	float BackdropBrightness = 1.0f;

	/** Material of the ground under and around the character, see ADressUpGround. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Ground")
	TObjectPtr<UMaterialInterface> GroundMaterial = nullptr;

	/** Mesh for each prop slot in the level, by the slot's name (see ADressUpPropSlot). Slots not listed stay empty. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Props")
	TMap<FName, TObjectPtr<UStaticMesh>> Props;

	/** Drifting petals, leaves or snow, see ADressUpSceneEffect. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Effect")
	TObjectPtr<UNiagaraSystem> Effect = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lighting")
	FDressUpSceneLighting Lighting;
};
