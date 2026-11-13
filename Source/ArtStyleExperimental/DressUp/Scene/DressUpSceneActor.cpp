#include "DressUp/Scene/DressUpSceneActor.h"

#include "DressUp/Scene/DressUpScene.h"
#include "DressUp/Scene/DressUpSceneSubsystem.h"
#include "Engine/World.h"

ADressUpSceneActor::ADressUpSceneActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void ADressUpSceneActor::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	if (GetWorld() && !GetWorld()->IsGameWorld())
	{
		Show(PreviewScene);
	}
}

void ADressUpSceneActor::BeginPlay()
{
	Super::BeginPlay();
	if (UDressUpSceneSubsystem* Scenes = UDressUpSceneSubsystem::Get(this))
	{
		Scenes->OnSceneChanged.AddUniqueDynamic(this, &ADressUpSceneActor::HandleSceneChanged);
		Show(Scenes->GetScene());
	}
}

void ADressUpSceneActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (UDressUpSceneSubsystem* Scenes = UDressUpSceneSubsystem::Get(this))
	{
		Scenes->OnSceneChanged.RemoveDynamic(this, &ADressUpSceneActor::HandleSceneChanged);
	}
	Super::EndPlay(EndPlayReason);
}

void ADressUpSceneActor::HandleSceneChanged(UDressUpScene* Scene)
{
	Show(Scene);
}

void ADressUpSceneActor::Show(const UDressUpScene* Scene)
{
	ApplyScene(Scene);
	OnSceneApplied(Scene);
}
