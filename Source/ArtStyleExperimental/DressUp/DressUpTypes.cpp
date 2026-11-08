#include "DressUp/DressUpTypes.h"

FName DressUp::RegionSlotName(EBodyRegion Region)
{
	const FString Name = StaticEnum<EBodyRegion>()->GetNameStringByValue(static_cast<int64>(Region));
	return FName(*(TEXT("Region_") + Name));
}

TArray<FDressUpTab> DressUp::DefaultTabs()
{
	auto Make = [](const TCHAR* Name, std::initializer_list<EDressUpSlot> Slots)
	{
		FDressUpTab Tab;
		Tab.Name = FText::FromString(Name);
		Tab.Slots = Slots;
		return Tab;
	};
	return {
		Make(TEXT("Üst"), {EDressUpSlot::Top, EDressUpSlot::Outer}),
		Make(TEXT("Alt"), {EDressUpSlot::Bottom, EDressUpSlot::Socks}),
		Make(TEXT("Elbise"), {EDressUpSlot::Dress}),
		Make(TEXT("Ayakkabı"), {EDressUpSlot::Shoes}),
		Make(TEXT("Saç"), {EDressUpSlot::Hair}),
		Make(TEXT("Aksesuar"), {EDressUpSlot::Glasses, EDressUpSlot::Hat, EDressUpSlot::Gloves, EDressUpSlot::Earrings, EDressUpSlot::Necklace, EDressUpSlot::Bag}),
	};
}
