#include "DressUp/UI/DressUpFinal.h"

#include "Algo/AllOf.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"
#include "DressUp/Core/DressUpData.h"
#include "DressUp/Game/DressUpGameMode.h"
#include "DressUp/Character/OutfitComponent.h"
#include "DressUp/Core/DressUpSound.h"

FText DressUp::PickMessage(const UDressUpCatalog* Catalog, const UOutfitComponent* Outfit)
{
	if (!Catalog)
	{
		return FText::GetEmpty();
	}
	TArray<const FDressUpMessage*> Matching;
	TArray<const FDressUpMessage*> General;
	for (const FDressUpMessage& Entry : Catalog->Messages)
	{
		if (Entry.Text.IsEmpty())
		{
			continue;
		}
		if (Entry.RequiredItems.IsEmpty() && Entry.RequiredSlots.IsEmpty())
		{
			General.Add(&Entry);
			continue;
		}
		const bool bItemsWorn = Algo::AllOf(Entry.RequiredItems, [Outfit](const UDressUpItem* Item)
		{
			return Item && Outfit && Outfit->IsEquipped(Item);
		});
		const bool bSlotsFilled = Algo::AllOf(Entry.RequiredSlots, [Outfit](EDressUpSlot Slot)
		{
			return Outfit && Outfit->GetEquipped(Slot) != nullptr;
		});
		if (bItemsWorn && bSlotsFilled)
		{
			Matching.Add(&Entry);
		}
	}
	const TArray<const FDressUpMessage*>& Pool = Matching.Num() > 0 ? Matching : General;
	return Pool.Num() > 0 ? Pool[FMath::RandRange(0, Pool.Num() - 1)]->Text : FText::GetEmpty();
}

void UDressUpFinalScreen::Setup(const FText& InMessage, ADressUpPlayerController* InController)
{
	MessageText = InMessage;
	Controller = InController;
}

void UDressUpFinalScreen::NativeConstruct()
{
	Super::NativeConstruct();
	Message->SetText(MessageText);
	PhotoBtn->OnClicked.AddUniqueDynamic(this, &UDressUpFinalScreen::HandlePhoto);
	ReplayBtn->OnClicked.AddUniqueDynamic(this, &UDressUpFinalScreen::HandleReplay);
	ShowStatus(FText::GetEmpty());
}

void UDressUpFinalScreen::ShowStatus(const FText& Text)
{
	if (Status)
	{
		Status->SetText(Text);
	}
}

void UDressUpFinalScreen::HandlePhoto()
{
	if (Controller)
	{
		Controller->TakePhoto();
	}
}

void UDressUpFinalScreen::HandleReplay()
{
	DressUp::PlayClick(this);
	if (Controller)
	{
		Controller->Replay();
	}
}
