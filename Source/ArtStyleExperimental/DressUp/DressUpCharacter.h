// The character standing in the scene: body, one component per slot, and the outfit logic.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DressUp/DressUpTypes.h"
#include "DressUpCharacter.generated.h"

class UDressUpBody;
class UDressUpCatalog;
class UMeshComponent;
class UOutfitComponent;
class USkeletalMeshComponent;

UCLASS()
class ARTSTYLEEXPERIMENTAL_API ADressUpCharacter : public AActor
{
	GENERATED_BODY()

public:
	ADressUpCharacter();

	UFUNCTION(BlueprintPure, Category = "Dress Up")
	UOutfitComponent* GetOutfit() const { return Outfit; }

	/** Loaded catalog; valid after BeginPlay. */
	UFUNCTION(BlueprintPure, Category = "Dress Up")
	UDressUpCatalog* GetCatalog() const { return LoadedCatalog; }

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	TSoftObjectPtr<UDressUpBody> Body = TSoftObjectPtr<UDressUpBody>(FSoftObjectPath(TEXT("/Game/DressUp/Data/DA_Body_evrar.DA_Body_evrar")));

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	TSoftObjectPtr<UDressUpCatalog> Catalog = TSoftObjectPtr<UDressUpCatalog>(FSoftObjectPath(TEXT("/Game/DressUp/Data/DA_Catalog.DA_Catalog")));

protected:
	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USkeletalMeshComponent> BodyMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USkeletalMeshComponent> BodyRegions;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TMap<EDressUpSlot, TObjectPtr<UMeshComponent>> SlotMeshes;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UOutfitComponent> Outfit;

private:
	UPROPERTY()
	TObjectPtr<UDressUpCatalog> LoadedCatalog;
};
