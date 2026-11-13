#include "DressUp/Scene/DressUpSceneSubsystem.h"

#include "DressUp/Core/DressUpData.h"
#include "DressUp/Core/DressUpProjectSettings.h"
#include "DressUp/Scene/DressUpScene.h"
#include "Engine/World.h"

UDressUpSceneSubsystem* UDressUpSceneSubsystem::Get(const UObject* WorldContext)
{
	const UWorld* World = WorldContext ? WorldContext->GetWorld() : nullptr;
	return World ? World->GetSubsystem<UDressUpSceneSubsystem>() : nullptr;
}

bool UDressUpSceneSubsystem::DoesSupportWorldType(const EWorldType::Type WorldType) const
{
	return WorldType == EWorldType::Game || WorldType == EWorldType::PIE;
}

void UDressUpSceneSubsystem::OnWorldBeginPlay(UWorld& InWorld)
{
	Super::OnWorldBeginPlay(InWorld);
	Catalog = UDressUpProjectSettings::Get()->Catalog.LoadSynchronous();
	const TArray<UDressUpScene*> Scenes = GetScenes();
	if (!CurrentScene && Scenes.Num() > 0)
	{
		SetScene(Scenes[0]);
	}
}

TArray<UDressUpScene*> UDressUpSceneSubsystem::GetScenes() const
{
	TArray<UDressUpScene*> Scenes;
	if (Catalog)
	{
		for (UDressUpScene* Scene : Catalog->Scenes)
		{
			if (Scene)
			{
				Scenes.Add(Scene);
			}
		}
	}
	return Scenes;
}

void UDressUpSceneSubsystem::SetScene(UDressUpScene* Scene)
{
	if (!Scene || Scene == CurrentScene)
	{
		return;
	}
	CurrentScene = Scene;
	OnSceneChanged.Broadcast(Scene);
}
