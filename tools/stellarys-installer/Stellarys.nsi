Unicode true
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"
!include "nsDialogs.nsh"
Var RemoveSettings
Var RemoveCache
Var SettingsCheck
Var CacheCheck
Var DataArgs
!define PRODUCT "Stellarys Viewer"
!define KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\StellarysViewer"
Name "${PRODUCT} 0.1.0 (based on Firestorm 7.2.4.80712)"
OutFile "${OUTPUT}"
InstallDir "$PROGRAMFILES64\StellarysViewer"
InstallDirRegKey HKLM "${KEY}" "InstallLocation"
RequestExecutionLevel admin
SetCompressor /SOLID lzma
SetCompressorDictSize 32
BrandingText "Stellarys Viewer 0.1.0 (based on Firestorm 7.2.4.80712)"
VIProductVersion "0.1.0.0"
VIAddVersionKey /LANG=1033 "ProductName" "Stellarys Viewer"
VIAddVersionKey /LANG=1033 "FileDescription" "Stellarys Viewer 0.1.0 Setup"
VIAddVersionKey /LANG=1033 "FileVersion" "0.1.0.0"
VIAddVersionKey /LANG=1033 "ProductVersion" "0.1.0 (based on Firestorm 7.2.4.80712)"
VIAddVersionKey /LANG=1033 "LegalCopyright" "Original viewer and libraries: their respective authors."
Var GuardResult
Var GuardMessage
!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TEXT "Stellarys Viewer 0.1.0 (based on Firestorm 7.2.4.80712), with the AMD flicker fix and permission-based local poser.$\r$\n$\r$\nInstalls for all Windows users. Each user has a separate Stellarys profile and cache. Existing Firestorm, Black Dragon and prototype profiles are not changed.$\r$\n$\r$\nUpdate checks are built in; downloading and installation require your approval."
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${PAYLOAD}\LICENSE.txt"
!define MUI_PAGE_HEADER_TEXT "Choose installation folder"
!define MUI_PAGE_HEADER_SUBTEXT "Select an empty folder or a marked Stellarys installation to update."
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE ValidateDestination
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_TEXT "Stellarys is installed. Start it from the Start menu or desktop shortcut.$\r$\n$\r$\nUse Help > Check for Updates to check for releases or change startup checking. Settings and cache are retained during updates. See README-Stellarys.txt for details."
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
UninstPage custom un.DataPage un.DataPageLeave
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

!macro Guard MODE
 InitPluginsDir
 File /oname=$PLUGINSDIR\InstallerGuard.ps1 "${GUARD}"
 ; Run the built-in 64-bit Windows PowerShell for the 64-bit registry view.
 ; ExecutionPolicy applies only to this helper process; no policy is changed.
 nsExec::ExecToStack /TIMEOUT=60000 '"$WINDIR\Sysnative\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$PLUGINSDIR\InstallerGuard.ps1" -Mode ${MODE} -Destination "$INSTDIR"'
 Pop $GuardResult
 Pop $GuardMessage
 ${If} $GuardResult != 0
  MessageBox MB_OK|MB_ICONSTOP "$GuardMessage$\r$\n$\r$\nSetup cannot safely continue." /SD IDOK
  SetErrorLevel 3
  Abort
 ${EndIf}
!macroend

Function .onInit
 SetShellVarContext all
 SetRegView 64
 ReadRegDWORD $0 HKLM "SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" "Release"
 ${If} $0 < 528040
  MessageBox MB_OK|MB_ICONSTOP "Stellarys requires Microsoft .NET Framework 4.8 or newer for its updater. Install it through Windows Update and run Setup again." /SD IDOK
  SetErrorLevel 3
  Abort
 ${EndIf}
 ${IfNot} ${RunningX64}
  MessageBox MB_OK|MB_ICONSTOP "This viewer requires 64-bit Windows." /SD IDOK
  SetErrorLevel 3
  Abort
 ${EndIf}
FunctionEnd

Function ValidateDestination
 !insertmacro Guard Install
FunctionEnd

Section "Viewer"
 ; Also validate here: silent installs and /D= must not bypass the checks.
 Call ValidateDestination
 SetOverwrite on
 ClearErrors
 SetOutPath "$INSTDIR"
 !include "${INSTALL_FILES}"
 IfErrors copy_failed
 WriteUninstaller "$INSTDIR\Uninstall.exe"
 IfErrors copy_failed
 CreateDirectory "$SMPROGRAMS\${PRODUCT}"
 SetOutPath "$INSTDIR"
 CreateShortCut "$SMPROGRAMS\${PRODUCT}\${PRODUCT}.lnk" "$INSTDIR\StellarysViewer.exe" "" "$INSTDIR\StellarysViewer.exe"
 CreateShortCut "$SMPROGRAMS\${PRODUCT}\Read me.lnk" "$INSTDIR\README-Stellarys.txt"
 CreateShortCut "$SMPROGRAMS\${PRODUCT}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
 CreateShortCut "$DESKTOP\${PRODUCT}.lnk" "$INSTDIR\StellarysViewer.exe" "" "$INSTDIR\StellarysViewer.exe"
 WriteRegStr HKLM "${KEY}" "DisplayName" "Stellarys Viewer 0.1.0"
 WriteRegStr HKLM "${KEY}" "DisplayVersion" "0.1.0"
 WriteRegStr HKLM "${KEY}" "BaseViewerVersion" "7.2.4.80712"
 WriteRegStr HKLM "${KEY}" "StellarysVersion" "0.1.0"
 WriteRegStr HKLM "${KEY}" "InstallerRevision" "1"
 WriteRegStr HKLM "${KEY}" "Publisher" "Stellarys (unofficial build)"
 WriteRegStr HKLM "${KEY}" "InstallLocation" "$INSTDIR"
 WriteRegStr HKLM "${KEY}" "DisplayIcon" "$INSTDIR\StellarysViewer.exe"
 WriteRegStr HKLM "${KEY}" "UninstallString" '$\"$INSTDIR\Uninstall.exe$\"'
 WriteRegStr HKLM "${KEY}" "QuietUninstallString" '$\"$INSTDIR\Uninstall.exe$\" /S'
 WriteRegDWORD HKLM "${KEY}" "NoModify" 1
 WriteRegDWORD HKLM "${KEY}" "NoRepair" 1
 IfErrors registration_failed
 ; Remove old per-user entries only AFTER copying and registering succeeded.
 ; The guard compares canonical paths and examines loaded user hives, so an
 ; installation in any other folder is left entirely alone.
 !insertmacro Guard CleanupLegacy
 Goto done
 copy_failed:
  MessageBox MB_OK|MB_ICONSTOP "Application files could not be written. Close the viewer and retry. No old per-user uninstall registration has been removed." /SD IDOK
  SetErrorLevel 4
  Abort
 registration_failed:
  MessageBox MB_OK|MB_ICONSTOP "The machine-wide installation could not be registered. Retry with administrator permission. Old per-user entries have been preserved." /SD IDOK
  SetErrorLevel 5
  Abort
 done:
