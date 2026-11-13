// Keeps the current scene and tells the scene actors when it changes.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "DressUpSceneSubsystem.generated.h"

class UDressUpCatalog;
class UDressUpScene;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FDressUpSceneChanged, UDressUpScene*, Scene);

/**
 * The current scene of a game world. It knows nothing about the actors that show a scene:
 * they subscribe to OnSceneChanged themselves (see ADressUpSceneActor), so a new kind of scene
 * actor needs no change here. Starts with the first scene of the catalog set in Project
 * Settings > Dress Up.
 */
UCLASS()
class ARTSTYLEEXPERIMENTAL_API UDressUpSceneSubsystem : public UWorldSubsystem
{
	GENERATED_BODY()

public:
	static UDressUpSceneSubsystem* Get(const UObject* WorldContext);

	/** Shows Scene everywhere at once. Does nothing if it is already shown. */
	UFUNCTION(BlueprintCallable, Category = "Dress Up|Scene")
	void SetScene(UDressUpScene* Scene);

	UFUNCTION(BlueprintPure, Category = "Dress Up|Scene")
	UDressUpScene* GetScene() const { return CurrentScene; }

	/** Scenes the player can pick, in button order. */
	UFUNCTION(BlueprintPure, Category = "Dress Up|Scene")
	TArray<UDressUpScene*> GetScenes() const;

	UPROPERTY(BlueprintAssignable, Category = "Dress Up|Scene")
	FDressUpSceneChanged OnSceneChanged;

protected:
	virtual bool DoesSupportWorldType(const EWorldType::Type WorldType) const override;
	virtual void OnWorldBeginPlay(UWorld& InWorld) override;

private:
	/** Holds every scene, and with them all their assets, so switching never waits for a load. */
	UPROPERTY(Transient)
	TObjectPtr<UDressUpCatalog> Catalog;

	UPROPERTY(Transient)
	TObjectPtr<UDressUpScene> CurrentScene;
};
