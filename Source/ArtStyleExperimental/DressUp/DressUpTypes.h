// Shared types for the dress-up game.

#pragma once

#include "CoreMinimal.h"
#include "DressUpTypes.generated.h"

class UAnimationAsset;
class UDressUpItem;

/** Where an item is worn. Each slot holds at most one item. */
UENUM(BlueprintType)
enum class EDressUpSlot : uint8
{
	Hair,
	Top,
	Bottom,
	Dress,
	Outer,
	Socks,
	Shoes,
	Bag,
	Glasses,
	Earrings,
	Necklace,
	Hat
};

/**
 * Body areas that clothes can hide. Each one is a material section named
 * "Region_<Name>" on the body region mesh (see split_body_regions.py).
 */
UENUM(BlueprintType)
enum class EBodyRegion : uint8
{
	Chest,
	Belly,
	Hips,
	UpperArm,
	LowerArm,
	Hand,
	Neck,
	Thigh,
	Calf,
	Foot,
	/** Above the foot up to the ankle bone: covered by sneakers, open in low shoes. */
	Ankle
};

/** How a bag sits on the body. */
UENUM(BlueprintType)
enum class EBagType : uint8
{
	None,
	Shoulder,
	Hand,
	Crossbody,
	Backpack
};

/** One worn item and its optional tint. */
USTRUCT(BlueprintType)
struct FDressUpOutfitEntry
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dress Up")
	TObjectPtr<UDressUpItem> Item = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dress Up")
	bool bHasColor = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dress Up")
	FLinearColor Color = FLinearColor::White;
};

/** A full outfit, used for saving and loading. */
USTRUCT(BlueprintType)
struct FDressUpOutfit
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dress Up")
	TArray<FDressUpOutfitEntry> Entries;
};

/** A wardrobe tab: a name and the slots whose items it lists. */
USTRUCT(BlueprintType)
struct FDressUpTab
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dress Up")
	FText Name;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dress Up")
	TArray<EDressUpSlot> Slots;
};

/** An idle loop the player can pick while dressing. */
USTRUCT(BlueprintType)
struct FDressUpPoseOption
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dress Up")
	FText Name;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dress Up")
	TObjectPtr<UAnimationAsset> Anim = nullptr;
};

/** A pose played when the outfit is finished. */
USTRUCT(BlueprintType)
struct FDressUpFinalPose
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dress Up")
	TObjectPtr<UAnimationAsset> Anim = nullptr;

	/** Seconds into Anim where the pose freezes for the photo. Negative plays it through, then returns to the idle. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dress Up")
	float HoldTime = -1.0f;
};

/**
 * A closing message. It can be shown when every listed item is worn and every listed
 * slot is filled. Messages without conditions are used when no conditional one fits.
 */
USTRUCT(BlueprintType)
struct FDressUpMessage
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dress Up", meta = (MultiLine = true))
	FText Text;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dress Up")
	TArray<TObjectPtr<UDressUpItem>> RequiredItems;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dress Up")
	TArray<EDressUpSlot> RequiredSlots;
};

namespace DressUp
{
	/** Tabs used when the catalog defines none. */
	ARTSTYLEEXPERIMENTAL_API TArray<FDressUpTab> DefaultTabs();

	/** Material slot name of a body region on the region mesh, e.g. "Region_Chest". */
	ARTSTYLEEXPERIMENTAL_API FName RegionSlotName(EBodyRegion Region);
}
