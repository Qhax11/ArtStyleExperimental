#include "DressUp/Scene/DressUpSceneEffect.h"

#include "DressUp/Scene/DressUpScene.h"
#include "NiagaraComponent.h"
#include "NiagaraSystem.h"

ADressUpSceneEffect::ADressUpSceneEffect()
{
	Effect = CreateDefaultSubobject<UNiagaraComponent>(TEXT("Effect"));
	SetRootComponent(Effect);
	Effect->SetAutoActivate(false);
}

void ADressUpSceneEffect::ApplyScene(const UDressUpScene* Scene)
{
	UNiagaraSystem* System = Scene ? Scene->Effect.Get() : nullptr;
	if (!System)
	{
		Effect->Deactivate();
		Effect->SetAsset(nullptr);
		return;
	}
	if (Effect->GetAsset() != System)
	{
		Effect->SetAsset(System);
	}
	// Reset so the new scene's effect starts fresh instead of carrying the old particles.
	Effect->Activate(true);
}
