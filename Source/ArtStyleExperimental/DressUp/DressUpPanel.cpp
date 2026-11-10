#include "DressUp/DressUpPanel.h"

#include "Components/Button.h"
#include "Components/Image.h"
#include "Components/PanelWidget.h"
#include "Components/ScrollBox.h"
#include "Components/ScrollBoxSlot.h"
#include "Components/VerticalBoxSlot.h"
#include "Components/TextBlock.h"
#include "DressUp/DressUpCharacter.h"
#include "DressUp/DressUpData.h"
#include "DressUp/DressUpGameMode.h"
#include "DressUp/OutfitComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"

// --- Item button ---

void UDressUpItemButton::Setup(UDressUpItem* InItem, UOutfitComponent* InOutfit)
{
	Item = InItem;
	Outfit = InOutfit;
	if (Outfit)
	{
		Outfit->OnOutfitChanged.AddUniqueDynamic(this, &UDressUpItemButton::RefreshState);
	}
}

void UDressUpItemButton::NativeConstruct()
{
	Super::NativeConstruct();
	Btn->OnClicked.AddUniqueDynamic(this, &UDressUpItemButton::HandleClicked);
	if (Item)
	{
		SetToolTipText(Item->DisplayName);
		if (Label)
		{
			Label->SetText(Item->DisplayName);
		}
		if (Icon)
		{
			if (Item->Icon)
			{
				Icon->SetBrushFromTexture(Item->Icon);
			}
			else
			{
				Icon->SetVisibility(ESlateVisibility::Collapsed);
			}
		}
	}
	RefreshState();
}

void UDressUpItemButton::NativeDestruct()
{
	if (Outfit)
	{
		Outfit->OnOutfitChanged.RemoveDynamic(this, &UDressUpItemButton::RefreshState);
	}
	Super::NativeDestruct();
}

namespace
{
	/** Sound family of a slot; matches the wardrobe tabs. SourceAssets/Scripts/make_sfx.py makes them. */
	const TCHAR* SoundFamily(EDressUpSlot Slot)
	{
		switch (Slot)
		{
		case EDressUpSlot::Top:
		case EDressUpSlot::Outer:
			return TEXT("Top");
		case EDressUpSlot::Bottom:
			return TEXT("Bottom");
		case EDressUpSlot::Dress:
			return TEXT("Dress");
		case EDressUpSlot::Shoes:
		case EDressUpSlot::Socks:
			return TEXT("Shoes");
		case EDressUpSlot::Hair:
			return TEXT("Hair");
		default:
			return TEXT("Accessory");
		}
	}

	/** Plays /Game/DressUp/Audio/SFX/SFX_<Family>_On or _Off (routed to SC_Effects). */
	void PlayItemSound(const UObject* WorldContext, EDressUpSlot Slot, bool bPutOn)
	{
		const FString Name = FString::Printf(TEXT("SFX_%s_%s"), SoundFamily(Slot), bPutOn ? TEXT("On") : TEXT("Off"));
		const TSoftObjectPtr<USoundBase> Sound(FSoftObjectPath(FString::Printf(TEXT("/Game/DressUp/Audio/SFX/%s.%s"), *Name, *Name)));
		if (USoundBase* Loaded = Sound.LoadSynchronous())
		{
			UGameplayStatics::PlaySound2D(WorldContext, Loaded);
		}
	}
}

void UDressUpItemButton::HandleClicked()
{
	if (Outfit && Item)
	{
		Outfit->Toggle(Item);
		PlayItemSound(this, Item->Slot, Outfit->IsEquipped(Item));
	}
}

void UDressUpItemButton::RefreshState()
{
	if (Btn)
	{
		const bool bWorn = Outfit && Outfit->IsEquipped(Item);
		Btn->SetBackgroundColor(bWorn ? EquippedColor : IdleColor);
	}
}

// --- Colour button ---

void UDressUpColorButton::Setup(FLinearColor InColor, UOutfitComponent* InOutfit, int32 InVariant)
{
	Color = InColor;
	Outfit = InOutfit;
	Variant = InVariant;
}

void UDressUpColorButton::NativeConstruct()
{
	Super::NativeConstruct();
	Btn->OnClicked.AddUniqueDynamic(this, &UDressUpColorButton::HandleClicked);
	Btn->SetBackgroundColor(Color);
	RefreshSelected();
}

void UDressUpColorButton::RefreshSelected()
{
	if (!Btn)
	{
		return;
	}
	bool bSelected = false;
	if (Outfit && Outfit->GetLastItem())
	{
		if (Variant >= 0)
		{
			bSelected = Outfit->GetLastVariant() == Variant;
		}
		else
		{
			FLinearColor Worn;
			bSelected = Outfit->GetLastColor(Worn) && Worn.Equals(Color);
		}
	}
	if (bSelected == bShownSelected)
	{
		return;
	}
	bShownSelected = bSelected;

	if (!bHasBaseStyle)
	{
		BaseStyle = Btn->GetStyle();
		bHasBaseStyle = true;
	}
	FButtonStyle Style = BaseStyle;
	if (bSelected)
	{
		for (FSlateBrush* Brush : {&Style.Normal, &Style.Hovered, &Style.Pressed})
		{
			Brush->OutlineSettings.Width = 4.0f;
			Brush->OutlineSettings.Color = FSlateColor(DressUpStyle::SwatchRing);
		}
	}
	Btn->SetStyle(Style);
	Btn->SetRenderScale(FVector2D(bSelected ? 1.12f : 1.0f));
}

