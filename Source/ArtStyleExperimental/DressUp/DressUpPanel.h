// UI base classes. Widget Blueprints only provide the layout; widgets are bound by name.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Styling/SlateTypes.h"
#include "DressUp/DressUpTypes.h"
#include "DressUpPanel.generated.h"

class UButton;
class UDressUpCatalog;
class UDressUpItem;
class UDressUpPanel;
class UImage;
class UOutfitComponent;
class UPanelWidget;
class UTextBlock;

/**
 * Colours shared by the wardrobe widgets. Nothing here is white: white belongs to the clothes
 * and the white swatch, so white icons stay visible on their tiles.
 */
namespace DressUpStyle
{
	inline const FLinearColor Tile(0.693f, 0.366f, 0.497f);
	inline const FLinearColor Accent(0.397f, 0.050f, 0.150f);
	inline const FLinearColor TextDark(0.102f, 0.017f, 0.051f);
	inline const FLinearColor TextLight(1.0f, 0.716f, 0.807f);
	/** Ring around the selected swatch; dark enough to show on every swatch colour. */
	inline const FLinearColor SwatchRing(0.10f, 0.01f, 0.04f);
}

/** One item tile: its icon, with its name as a tooltip. Click to put on or take off. */
UCLASS(Abstract)
class ARTSTYLEEXPERIMENTAL_API UDressUpItemButton : public UUserWidget
{
	GENERATED_BODY()

public:
	void Setup(UDressUpItem* InItem, UOutfitComponent* InOutfit);

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Look")
	FLinearColor IdleColor = DressUpStyle::Tile;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Look")
	FLinearColor EquippedColor = DressUpStyle::Accent;

protected:
	virtual void NativeConstruct() override;
	virtual void NativeDestruct() override;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> Btn;

	/** Shows the item's icon. */
	UPROPERTY(meta = (BindWidgetOptional))
	TObjectPtr<UImage> Icon;

	/** Shows the item's name, for items without an icon or layouts that want both. */
	UPROPERTY(meta = (BindWidgetOptional))
	TObjectPtr<UTextBlock> Label;

private:
	UFUNCTION()
	void HandleClicked();

	/** Highlights the tile while its item is worn. */
	UFUNCTION()
	void RefreshState();

	UPROPERTY()
	TObjectPtr<UDressUpItem> Item;

	UPROPERTY()
	TObjectPtr<UOutfitComponent> Outfit;
};

/** A colour swatch. Tints the item picked most recently, or switches it to one of its variants. */
UCLASS(Abstract)
class ARTSTYLEEXPERIMENTAL_API UDressUpColorButton : public UUserWidget
{
	GENERATED_BODY()

public:
	/** InVariant >= 0 makes the swatch pick that variant instead of tinting. */
	void Setup(FLinearColor InColor, UOutfitComponent* InOutfit, int32 InVariant = INDEX_NONE);

	/** Shows a ring when this swatch is what the item picked last currently wears. */
	void RefreshSelected();

protected:
	virtual void NativeConstruct() override;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> Btn;

private:
	UFUNCTION()
	void HandleClicked();

	FLinearColor Color = FLinearColor::White;
	int32 Variant = INDEX_NONE;
	bool bShownSelected = false;
	bool bHasBaseStyle = false;
	FButtonStyle BaseStyle;

	UPROPERTY()
	TObjectPtr<UOutfitComponent> Outfit;
};

/** A text chip with a selected state: wardrobe tab headers and idle pose choices. */
UCLASS(Abstract)
class ARTSTYLEEXPERIMENTAL_API UDressUpTabButton : public UUserWidget
{
	GENERATED_BODY()

public:
	/** OnChosen receives InIndex when the chip is clicked. */
	void Setup(int32 InIndex, const FText& InName, TFunction<void(int32)> InOnChosen);
	void SetSelected(bool bSelected);

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Look")
	FLinearColor IdleColor = DressUpStyle::Tile;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Look")
	FLinearColor SelectedColor = DressUpStyle::Accent;

protected:
	virtual void NativeConstruct() override;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> Btn;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UTextBlock> Label;

private:
	UFUNCTION()
	void HandleClicked();

	int32 Index = INDEX_NONE;
	FText Name;
	bool bIsSelected = false;
	TFunction<void(int32)> OnChosen;
};

