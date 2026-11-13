#include "DressUp/Scene/DressUpBackdrop.h"

#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "DressUp/Scene/DressUpScene.h"
#include "Engine/StaticMesh.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "Materials/MaterialInstanceDynamic.h"

ADressUpBackdrop::ADressUpBackdrop()
{
	Card = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Card"));
	SetRootComponent(Card);
	Card->SetCastShadow(false);
	Card->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

void ADressUpBackdrop::OnConstruction(const FTransform& Transform)
{
	// Editor only: the placement is saved with the level, so play just uses it.
	if (GetWorld() && !GetWorld()->IsGameWorld())
	{
		FitToCamera();
	}
	Super::OnConstruction(Transform);
}

void ADressUpBackdrop::ApplyScene(const UDressUpScene* Scene)
{
	UTexture2D* Picture = Scene ? Scene->Backdrop.Get() : nullptr;
	Card->SetVisibility(Picture != nullptr);
	if (!Picture)
	{
		return;
	}
	if (!CardMaterial)
	{
		CardMaterial = Card->CreateDynamicMaterialInstance(0);
	}
	if (CardMaterial)
	{
		CardMaterial->SetTextureParameterValue(PictureParameter, Picture);
		CardMaterial->SetScalarParameterValue(BrightnessParameter, Scene->BackdropBrightness);
	}
}

void ADressUpBackdrop::FitToCamera()
{
	if (!Camera || !Card->GetStaticMesh())
	{
		return;
	}
	const UCameraComponent* View = Camera->GetCameraComponent();
	const FTransform ViewTransform = View->GetComponentTransform();
	const FVector Forward = ViewTransform.GetUnitAxis(EAxis::X);
	const FVector Right = ViewTransform.GetUnitAxis(EAxis::Y);
	const FVector Up = ViewTransform.GetUnitAxis(EAxis::Z);

	// Half-angle tangents of the view: the field of view is horizontal at the camera's aspect
	// ratio, and the height stays the same in wider windows.
	const float TanY = FMath::Tan(FMath::DegreesToRadians(View->FieldOfView * 0.5f)) / FMath::Max(View->AspectRatio, 0.1f);
	const float TanX = TanY * CoverAspect;

	// The picture keeps its shape (the preview scene's picture; all backdrops share it).
	const UTexture2D* Picture = PreviewScene ? PreviewScene->Backdrop.Get() : nullptr;
	// The imported size: in the editor the GPU texture may still be compiling and report 1x1.
	const FIntPoint Size = Picture ? Picture->GetImportedSize() : FIntPoint::ZeroValue;
	const float PictureAspect = Size.Y > 0 ? float(Size.X) / float(Size.Y) : 16.0f / 9.0f;

	// Cover the widest window; the bottom edge sits at the bottom of the view.
	const float HalfWidth = FMath::Max(TanX, TanY * PictureAspect) * Overscan * Distance;
	const float HalfHeight = HalfWidth / PictureAspect;
	const float Bottom = -TanY * Overscan * Distance;
	const FVector Centre = ViewTransform.GetLocation() + Forward * Distance + Up * (Bottom + HalfHeight);

	// The plane faces +Z; turn that towards the camera, with its X along the view's right.
	const FVector MeshSize = Card->GetStaticMesh()->GetBoundingBox().GetSize();
	SetActorLocationAndRotation(Centre, FRotationMatrix::MakeFromXZ(Right, -Forward).Rotator());
	SetActorScale3D(FVector(2.0f * HalfWidth / FMath::Max(MeshSize.X, 1.0f), 2.0f * HalfHeight / FMath::Max(MeshSize.Y, 1.0f), 1.0f));
}