void UDressUpColorButton::HandleClicked()
{
	if (Outfit && Variant >= 0)
	{
		Outfit->SetVariantForLastSlot(Variant);
	}
	else if (Outfit)
	{
		Outfit->SetColorForLastSlot(Color);
	}
}

// --- Tab button ---

void UDressUpTabButton::Setup(int32 InIndex, const FText& InName, TFunction<void(int32)> InOnChosen)
{
	Index = InIndex;
	Name = InName;
	OnChosen = MoveTemp(InOnChosen);
}

void UDressUpTabButton::NativeConstruct()
{
	Super::NativeConstruct();
	Btn->OnClicked.AddUniqueDynamic(this, &UDressUpTabButton::HandleClicked);
	Label->SetText(Name);
	SetSelected(bIsSelected);
}

void UDressUpTabButton::SetSelected(bool bSelected)
{
	bIsSelected = bSelected;
	if (Btn)
	{
		Btn->SetBackgroundColor(bSelected ? SelectedColor : IdleColor);
	}
	if (Label)
	{
		Label->SetColorAndOpacity(FSlateColor(bSelected ? DressUpStyle::TextLight : DressUpStyle::TextDark));
	}
}

void UDressUpTabButton::HandleClicked()
{
	if (OnChosen)
	{
		OnChosen(Index);
	}
}

// --- Panel ---

void UDressUpPanel::Setup(UOutfitComponent* InOutfit, UDressUpCatalog* InCatalog)
{
	Outfit = InOutfit;
	Catalog = InCatalog;
	UClass* TabClass = TabButtonClass.LoadSynchronous();
	UClass* ColorClass = ColorButtonClass.LoadSynchronous();
	if (!Catalog || !TabClass || !ColorClass)
	{
		return;
	}

	// Only keep tabs that have something to show.
	TabDefs.Reset();
	for (const FDressUpTab& Tab : Catalog->Tabs.Num() > 0 ? Catalog->Tabs : DressUp::DefaultTabs())
	{
		const bool bHasItems = Catalog->AllItems.ContainsByPredicate([&Tab](const UDressUpItem* Item)
		{
			return Item && Tab.Slots.Contains(Item->Slot);
		});
		if (bHasItems)
		{
			TabDefs.Add(Tab);
		}
	}

	Tabs->ClearChildren();
	TabButtons.Reset();
	for (int32 Index = 0; Index < TabDefs.Num(); ++Index)
	{
		UDressUpTabButton* Button = CreateWidget<UDressUpTabButton>(this, TabClass);
		Button->Setup(Index, TabDefs[Index].Name, [WeakThis = TWeakObjectPtr<UDressUpPanel>(this)](int32 Chosen)
		{
			if (WeakThis.IsValid())
			{
				WeakThis->SelectTab(Chosen);
			}
		});
		Tabs->AddChild(Button);
		TabButtons.Add(Button);
	}

	bSwatchesBuilt = false;
	RefreshSwatches();
	if (Outfit)
	{
		Outfit->OnOutfitChanged.AddUniqueDynamic(this, &UDressUpPanel::RefreshSwatches);
	}

	BuildPoseChips(TabClass);
	SelectTab(0);
}

void UDressUpPanel::RefreshSwatches()
{
	UClass* ColorClass = ColorButtonClass.LoadSynchronous();
	if (!Catalog || !ColorClass || !Colors)
	{
		return;
	}
	UDressUpItem* Item = Outfit ? Outfit->GetLastItem() : nullptr;
	if (Item && Item->Variants.Num() < 2)
	{
		Item = nullptr;
	}
	// Same swatches: only their rings change. Rebuilding would destroy the swatch being clicked.
	if (!bSwatchesBuilt || SwatchItem.Get() != Item)
	{
		bSwatchesBuilt = true;
		SwatchItem = Item;
		Colors->ClearChildren();
		SwatchButtons.Reset();
		auto AddSwatch = [this, ColorClass](const FLinearColor& Color, int32 Variant)
		{
			UDressUpColorButton* Swatch = CreateWidget<UDressUpColorButton>(this, ColorClass);
			Swatch->Setup(Color, Outfit, Variant);
			Colors->AddChild(Swatch);
			SwatchButtons.Add(Swatch);
		};
		if (Item)
		{
			for (int32 Index = 0; Index < Item->Variants.Num(); ++Index)
			{
				AddSwatch(Item->Variants[Index].Swatch, Index);
			}
		}
		else
		{
			for (const FLinearColor& Color : Catalog->Palette)
			{
				AddSwatch(Color, INDEX_NONE);
			}
		}
	}
	for (UDressUpColorButton* Swatch : SwatchButtons)
	{
		Swatch->RefreshSelected();
	}
}