/** The wardrobe panel: tabs, the current tab's item tiles, colour swatches and a reset button. */
UCLASS(Abstract)
class ARTSTYLEEXPERIMENTAL_API UDressUpPanel : public UUserWidget
{
	GENERATED_BODY()

public:
	/** Builds the tabs and swatches from the catalog and opens the first tab. Call before adding to the viewport. */
	void Setup(UOutfitComponent* InOutfit, UDressUpCatalog* InCatalog);

	/** Shows the items of one tab. */
	void SelectTab(int32 TabIndex);

	/** Loops one of the catalog's idle options on the character. */
	void SelectIdle(int32 IdleIndex);

	/** Shows the player's name on the HUD, or hides it when the name is empty. */
	void SetPlayerName(const FString& Name);

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	TSoftClassPtr<UDressUpItemButton> ItemButtonClass = TSoftClassPtr<UDressUpItemButton>(FSoftObjectPath(TEXT("/Game/DressUp/UI/WBP_ItemButton.WBP_ItemButton_C")));

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	TSoftClassPtr<UDressUpColorButton> ColorButtonClass = TSoftClassPtr<UDressUpColorButton>(FSoftObjectPath(TEXT("/Game/DressUp/UI/WBP_ColorButton.WBP_ColorButton_C")));

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	TSoftClassPtr<UDressUpTabButton> TabButtonClass = TSoftClassPtr<UDressUpTabButton>(FSoftObjectPath(TEXT("/Game/DressUp/UI/WBP_TabButton.WBP_TabButton_C")));

protected:
	virtual void NativeOnInitialized() override;
	virtual void NativeConstruct() override;
	virtual void NativeDestruct() override;

	/** Holds the tab headers. */
	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UPanelWidget> Tabs;

	/** Holds the item tiles of the selected tab. A wrap box gives a grid. */
	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UPanelWidget> List;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UPanelWidget> Colors;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> ResetBtn;

	/** Holds the idle pose chips. */
	UPROPERTY(meta = (BindWidgetOptional))
	TObjectPtr<UPanelWidget> Poses;

	UPROPERTY(meta = (BindWidgetOptional))
	TObjectPtr<UButton> FinishBtn;

	/** Frame of the player's name; hidden while there is no name. */
	UPROPERTY(meta = (BindWidgetOptional))
	TObjectPtr<UWidget> NameHud;

	UPROPERTY(meta = (BindWidgetOptional))
	TObjectPtr<UTextBlock> NameText;

	/** "Drag to turn" hint, bottom right. It pulses now and then so it gets noticed. */
	UPROPERTY(meta = (BindWidgetOptional))
	TObjectPtr<UWidget> RotateHint;

	/** Seconds between pulses of the rotate hint, and how long one pulse lasts. */
	UPROPERTY(EditAnywhere, Category = "Dress Up|Hint")
	float HintPulseInterval = 7.0f;

	UPROPERTY(EditAnywhere, Category = "Dress Up|Hint")
	float HintPulseDuration = 1.0f;

	/** How much the hint grows at the top of a pulse (0.15 = 15%). */
	UPROPERTY(EditAnywhere, Category = "Dress Up|Hint")
	float HintPulseGrowth = 0.15f;

private:
	UFUNCTION()
	void HandleReset();

	UFUNCTION()
	void HandleFinish();

	void BuildPoseChips(UClass* ChipClass);

	/** Shows the variants of the item picked last, or the shared palette when it has none. */
	UFUNCTION()
	void RefreshSwatches();

	void PulseRotateHint();

	FTimerHandle HintTimer;
	float HintClock = 0.0f;

	/** Puts the item list in a scroll box when the layout did not. */
	void WrapListInScrollBox();

	UPROPERTY()
	TObjectPtr<UOutfitComponent> Outfit;

	UPROPERTY()
	TObjectPtr<UDressUpCatalog> Catalog;

	UPROPERTY()
	TArray<TObjectPtr<UDressUpTabButton>> TabButtons;

	UPROPERTY()
	TArray<TObjectPtr<UDressUpTabButton>> PoseButtons;

	UPROPERTY()
	TArray<TObjectPtr<UDressUpColorButton>> SwatchButtons;

	TArray<FDressUpTab> TabDefs;
	int32 CurrentTab = INDEX_NONE;

	/** Item whose variants the swatches show; null while they show the palette. */
	TWeakObjectPtr<UDressUpItem> SwatchItem;
	bool bSwatchesBuilt = false;
};
