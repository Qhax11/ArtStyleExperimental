#include "DressUp/Scene/DressUpGround.h"

#include "Components/StaticMeshComponent.h"
#include "DressUp/Scene/DressUpScene.h"
#include "Materials/MaterialInterface.h"

ADressUpGround::ADressUpGround()
{
	Surface = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Surface"));
	SetRootComponent(Surface);
	Surface->SetCastShadow(false);
	Surface->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

void ADressUpGround::ApplyScene(const UDressUpScene* Scene)
{
	UMaterialInterface* Material = Scene ? Scene->GroundMaterial.Get() : nullptr;
	Surface->SetVisibility(Material != nullptr);
	if (Material)
	{
		Surface->SetMaterial(0, Material);
	}
}
