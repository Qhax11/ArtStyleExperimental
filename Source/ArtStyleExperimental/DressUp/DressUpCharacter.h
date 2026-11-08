// The character standing in the scene: body, one component per slot, and the outfit logic.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DressUp/DressUpTypes.h"
#include "DressUpCharacter.generated.h"

class UAnimationAsset;
class UDressUpBody;
class UDressUpCatalog;
class UDressUpItem;
class UMeshComponent;
class UDressUpNameTag;
class UOutfitComponent;
class USkeletalMeshComponent;
class UWidgetComponent;

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

	UFUNCTION(BlueprintPure, Category = "Dress Up")
	UDressUpBody* GetBody() const { return LoadedBody; }

	/** Loops an idle animation while dressing. */
	UFUNCTION(BlueprintCallable, Category = "Dress Up")
	void SetIdle(UAnimationAsset* Anim);

	UFUNCTION(BlueprintPure, Category = "Dress Up")
	UAnimationAsset* GetIdle() const { return CurrentIdle; }

	/** Plays a finishing pose; freezes at its HoldTime, or returns to the idle when it ends. */
	UFUNCTION(BlueprintCallable, Category = "Dress Up")
	void PlayFinalPose(const FDressUpFinalPose& Pose);

	/** Stops any finishing pose and loops the current idle again. */
	UFUNCTION(BlueprintCallable, Category = "Dress Up")
	void ReturnToIdle();

	/** Shows the name above the head, or hides it when the name is empty. */
	UFUNCTION(BlueprintCallable, Category = "Dress Up")
	void ShowNameTag(const FString& Name);

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	TSoftClassPtr<UDressUpNameTag> NameTagClass = TSoftClassPtr<UDressUpNameTag>(FSoftObjectPath(TEXT("/Game/DressUp/UI/WBP_NameTag.WBP_NameTag_C")));

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	TSoftObjectPtr<UDressUpBody> Body = TSoftObjectPtr<UDressUpBody>(FSoftObjectPath(TEXT("/Game/DressUp/Data/DA_Body_evrar.DA_Body_evrar")));

	/** Outfit worn at start instead of the catalog's DefaultItems, e.g. on the title screen. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up|Showcase")
	TArray<TObjectPtr<UDressUpItem>> ShowcaseItems;

	/** Idle played instead of the body's IdleAnim, e.g. on the title screen. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up|Showcase")
	TObjectPtr<UAnimationAsset> ShowcaseIdle = nullptr;

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

	/** Follows the head; always faces the camera at a fixed size. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UWidgetComponent> NameTag;

private:
	void FreezePose();

	UPROPERTY()
	TObjectPtr<UDressUpCatalog> LoadedCatalog;

	UPROPERTY()
	TObjectPtr<UDressUpBody> LoadedBody;

	UPROPERTY()
	TObjectPtr<UAnimationAsset> CurrentIdle;

	FTimerHandle PoseTimer;
};
