#include "DressUp/Scene/DressUpPropSlot.h"

#include "Components/StaticMeshComponent.h"
#include "DressUp/Scene/DressUpScene.h"
#include "Engine/StaticMesh.h"

ADressUpPropSlot::ADressUpPropSlot()
{
	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	SetRootComponent(Mesh);
	// The mesh changes with the scene.
	Mesh->SetMobility(EComponentMobility::Movable);
	Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

void ADressUpPropSlot::ApplyScene(const UDressUpScene* Scene)
{
	const TObjectPtr<UStaticMesh>* Found = Scene ? Scene->Props.Find(SlotName) : nullptr;
	UStaticMesh* Shown = Found ? Found->Get() : nullptr;
	Mesh->SetStaticMesh(Shown);
	Mesh->SetVisibility(Shown != nullptr);
}
