// Plays one animation on the body, like PlayAnimation, and points the feet for shoes afterwards.

#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/AnimSingleNodeInstanceProxy.h"
#include "DressUpAnimInstance.generated.h"

/** Evaluates the animation, then turns both feet down by FootPitch around their own side axis. */
USTRUCT()
struct FDressUpAnimInstanceProxy : public FAnimSingleNodeInstanceProxy
{
	GENERATED_BODY()

	FDressUpAnimInstanceProxy() = default;

	explicit FDressUpAnimInstanceProxy(UAnimInstance* InAnimInstance)
		: FAnimSingleNodeInstanceProxy(InAnimInstance)
	{
	}

	virtual void PreUpdate(UAnimInstance* InAnimInstance, float DeltaSeconds) override;
	virtual bool Evaluate(FPoseContext& Output) override;

private:
	/** Copied from the instance on the game thread each update. */
	float FootPitch = 0.0f;
};

/**
 * VRoid points the foot about 8 degrees inside shoes (heel up, toes down) and its shoes are
 * shaped for that foot. The game plays the body's animations through this instance and sets
 * FootPitch from the worn shoes, so the bare foot takes the same pose and the shoe fits it.
 */
UCLASS(Transient, NotBlueprintable)
class ARTSTYLEEXPERIMENTAL_API UDressUpAnimInstance : public UAnimSingleNodeInstance
{
	GENERATED_BODY()

public:
	/** Degrees; positive turns the toes down. */
	UPROPERTY(Transient, BlueprintReadOnly, Category = "Dress Up")
	float FootPitch = 0.0f;

	/** Starts an animation from its beginning. */
	void Play(UAnimationAsset* Anim, bool bLoop);

protected:
	virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override;
};
