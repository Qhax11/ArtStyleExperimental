#include "DressUp/DressUpPanel.h"

#include "Components/Button.h"
#include "Components/Image.h"
#include "Components/PanelWidget.h"
#include "Components/TextBlock.h"
#include "DressUp/DressUpCharacter.h"
#include "DressUp/DressUpData.h"
#include "DressUp/DressUpGameMode.h"
#include "DressUp/OutfitComponent.h"

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

void UDressUpItemButton::HandleClicked()
{
	if (Outfit && Item)
	{
		Outfit->Toggle(Item);
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

void UDressUpColorButton::Setup(FLinearColor InColor, UOutfitComponent* InOutfit)
{
	Color = InColor;
	Outfit = InOutfit;
}

void UDressUpColorButton::NativeConstruct()
{
	Super::NativeConstruct();
	Btn->OnClicked.AddUniqueDynamic(this, &UDressUpColorButton::HandleClicked);
	Btn->SetBackgroundColor(Color);
}

void UDressUpColorButton::HandleClicked()
{
	if (Outfit)
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
		Label->SetColorAndOpacity(FSlateColor(bSelected ? FLinearColor::White : DressUpStyle::TextDark));
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

	Colors->ClearChildren();
	for (const FLinearColor& Color : Catalog->Palette)
	{
		UDressUpColorButton* Swatch = CreateWidget<UDressUpColorButton>(this, ColorClass);
		Swatch->Setup(Color, Outfit);
		Colors->AddChild(Swatch);
	}

	BuildPoseChips(TabClass);
	SelectTab(0);
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
