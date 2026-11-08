#include "DressUp/DressUpCharacter.h"

#include "Animation/AnimationAsset.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "DressUp/DressUpData.h"
#include "DressUp/OutfitComponent.h"
#include "TimerManager.h"

namespace
{
	/** Rigid accessories that attach to a socket. Every other slot bends with the body. */
	bool IsStaticSlot(EDressUpSlot Slot)
	{
		return Slot == EDressUpSlot::Earrings;  // VRoid neck pieces (ties, ribbons) bend with the body
	}

	USkeletalMeshComponent* MakeSkeletal(AActor* Owner, FName Name, USceneComponent* Parent)
	{
		USkeletalMeshComponent* Mesh = Owner->CreateDefaultSubobject<USkeletalMeshComponent>(Name);
		Mesh->SetupAttachment(Parent);
		Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		return Mesh;
	}
}

ADressUpCharacter::ADressUpCharacter()
{
	PrimaryActorTick.bCanEverTick = false;

	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	BodyMesh = MakeSkeletal(this, TEXT("BodyMesh"), RootComponent);
	BodyRegions = MakeSkeletal(this, TEXT("BodyRegions"), BodyMesh);

	UEnum* SlotEnum = StaticEnum<EDressUpSlot>();
	for (int32 Index = 0; Index < SlotEnum->NumEnums() - 1; ++Index)
	{
		const EDressUpSlot Slot = static_cast<EDressUpSlot>(SlotEnum->GetValueByIndex(Index));
		const FName Name(*SlotEnum->GetNameStringByIndex(Index));
		UMeshComponent* Mesh = nullptr;
		if (IsStaticSlot(Slot))
		{
			UStaticMeshComponent* Static = CreateDefaultSubobject<UStaticMeshComponent>(Name);
			Static->SetupAttachment(BodyMesh);
			Static->SetCollisionEnabled(ECollisionEnabled::NoCollision);
			Mesh = Static;
		}
		else
		{
			Mesh = MakeSkeletal(this, Name, BodyMesh);
		}
		SlotMeshes.Add(Slot, Mesh);
	}

	Outfit = CreateDefaultSubobject<UOutfitComponent>(TEXT("Outfit"));
}

void ADressUpCharacter::BeginPlay()
{
	Super::BeginPlay();

	LoadedBody = Body.LoadSynchronous();
	if (UDressUpBody* BodyData = LoadedBody)
	{
		BodyMesh->SetSkinnedAssetAndUpdate(BodyData->BodyMesh, true);
		for (int32 Section : BodyData->HiddenBodySections)
		{
			BodyMesh->ShowMaterialSection(Section, 0, false, 0);
		}
		BodyRegions->SetSkinnedAssetAndUpdate(BodyData->RegionMesh, false);
		BodyRegions->SetLeaderPoseComponent(BodyMesh);
		SetIdle(ShowcaseIdle ? ShowcaseIdle.Get() : BodyData->IdleAnim.Get());
	}
	LoadedCatalog = Catalog.LoadSynchronous();

	Outfit->Initialize(BodyMesh, BodyRegions);
	for (const TPair<EDressUpSlot, TObjectPtr<UMeshComponent>>& Pair : SlotMeshes)
	{
		Outfit->RegisterSlot(Pair.Key, Pair.Value);
	}
	if (ShowcaseItems.Num() > 0)
	{
		Outfit->DefaultItems = ShowcaseItems;
	}
	else if (LoadedCatalog)
	{
		Outfit->DefaultItems = LoadedCatalog->DefaultItems;
	}
	Outfit->ResetToDefault();
}

void ADressUpCharacter::SetIdle(UAnimationAsset* Anim)
{
	CurrentIdle = Anim;
	ReturnToIdle();
}

void ADressUpCharacter::ReturnToIdle()
{
	GetWorldTimerManager().ClearTimer(PoseTimer);
	BodyMesh->bPauseAnims = false;
	if (CurrentIdle)
	{
		BodyMesh->PlayAnimation(CurrentIdle, true);
	}
}

void ADressUpCharacter::PlayFinalPose(const FDressUpFinalPose& Pose)
{
	if (!Pose.Anim)
	{
		return;
	}
	GetWorldTimerManager().ClearTimer(PoseTimer);
	BodyMesh->bPauseAnims = false;
	BodyMesh->PlayAnimation(Pose.Anim, false);
	if (Pose.HoldTime >= 0.0f)
	{
		GetWorldTimerManager().SetTimer(PoseTimer, this, &ADressUpCharacter::FreezePose, FMath::Max(Pose.HoldTime, 0.01f), false);
	}
	else
	{
		GetWorldTimerManager().SetTimer(PoseTimer, this, &ADressUpCharacter::ReturnToIdle, Pose.Anim->GetPlayLength(), false);
	}
}

void ADressUpCharacter::FreezePose()
{
	BodyMesh->bPauseAnims = true;
}
