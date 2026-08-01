// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class ArtStyleExperimental : ModuleRules
{
	public ArtStyleExperimental(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"AIModule",
			"StateTreeModule",
			"GameplayStateTreeModule",
			"UMG",
			"Slate"
		});

		PrivateDependencyModuleNames.AddRange(new string[] { });

		PublicIncludePaths.AddRange(new string[] {
			"ArtStyleExperimental",
			"ArtStyleExperimental/Variant_Platforming",
			"ArtStyleExperimental/Variant_Platforming/Animation",
			"ArtStyleExperimental/Variant_Combat",
			"ArtStyleExperimental/Variant_Combat/AI",
			"ArtStyleExperimental/Variant_Combat/Animation",
			"ArtStyleExperimental/Variant_Combat/Gameplay",
			"ArtStyleExperimental/Variant_Combat/Interfaces",
			"ArtStyleExperimental/Variant_Combat/UI",
			"ArtStyleExperimental/Variant_SideScrolling",
			"ArtStyleExperimental/Variant_SideScrolling/AI",
			"ArtStyleExperimental/Variant_SideScrolling/Gameplay",
			"ArtStyleExperimental/Variant_SideScrolling/Interfaces",
			"ArtStyleExperimental/Variant_SideScrolling/UI"
		});

		// Uncomment if you are using Slate UI
		// PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore" });

		// Uncomment if you are using online features
		// PrivateDependencyModuleNames.Add("OnlineSubsystem");

		// To include OnlineSubsystemSteam, add it to the plugins section in your uproject file with the Enabled attribute set to true
	}
}
