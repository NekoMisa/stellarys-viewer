; SPDX-License-Identifier: LGPL-2.1-only
; The generated file include and embedded manifest have exactly the same order.
Var ForceRepair
Var InstallPlanHandle
Var InstallPlanByte
Var FilesReplaced
Var FilesUnchanged

Function PrepareApplicationFiles
 InitPluginsDir
 File /oname=$PLUGINSDIR\InstallerFiles.exe "${FILE_PLANNER}"
 File /oname=$PLUGINSDIR\application-files.json "${FILE_MANIFEST}"
 DetailPrint "Checking installed application files..."
 nsExec::ExecToStack /TIMEOUT=600000 '"$PLUGINSDIR\InstallerFiles.exe" plan "$INSTDIR" "$PLUGINSDIR\application-files.json" "$PLUGINSDIR\application-plan.bin" "$ForceRepair"'
 Pop $0
 Pop $1
 ${If} $0 != 0
  MessageBox MB_OK|MB_ICONSTOP "Application file checks failed: $1$\r$\nNo application files have been replaced." /SD IDOK
  SetErrorLevel 7
  Abort
 ${EndIf}
 DetailPrint "$1"
 ClearErrors
 FileOpen $InstallPlanHandle "$PLUGINSDIR\application-plan.bin" r
 ${If} ${Errors}
  SetErrorLevel 7
  Abort "Could not open the application file plan."
 ${EndIf}
 StrCpy $FilesReplaced 0
 StrCpy $FilesUnchanged 0
FunctionEnd

Function NextApplicationFile
 ClearErrors
 FileReadByte $InstallPlanHandle $InstallPlanByte
 ${If} ${Errors}
  SetErrorLevel 7
  Abort "Incomplete application file plan. Run Setup again."
 ${EndIf}
 ${If} $InstallPlanByte == 48
  IntOp $FilesReplaced $FilesReplaced + 1
 ${ElseIf} $InstallPlanByte == 49
  IntOp $FilesUnchanged $FilesUnchanged + 1
 ${Else}
  SetErrorLevel 7
  Abort "Invalid application file plan. Run Setup again."
 ${EndIf}
FunctionEnd

Function CheckApplicationFileWrite
 ${If} ${Errors}
  SetErrorLevel 4
  Abort "An application file could not be written. Close Stellarys and retry Setup."
 ${EndIf}
FunctionEnd

; Keep per-file bytecode small: shared checks are compiled only once.
!macro StellarysFile SOURCE DIRECTORY
 Call NextApplicationFile
 ${If} $InstallPlanByte == 48
  SetOutPath "${DIRECTORY}"
  File "${SOURCE}"
  Call CheckApplicationFileWrite
 ${EndIf}
!macroend

Function VerifyApplicationFiles
 ClearErrors
 FileReadByte $InstallPlanHandle $InstallPlanByte
 ${IfNot} ${Errors}
  FileClose $InstallPlanHandle
  SetErrorLevel 7
  Abort "Application file plan does not match this installer."
 ${EndIf}
 FileClose $InstallPlanHandle
 DetailPrint "Checking the completed application..."
 nsExec::ExecToStack /TIMEOUT=600000 '"$PLUGINSDIR\InstallerFiles.exe" verify "$INSTDIR" "$PLUGINSDIR\application-files.json"'
 Pop $0
 Pop $1
 ${If} $0 != 0
  MessageBox MB_OK|MB_ICONSTOP "$1$\r$\nSetup could not verify the completed application. Retry with Full reinstall / repair." /SD IDOK
  SetErrorLevel 7
  Abort
 ${EndIf}
 DetailPrint "$1"
 DetailPrint "Replaced $FilesReplaced application files; kept $FilesUnchanged identical files."
 ClearErrors
FunctionEnd
