#include "DressUp/OutfitComponent.h"

#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "DressUp/DressUpData.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"

DEFINE_LOG_CATEGORY_STATIC(LogOutfit, Log, All);

namespace
{
	const FName ColorParam(TEXT("mtoon_Color"));
	const FName ShadeColorParam(TEXT("mtoon_ShadeColor"));

	/** Drops material overrides so a new mesh starts with its own materials (and no old tint). */
	void ClearMaterialOverrides(UMeshComponent* Mesh)
	{
		for (int32 Index = 0; Index < Mesh->GetNumMaterials(); ++Index)
		{
			Mesh->SetMaterial(Index, nullptr);
		}
	}
}

void UOutfitComponent::Initialize(USkeletalMeshComponent* InBodyMesh, USkeletalMeshComponent* InBodyRegions)
{
	BodyMesh = InBodyMesh;
	BodyRegions = InBodyRegions;
}

void UOutfitComponent::RegisterSlot(EDressUpSlot Slot, UMeshComponent* Component)
{
	SlotComponents.Add(Slot, Component);
}

void UOutfitComponent::Equip(UDressUpItem* Item)
{
	if (!Item)
	{
		return;
	}
	EquipInternal(Item);
	LastSlot = Item->Slot;
	RefreshBodyVisibility();
	OnOutfitChanged.Broadcast();
}

void UOutfitComponent::Unequip(EDressUpSlot Slot)
{
	UnequipInternal(Slot);
	RefreshBodyVisibility();
	OnOutfitChanged.Broadcast();
}

void UOutfitComponent::Toggle(UDressUpItem* Item)
{
	if (!Item)
	{
		return;
	}
	if (IsEquipped(Item))
	{
		Unequip(Item->Slot);
	}
	else
	{
		Equip(Item);
	}
}

UDressUpItem* UOutfitComponent::GetEquipped(EDressUpSlot Slot) const
{
	const TObjectPtr<UDressUpItem>* Found = Equipped.Find(Slot);
	return Found ? Found->Get() : nullptr;
}

bool UOutfitComponent::IsEquipped(const UDressUpItem* Item) const
{
	return Item && GetEquipped(Item->Slot) == Item;
}

void UOutfitComponent::ResetToDefault()
{
	TArray<EDressUpSlot> Worn;
	Equipped.GetKeys(Worn);
	for (EDressUpSlot Slot : Worn)
	{
		UnequipInternal(Slot);
	}
	for (UDressUpItem* Item : DefaultItems)
	{
		if (Item)
		{
			EquipInternal(Item);
		}
	}
	LastSlot.Reset();
	RefreshBodyVisibility();
	OnOutfitChanged.Broadcast();
}

void UOutfitComponent::SetSlotColor(EDressUpSlot Slot, FLinearColor Color)
{
	TObjectPtr<UMeshComponent>* Component = SlotComponents.Find(Slot);
	if (!Component || !*Component || !GetEquipped(Slot))
	{
		return;
	}
	(*Component)->SetColorParameterValueOnMaterials(ColorParam, Color);
	(*Component)->SetColorParameterValueOnMaterials(ShadeColorParam, Color);
	SlotColors.Add(Slot, Color);
	OnOutfitChanged.Broadcast();
}

void UOutfitComponent::SetColorForLastSlot(FLinearColor Color)
{
	if (LastSlot.IsSet())
	{
		SetSlotColor(LastSlot.GetValue(), Color);
	}
}

void UOutfitComponent::SetSlotVariant(EDressUpSlot Slot, int32 Variant)
{
	TObjectPtr<UMeshComponent>* Component = SlotComponents.Find(Slot);
	UDressUpItem* Item = GetEquipped(Slot);
	if (!Component || !*Component || !Item || !Item->Variants.IsValidIndex(Variant))
	{
		return;
	}
	ClearMaterialOverrides(*Component);
	const TArray<TObjectPtr<UMaterialInterface>>& Materials = Item->Variants[Variant].Materials;
	for (int32 Index = 0; Index < Materials.Num(); ++Index)
	{
		if (Materials[Index])
		{
			(*Component)->SetMaterial(Index, Materials[Index]);
		}
	}
	SlotColors.Remove(Slot);
	SlotVariants.Add(Slot, Variant);
	OnOutfitChanged.Broadcast();
}

void UOutfitComponent::SetVariantForLastSlot(int32 Variant)
{
	if (LastSlot.IsSet())
	{
		SetSlotVariant(LastSlot.GetValue(), Variant);
	}
}

int32 UOutfitComponent::GetSlotVariant(EDressUpSlot Slot) const
{
	const int32* Found = SlotVariants.Find(Slot);
	return Found ? *Found : 0;
}

UDressUpItem* UOutfitComponent::GetLastItem() const
{
	return LastSlot.IsSet() ? GetEquipped(LastSlot.GetValue()) : nullptr;
}

int32 UOutfitComponent::GetLastVariant() const
{
	return LastSlot.IsSet() ? GetSlotVariant(LastSlot.GetValue()) : 0;
}

bool UOutfitComponent::GetLastColor(FLinearColor& OutColor) const
{
	const FLinearColor* Found = LastSlot.IsSet() ? SlotColors.Find(LastSlot.GetValue()) : nullptr;
	if (Found)
	{
		OutColor = *Found;
	}
	return Found != nullptr;
}

