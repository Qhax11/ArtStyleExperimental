// The closing screen: the personal message, a photo button and a replay button.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "DressUpFinal.generated.h"

class ADressUpPlayerController;
class UButton;
class UDressUpCatalog;
class UOutfitComponent;
class UTextBlock;

namespace DressUp
{
	/**
	 * Picks a closing message at random. Messages whose conditions all match the outfit
	 * win; when none does, one without conditions is used. Returns empty text if the
	 * catalog has no fitting message.
	 */
	ARTSTYLEEXPERIMENTAL_API FText PickMessage(const UDressUpCatalog* Catalog, const UOutfitComponent* Outfit);
}

UCLASS(Abstract)
class ARTSTYLEEXPERIMENTAL_API UDressUpFinalScreen : public UUserWidget
{
	GENERATED_BODY()

public:
	void Setup(const FText& InMessage, ADressUpPlayerController* InController);

	/** Short feedback under the message, e.g. where the photo was saved. */
	void ShowStatus(const FText& Text);

protected:
	virtual void NativeConstruct() override;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UTextBlock> Message;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> PhotoBtn;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> ReplayBtn;

	UPROPERTY(meta = (BindWidgetOptional))
	TObjectPtr<UTextBlock> Status;

private:
	UFUNCTION()
	void HandlePhoto();

	UFUNCTION()
	void HandleReplay();

	FText MessageText;

	UPROPERTY()
	TObjectPtr<ADressUpPlayerController> Controller;
};
