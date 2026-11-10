#include "DressUp/DressUpAnimInstance.h"

#include "Animation/AnimNodeBase.h"

namespace
{
	const FName FootBones[] = {TEXT("J_Bip_L_Foot"), TEXT("J_Bip_R_Foot")};
}

void FDressUpAnimInstanceProxy::PreUpdate(UAnimInstance* InAnimInstance, float DeltaSeconds)
{
	FAnimSingleNodeInstanceProxy::PreUpdate(InAnimInstance, DeltaSeconds);
	if (const UDressUpAnimInstance* Instance = Cast<UDressUpAnimInstance>(InAnimInstance))
	{
		FootPitch = Instance->FootPitch;
	}
}

bool FDressUpAnimInstanceProxy::Evaluate(FPoseContext& Output)
{
	const bool bResult = FAnimSingleNodeInstanceProxy::Evaluate(Output);
	if (FMath::IsNearlyZero(FootPitch))
	{
		return bResult;
	}
	const FBoneContainer& Bones = Output.Pose.GetBoneContainer();
	// VRM4U bones keep an identity reference rotation, so a bone's own X is the body's side axis.
	// A negative turn about it lowers the toes (checked in game with 40 degrees).
	const FQuat Pitch(FVector::XAxisVector, FMath::DegreesToRadians(-FootPitch));
	for (const FName& Name : FootBones)
	{
		const int32 MeshIndex = Bones.GetReferenceSkeleton().FindBoneIndex(Name);
		if (MeshIndex == INDEX_NONE)
		{
			continue;
		}
		const FCompactPoseBoneIndex Index = Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(MeshIndex));
		if (!Index.IsValid())
		{
			continue;
		}
		FTransform& Local = Output.Pose[Index];
		Local.SetRotation((Local.GetRotation() * Pitch).GetNormalized());
	}
	return bResult;
}

void UDressUpAnimInstance::Play(UAnimationAsset* Anim, bool bLoop)
{
	SetAnimationAsset(Anim, bLoop);
	SetPosition(0.0f, false);
	SetPlaying(true);
}

FAnimInstanceProxy* UDressUpAnimInstance::CreateAnimInstanceProxy()
{
	return new FDressUpAnimInstanceProxy(this);
}