FDressUpOutfit UOutfitComponent::GetOutfit() const
{
	FDressUpOutfit Outfit;
	for (const TPair<EDressUpSlot, TObjectPtr<UDressUpItem>>& Pair : Equipped)
	{
		FDressUpOutfitEntry& Entry = Outfit.Entries.AddDefaulted_GetRef();
		Entry.Item = Pair.Value;
		Entry.Variant = GetSlotVariant(Pair.Key);
		if (const FLinearColor* Color = SlotColors.Find(Pair.Key))
		{
			Entry.bHasColor = true;
			Entry.Color = *Color;
		}
	}
	return Outfit;
}

void UOutfitComponent::ApplyOutfit(const FDressUpOutfit& Outfit)
{
	TArray<EDressUpSlot> Worn;
	Equipped.GetKeys(Worn);
	for (EDressUpSlot Slot : Worn)
	{
		UnequipInternal(Slot);
	}
	for (const FDressUpOutfitEntry& Entry : Outfit.Entries)
	{
		EquipInternal(Entry.Item);
	}
	RefreshBodyVisibility();
	for (const FDressUpOutfitEntry& Entry : Outfit.Entries)
	{
		if (Entry.Item && Entry.Variant > 0)
		{
			SetSlotVariant(Entry.Item->Slot, Entry.Variant);
		}
		if (Entry.Item && Entry.bHasColor)
		{
			SetSlotColor(Entry.Item->Slot, Entry.Color);
		}
	}
	OnOutfitChanged.Broadcast();
}

bool UOutfitComponent::SaveOutfit(const FString& SlotName)
{
	UDressUpSaveGame* Save = Cast<UDressUpSaveGame>(UGameplayStatics::CreateSaveGameObject(UDressUpSaveGame::StaticClass()));
	Save->Outfit = GetOutfit();
	return UGameplayStatics::SaveGameToSlot(Save, SlotName, 0);
}

bool UOutfitComponent::LoadOutfit(const FString& SlotName)
{
	const UDressUpSaveGame* Save = Cast<UDressUpSaveGame>(UGameplayStatics::LoadGameFromSlot(SlotName, 0));
	if (!Save)
	{
		return false;
	}
	ApplyOutfit(Save->Outfit);
	return true;
}

void UOutfitComponent::EquipInternal(UDressUpItem* Item)
{
	if (!Item)
	{
		return;
	}
	for (EDressUpSlot Blocked : Item->BlockedSlots)
	{
		UnequipInternal(Blocked);
	}
	// Remove worn items that block this slot, e.g. a dress when a top goes on.
	TArray<EDressUpSlot> Worn;
	Equipped.GetKeys(Worn);
	for (EDressUpSlot Slot : Worn)
	{
		const UDressUpItem* Other = GetEquipped(Slot);
		if (Other && Other->BlockedSlots.Contains(Item->Slot))
		{
			UnequipInternal(Slot);
		}
	}
	Equipped.Add(Item->Slot, Item);
	SlotColors.Remove(Item->Slot);
	SlotVariants.Remove(Item->Slot);
	ApplyMesh(Item->Slot, Item);
}

void UOutfitComponent::UnequipInternal(EDressUpSlot Slot)
{
	Equipped.Remove(Slot);
	SlotColors.Remove(Slot);
	SlotVariants.Remove(Slot);
	ApplyMesh(Slot, nullptr);
}

void UOutfitComponent::ApplyMesh(EDressUpSlot Slot, UDressUpItem* Item)
{
	TObjectPtr<UMeshComponent>* Found = SlotComponents.Find(Slot);
	if (!Found || !*Found)
	{
		if (Item)
		{
			UE_LOG(LogOutfit, Warning, TEXT("No component registered for slot %s"),
				*StaticEnum<EDressUpSlot>()->GetNameStringByValue(static_cast<int64>(Slot)));
		}
		return;
	}
	UMeshComponent* Component = *Found;
	ClearMaterialOverrides(Component);

	if (USkeletalMeshComponent* Skeletal = Cast<USkeletalMeshComponent>(Component))
	{
		Skeletal->SetSkinnedAssetAndUpdate(Item ? Item->SkeletalMesh.Get() : nullptr, false);
		if (Item && BodyMesh)
		{
			Skeletal->SetLeaderPoseComponent(BodyMesh);
		}
	}
	else if (UStaticMeshComponent* Static = Cast<UStaticMeshComponent>(Component))
	{
		Static->SetStaticMesh(Item ? Item->StaticMesh.Get() : nullptr);
		if (Item && BodyMesh)
		{
			const FAttachmentTransformRules Rules(EAttachmentRule::SnapToTarget, EAttachmentRule::SnapToTarget,
				EAttachmentRule::KeepRelative, false);
			Static->AttachToComponent(BodyMesh, Rules, Item->Socket);
			Static->SetRelativeTransform(Item->Offset);
		}
	}
}

void UOutfitComponent::RefreshBodyVisibility()
{
	if (!BodyRegions)
	{
		return;
	}
	for (const FName& SlotName : BodyRegions->GetMaterialSlotNames())
	{
		BodyRegions->ShowMaterialSection(BodyRegions->GetMaterialIndex(SlotName), 0, true, 0);
	}
	for (const TPair<EDressUpSlot, TObjectPtr<UDressUpItem>>& Pair : Equipped)
	{
		if (!Pair.Value)
		{
			continue;
		}
		for (EBodyRegion Region : Pair.Value->HiddenBodyRegions)
		{
			const int32 Index = BodyRegions->GetMaterialIndex(DressUp::RegionSlotName(Region));
			if (Index != INDEX_NONE)
			{
				BodyRegions->ShowMaterialSection(Index, 0, false, 0);
			}
		}
	}
}