SectionEnd

Function un.onInit
 StrCpy $RemoveSettings 0
 StrCpy $RemoveCache 0
 SetShellVarContext all
 SetRegView 64
 !insertmacro Guard Uninstall
FunctionEnd


Function un.DataPage
 !insertmacro MUI_HEADER_TEXT "Optional data removal" "Leave both boxes unchecked to keep your settings and cache."
 nsDialogs::Create 1018
 Pop $0
 SetShellVarContext current
 ${NSD_CreateLabel} 0 0 100% 42u "Only data for this Windows account is affected: $PROFILE$\r$\nIf you elevated as another account, these are that administrator's folders. Other users and older viewer profiles are never removed."
 Pop $0
 ${NSD_CreateCheckbox} 0 48u 100% 22u "Remove Stellarys settings, saved sign-ins and logs"
 Pop $SettingsCheck
 ${NSD_SetState} $SettingsCheck $RemoveSettings
 ${NSD_CreateLabel} 12u 72u 100% 22u "$APPDATA\Stellarys_x64"
 Pop $0
 ${NSD_CreateCheckbox} 0 98u 100% 22u "Remove Stellarys default cache and downloaded updates"
 Pop $CacheCheck
 ${NSD_SetState} $CacheCheck $RemoveCache
 ${NSD_CreateLabel} 12u 122u 100% 22u "$LOCALAPPDATA\Stellarys_x64"
 Pop $0
 SetShellVarContext all
 nsDialogs::Show
FunctionEnd
Function un.DataPageLeave
 ${NSD_GetState} $SettingsCheck $RemoveSettings
 ${NSD_GetState} $CacheCheck $RemoveCache
FunctionEnd
Function un.RemoveOptionalData
 StrCpy $DataArgs ""
 ${If} $RemoveSettings == ${BST_CHECKED}
  StrCpy $DataArgs "$DataArgs -Settings"
 ${EndIf}
 ${If} $RemoveCache == ${BST_CHECKED}
  StrCpy $DataArgs "$DataArgs -Cache"
 ${EndIf}
 ${If} $DataArgs != ""
  InitPluginsDir
  File /oname=$PLUGINSDIR\RemoveUserData.ps1 "${REMOVE_DATA}"
  nsExec::ExecToStack /TIMEOUT=120000 '"$WINDIR\Sysnative\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$PLUGINSDIR\RemoveUserData.ps1" $DataArgs'
  Pop $GuardResult
  Pop $GuardMessage
  ${If} $GuardResult != 0
   MessageBox MB_OK|MB_ICONSTOP "Data removal stopped: $GuardMessage$\r$\nApplication files have not been removed. Retry with both data options unchecked to preserve remaining data." /SD IDOK
   SetErrorLevel 6
   Abort
  ${EndIf}
 ${EndIf}
FunctionEnd

Section "Uninstall"
 ; Recheck just before removal in case the viewer started at the confirm page.
 !insertmacro Guard Uninstall
 Call un.RemoveOptionalData
 ; Explicit package files only. No recursive deletion, no profile/cache paths.
 !include "${UNINSTALL_FILES}"
 Delete "$INSTDIR\Uninstall.exe"
 RMDir "$INSTDIR"
 ; An obsolete uninstaller in another folder cannot unregister the new copy.
 ReadRegStr $0 HKLM "${KEY}" "InstallLocation"
 ${If} $0 != ""
  GetFullPathName $0 "$0"
  GetFullPathName $1 "$INSTDIR"
  ${If} $0 == $1
   Delete "$DESKTOP\${PRODUCT}.lnk"
   Delete "$SMPROGRAMS\${PRODUCT}\${PRODUCT}.lnk"
   Delete "$SMPROGRAMS\${PRODUCT}\Read me.lnk"
   Delete "$SMPROGRAMS\${PRODUCT}\Uninstall.lnk"
   RMDir "$SMPROGRAMS\${PRODUCT}"
   DeleteRegKey HKLM "${KEY}"
  ${EndIf}
 ${EndIf}
SectionEnd
