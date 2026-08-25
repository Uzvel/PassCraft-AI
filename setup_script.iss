[Setup]
AppName=PassCraft AI
AppVersion=1.0
AppPublisher=Ujjwal Chaudhary
DefaultDirName={autopf}\PassCraft AI
DefaultGroupName=PassCraft AI
OutputDir=.\Output
OutputBaseFilename=PassCraft_Setup
SetupIconFile=icon.ico
Compression=lzma2/max
SolidCompression=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\app\app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PassCraft AI"; Filename: "{app}\app.exe"
Name: "{autodesktop}\PassCraft AI"; Filename: "{app}\app.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\app.exe"; Description: "{cm:LaunchProgram,PassCraft AI}"; Flags: nowait postinstall skipifsilent