void UDressUpPanel::WrapListInScrollBox()
{
	if (!List || Cast<UScrollBox>(List->GetParent()))
	{
		return;
	}
	UPanelWidget* Parent = List->GetParent();
	if (!Parent)
	{
		return;
	}
	const int32 Index = Parent->GetChildIndex(List);
	UScrollBox* Scroll = NewObject<UScrollBox>(this, TEXT("ListScroll"));
	Scroll->SetAlwaysShowScrollbar(false);
	Scroll->SetScrollbarThickness(FVector2D(6.0f, 6.0f));
	// The list's slot is the template, so the scroll box keeps its size and padding in the layout.
	Parent->InsertChildAt(Index, Scroll, List->Slot);
	if (UVerticalBoxSlot* VSlot = Cast<UVerticalBoxSlot>(Scroll->Slot))
	{
		VSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
	}
	Scroll->AddChild(List);
}

void UDressUpPanel::BuildPoseChips(UClass* ChipClass)
{
	PoseButtons.Reset();
	if (!Poses)
	{
		return;
	}
	Poses->ClearChildren();
	const ADressUpCharacter* Character = Outfit ? Cast<ADressUpCharacter>(Outfit->GetOwner()) : nullptr;
	for (int32 Index = 0; Index < Catalog->IdleOptions.Num(); ++Index)
	{
		const FDressUpPoseOption& Option = Catalog->IdleOptions[Index];
		UDressUpTabButton* Chip = CreateWidget<UDressUpTabButton>(this, ChipClass);
		Chip->Setup(Index, Option.Name, [WeakThis = TWeakObjectPtr<UDressUpPanel>(this)](int32 Chosen)
		{
			if (WeakThis.IsValid())
			{
				WeakThis->SelectIdle(Chosen);
			}
		});
		Chip->SetSelected(Character && Character->GetIdle() == Option.Anim);
		Poses->AddChild(Chip);
		PoseButtons.Add(Chip);
	}
}

void UDressUpPanel::SelectIdle(int32 IdleIndex)
{
	ADressUpCharacter* Character = Outfit ? Cast<ADressUpCharacter>(Outfit->GetOwner()) : nullptr;
	if (!Character || !Catalog || !Catalog->IdleOptions.IsValidIndex(IdleIndex))
	{
		return;
	}
	Character->SetIdle(Catalog->IdleOptions[IdleIndex].Anim);
	for (int32 Index = 0; Index < PoseButtons.Num(); ++Index)
	{
		PoseButtons[Index]->SetSelected(Index == IdleIndex);
	}
}

void UDressUpPanel::SelectTab(int32 TabIndex)
{
	UClass* ItemClass = ItemButtonClass.LoadSynchronous();
	if (!Catalog || !ItemClass || !TabDefs.IsValidIndex(TabIndex))
	{
		return;
	}
	CurrentTab = TabIndex;
	for (int32 Index = 0; Index < TabButtons.Num(); ++Index)
	{
		TabButtons[Index]->SetSelected(Index == TabIndex);
	}

	List->ClearChildren();
	if (UScrollBox* Scroll = Cast<UScrollBox>(List->GetParent()))
	{
		Scroll->ScrollToStart();
	}
	const FDressUpTab& Tab = TabDefs[TabIndex];
	for (UDressUpItem* Item : Catalog->AllItems)
	{
		if (Item && Tab.Slots.Contains(Item->Slot))
		{
			UDressUpItemButton* Button = CreateWidget<UDressUpItemButton>(this, ItemClass);
			Button->Setup(Item, Outfit);
			List->AddChild(Button);
		}
	}
}

void UDressUpPanel::SetPlayerName(const FString& Name)
{
	if (NameText)
	{
		NameText->SetText(FText::FromString(Name));
	}
	if (NameHud)
	{
		// The name must not catch the mouse, or dragging across it would not turn the character.
		NameHud->SetVisibility(Name.IsEmpty() ? ESlateVisibility::Collapsed : ESlateVisibility::HitTestInvisible);
	}
}

void UDressUpPanel::NativeOnInitialized()
{
	Super::NativeOnInitialized();
	// Must run before the Slate tree is built: InsertChildAt does not update a live one.
	WrapListInScrollBox();
}

void UDressUpPanel::NativeConstruct()
{
	Super::NativeConstruct();
	ResetBtn->OnClicked.AddUniqueDynamic(this, &UDressUpPanel::HandleReset);
	if (FinishBtn)
	{
		FinishBtn->OnClicked.AddUniqueDynamic(this, &UDressUpPanel::HandleFinish);
	}
}

void UDressUpPanel::HandleFinish()
{
	if (ADressUpPlayerController* Controller = Cast<ADressUpPlayerController>(GetOwningPlayer()))
	{
		Controller->Finish();
	}
}

void UDressUpPanel::HandleReset()
{
	if (Outfit)
	{
		Outfit->ResetToDefault();
	}
}
