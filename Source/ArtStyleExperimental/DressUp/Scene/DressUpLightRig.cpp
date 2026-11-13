#include "DressUp/Scene/DressUpLightRig.h"

#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "DressUp/Scene/DressUpScene.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkyLight.h"

ADressUpLightRig::ADressUpLightRig()
{
	SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
}

void ADressUpLightRig::ApplyScene(const UDressUpScene* Scene)
{
	if (!Scene)
	{
		return;
	}
	const FDressUpSceneLighting& Lighting = Scene->Lighting;
	if (Sun)
	{
		Sun->SetActorRotation(Lighting.SunRotation);
		if (UDirectionalLightComponent* Light = Cast<UDirectionalLightComponent>(Sun->GetLightComponent()))
		{
			Light->SetIntensity(Lighting.SunIntensity);
			Light->SetLightColor(Lighting.SunColor);
		}
	}
	if (Sky)
	{
		if (USkyLightComponent* Light = Sky->GetLightComponent())
		{
			Light->SetIntensity(Lighting.SkyIntensity);
			Light->SetLightColor(Lighting.SkyColor);
		}
	}
}
