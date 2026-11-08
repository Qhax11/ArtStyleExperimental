@echo off
rem Packages the game for Windows into Desktop\PackagesForDressUp.
rem The cooker gets its own MCP port, so this works while the editor (holding port 8000) is open.
rem Close the editor first if C++ changed and the editor DLL is not built yet.
call "C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun ^
 -project="%~dp0ArtStyleExperimental.uproject" -target=ArtStyleExperimental -platform=Win64 -clientconfig=Development ^
 -nop4 -utf8output -build -cook -stage -pak -iostore -compressed -package -prereqs ^
 -archive -archivedirectory="%USERPROFILE%\OneDrive\Desktop\PackagesForDressUp" ^
 -unrealexe="C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" ^
 -nocompileeditor -skipbuildeditor -AdditionalCookerOptions=-ModelContextProtocolPort=8013
pause
