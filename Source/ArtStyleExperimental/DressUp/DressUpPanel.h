// UI base classes. Widget Blueprints only provide the layout; widgets are bound by name.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
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

/** Pastel pink-cream colours shared by the wardrobe widgets. */
namespace DressUpStyle
{
	inline const FLinearColor Cream(1.0f, 0.95f, 0.90f);
	inline const FLinearColor Pink(0.97f, 0.55f, 0.68f);
	inline const FLinearColor TextDark(0.30f, 0.17f, 0.22f);
}

/** One item tile: its icon, with its name as a tooltip. Click to put on or take off. */
UCLASS(Abstract)
class ARTSTYLEEXPERIMENTAL_API UDressUpItemButton : public UUserWidget
{
	GENERATED_BODY()

public:
	void Setup(UDressUpItem* InItem, UOutfitComponent* InOutfit);

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Look")
	FLinearColor IdleColor = DressUpStyle::Cream;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Look")
	FLinearColor EquippedColor = DressUpStyle::Pink;

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

/** A colour swatch. Tints the item picked most recently. */
UCLASS(Abstract)
class ARTSTYLEEXPERIMENTAL_API UDressUpColorButton : public UUserWidget
{
	GENERATED_BODY()

public:
	void Setup(FLinearColor InColor, UOutfitComponent* InOutfit);

protected:
	virtual void NativeConstruct() override;

	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UButton> Btn;

private:
	UFUNCTION()
	void HandleClicked();

	FLinearColor Color = FLinearColor::White;

	UPROPERTY()
	TObjectPtr<UOutfitComponent> Outfit;
};

/** A wardrobe tab header. Selecting it shows that tab's items in the panel. */
UCLASS(Abstract)
class ARTSTYLEEXPERIMENTAL_API UDressUpTabButton : public UUserWidget
{
	GENERATED_BODY()

public:
	void Setup(int32 InIndex, const FText& InName, UDressUpPanel* InPanel);
	void SetSelected(bool bSelected);

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Look")
	FLinearColor IdleColor = DressUpStyle::Cream;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Look")
	FLinearColor SelectedColor = DressUpStyle::Pink;

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

	UPROPERTY()
	TObjectPtr<UDressUpPanel> Panel;
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

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	TSoftClassPtr<UDressUpItemButton> ItemButtonClass = TSoftClassPtr<UDressUpItemButton>(FSoftObjectPath(TEXT("/Game/DressUp/UI/WBP_ItemButton.WBP_ItemButton_C")));

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	TSoftClassPtr<UDressUpColorButton> ColorButtonClass = TSoftClassPtr<UDressUpColorButton>(FSoftObjectPath(TEXT("/Game/DressUp/UI/WBP_ColorButton.WBP_ColorButton_C")));

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dress Up")
	TSoftClassPtr<UDressUpTabButton> TabButtonClass = TSoftClassPtr<UDressUpTabButton>(FSoftObjectPath(TEXT("/Game/DressUp/UI/WBP_TabButton.WBP_TabButton_C")));

protected:
	virtual void NativeConstruct() override;

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

private:
	UFUNCTION()
	void HandleReset();

	UPROPERTY()
	TObjectPtr<UOutfitComponent> Outfit;

	UPROPERTY()
	TObjectPtr<UDressUpCatalog> Catalog;

	UPROPERTY()
	TArray<TObjectPtr<UDressUpTabButton>> TabButtons;

	TArray<FDressUpTab> TabDefs;
	int32 CurrentTab = INDEX_NONE;
};
