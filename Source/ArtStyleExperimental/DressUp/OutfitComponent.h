// Puts items on and takes them off. The UI only talks to this component.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GameFramework/SaveGame.h"
#include "DressUp/DressUpTypes.h"
#include "OutfitComponent.generated.h"

class UDressUpItem;
class UMeshComponent;
class USkeletalMeshComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnOutfitChanged);

/** Saved outfit on disk. */
UCLASS()
class ARTSTYLEEXPERIMENTAL_API UDressUpSaveGame : public USaveGame
{
	GENERATED_BODY()

public:
	UPROPERTY()
	FDressUpOutfit Outfit;
};

UCLASS(ClassGroup = (DressUp), meta = (BlueprintSpawnableComponent))
class ARTSTYLEEXPERIMENTAL_API UOutfitComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	/** Sets the lead body and the region mesh used to hide covered skin. */
	UFUNCTION(BlueprintCallable, Category = "Outfit")
	void Initialize(USkeletalMeshComponent* InBodyMesh, USkeletalMeshComponent* InBodyRegions);

	/** Tells the component which mesh component shows a slot. */
	UFUNCTION(BlueprintCallable, Category = "Outfit")
	void RegisterSlot(EDressUpSlot Slot, UMeshComponent* Component);

	/** Puts an item on, removing whatever it blocks or is blocked by. */
	UFUNCTION(BlueprintCallable, Category = "Outfit")
	void Equip(UDressUpItem* Item);

	UFUNCTION(BlueprintCallable, Category = "Outfit")
	void Unequip(EDressUpSlot Slot);

	/** Equips the item, or takes it off when it is already worn. */
	UFUNCTION(BlueprintCallable, Category = "Outfit")
	void Toggle(UDressUpItem* Item);

	UFUNCTION(BlueprintPure, Category = "Outfit")
	UDressUpItem* GetEquipped(EDressUpSlot Slot) const;

	UFUNCTION(BlueprintPure, Category = "Outfit")
	bool IsEquipped(const UDressUpItem* Item) const;

	/** Takes everything off and puts DefaultItems back on. */
	UFUNCTION(BlueprintCallable, Category = "Outfit")
	void ResetToDefault();

	/** Tints the item in a slot. The tint is cleared when the item changes. */
	UFUNCTION(BlueprintCallable, Category = "Outfit")
	void SetSlotColor(EDressUpSlot Slot, FLinearColor Color);

	/** Tints the item the player picked most recently, if it is still worn. */
	UFUNCTION(BlueprintCallable, Category = "Outfit")
	void SetColorForLastSlot(FLinearColor Color);

	/** Switches the item in a slot to one of its Variants. Reset when the item changes. */
	UFUNCTION(BlueprintCallable, Category = "Outfit")
	void SetSlotVariant(EDressUpSlot Slot, int32 Variant);

	UFUNCTION(BlueprintCallable, Category = "Outfit")
	void SetVariantForLastSlot(int32 Variant);

	UFUNCTION(BlueprintPure, Category = "Outfit")
	int32 GetSlotVariant(EDressUpSlot Slot) const;

	/** The item the player picked most recently, if it is still worn. */
	UFUNCTION(BlueprintPure, Category = "Outfit")
	UDressUpItem* GetLastItem() const;

	UFUNCTION(BlueprintPure, Category = "Outfit")
	FDressUpOutfit GetOutfit() const;

	UFUNCTION(BlueprintCallable, Category = "Outfit")
	void ApplyOutfit(const FDressUpOutfit& Outfit);

	UFUNCTION(BlueprintCallable, Category = "Outfit")
	bool SaveOutfit(const FString& SlotName);

	UFUNCTION(BlueprintCallable, Category = "Outfit")
	bool LoadOutfit(const FString& SlotName);

	UPROPERTY(BlueprintAssignable, Category = "Outfit")
	FOnOutfitChanged OnOutfitChanged;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Outfit")
	TArray<TObjectPtr<UDressUpItem>> DefaultItems;

private:
	/** Shows every body region, then hides the ones worn items cover. */
	void RefreshBodyVisibility();

	/** Puts the item's mesh on the slot component, or clears it when Item is null. */
	void ApplyMesh(EDressUpSlot Slot, UDressUpItem* Item);

	/** Changes state without broadcasting, so composite operations notify once. */
	void UnequipInternal(EDressUpSlot Slot);
	void EquipInternal(UDressUpItem* Item);

	UPROPERTY()
	TObjectPtr<USkeletalMeshComponent> BodyMesh;

	UPROPERTY()
	TObjectPtr<USkeletalMeshComponent> BodyRegions;

	UPROPERTY()
	TMap<EDressUpSlot, TObjectPtr<UMeshComponent>> SlotComponents;

	UPROPERTY()
	TMap<EDressUpSlot, TObjectPtr<UDressUpItem>> Equipped;

	UPROPERTY()
	TMap<EDressUpSlot, FLinearColor> SlotColors;

	UPROPERTY()
	TMap<EDressUpSlot, int32> SlotVariants;

	TOptional<EDressUpSlot> LastSlot;
};
