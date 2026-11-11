// Data assets: one per item, one for the body, one catalog for the UI.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "DressUp/DressUpTypes.h"
#include "DressUpData.generated.h"

class UAnimationAsset;
class USkeletalMesh;
class UStaticMesh;
class UTexture2D;

/** A wearable item. Adding a new piece only needs a new asset of this type. */
UCLASS(BlueprintType)
class ARTSTYLEEXPERIMENTAL_API UDressUpItem : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item")
	TObjectPtr<UTexture2D> Icon = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item")
	EDressUpSlot Slot = EDressUpSlot::Top;

	/** Bending pieces: clothes, hair, VRoid accessories. Follows the body through Leader Pose. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Mesh")
	TObjectPtr<USkeletalMesh> SkeletalMesh = nullptr;

	/** Rigid pieces attached to a socket, used when the slot has a static mesh component. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Mesh")
	TObjectPtr<UStaticMesh> StaticMesh = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Mesh")
	FName Socket;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Mesh")
	FTransform Offset;

	/**
	 * Shoes: sole thickness in cm. The character is raised by this while the shoes are worn, as
	 * VRoid does, so the foot stands on the insole and the sole on the floor.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Mesh", meta = (ClampMin = "0", Units = "cm"))
	float SoleHeight = 0.0f;

	/** Shoes: degrees the feet are pointed (toes down) while worn; VRoid shoes are shaped for ~8. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Mesh", meta = (Units = "deg"))
	float FootPitch = 0.0f;

	/** Colours the UI offers for this item. Empty means the shared palette. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Look")
	TArray<FLinearColor> ColorOptions;

	/** Colour and pattern versions of the same mesh. When set, the UI offers these instead of tints. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Look")
	TArray<FDressUpVariant> Variants;

	/** Body regions this item covers. They are hidden while it is worn. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Rules")
	TArray<EBodyRegion> HiddenBodyRegions;

	/** Slots emptied when this item is put on. A dress blocks Top and Bottom. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Rules")
	TArray<EDressUpSlot> BlockedSlots;

	/**
	 * Items that cannot be worn together with this one, e.g. tops too big to go under a jacket.
	 * Works both ways: putting either on takes the other off, so listing it on one side is enough.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Rules")
	TArray<TObjectPtr<UDressUpItem>> ClashingItems;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Rules")
	EBagType BagType = EBagType::None;
};

/** The character's body. Changing the model means changing this asset, not the code. */
UCLASS(BlueprintType)
class ARTSTYLEEXPERIMENTAL_API UDressUpBody : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	/** Lead skeleton. Shows the face; its body and baked clothes are hidden. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Body")
	TObjectPtr<USkeletalMesh> BodyMesh = nullptr;

	/** Body split into region sections so clothes can hide what they cover. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Body")
	TObjectPtr<USkeletalMesh> RegionMesh = nullptr;

	/** Material sections of BodyMesh to hide (the body and the clothes baked into it). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Body")
	TArray<int32> HiddenBodySections;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animation")
	TObjectPtr<UAnimationAsset> IdleAnim = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animation")
	TObjectPtr<UAnimationAsset> FinalPose = nullptr;
};

/** Everything the UI lists, plus the starting outfit and colour palette. */
UCLASS(BlueprintType)
class ARTSTYLEEXPERIMENTAL_API UDressUpCatalog : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Catalog")
	TArray<TObjectPtr<UDressUpItem>> AllItems;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Catalog")
	TArray<TObjectPtr<UDressUpItem>> DefaultItems;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Catalog")
	TArray<FLinearColor> Palette;

	/** Wardrobe tabs in display order. Empty means DressUp::DefaultTabs(). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Catalog")
	TArray<FDressUpTab> Tabs;

	/** Idle loops the player can pick. The body's IdleAnim plays first. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Pose")
	TArray<FDressUpPoseOption> IdleOptions;

	/** One is picked at random when the outfit is finished. Empty means the body's FinalPose. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Finale")
	TArray<FDressUpFinalPose> FinalPoses;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Finale")
	TArray<FDressUpMessage> Messages;
};
