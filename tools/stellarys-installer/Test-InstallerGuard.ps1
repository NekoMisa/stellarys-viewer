param([Parameter(Mandatory=$true)][string]$FixtureRoot, [Parameter(Mandatory=$true)][string]$Report)
$ErrorActionPreference='Stop'
. "$PSScriptRoot\InstallerGuard.ps1" -Mode Library
if (Test-Path -LiteralPath $FixtureRoot) { throw 'Use a new, empty fixture root.' }
New-Item -ItemType Directory -Path $FixtureRoot | Out-Null
$results = New-Object 'System.Collections.Generic.List[object]'
function Check([string]$Name, [scriptblock]$Action, [bool]$Reject=$false) {
    $failed=$false; $message=''
    try { & $Action | Out-Null } catch { $failed=$true; $message=$_.Exception.Message }
    $passed=($failed -eq $Reject)
    $results.Add([pscustomobject]@{name=$Name;passed=$passed;rejected=$failed;message=$message})
    if (-not $passed) { throw "FAILED $Name : $message" }
}
function Folder([string]$Name, [string]$Marker='') {
    $path=Join-Path $FixtureRoot $Name
    New-Item -ItemType Directory -Path $path | Out-Null
    if ($Marker) { [IO.File]::WriteAllText((Join-Path $path 'stellarys-install.txt'),$Marker) }
    return $path
}
$empty=Folder 'empty'
$valid=Folder 'existing-kitty' "StellarysViewer`nBase=26.2.0.57700`nFix=0.1.0`n"
$unrelated=Folder 'unrelated'; [IO.File]::WriteAllText((Join-Path $unrelated 'keep.txt'),'Unrelated data')
$invalid=Folder 'invalid-marker' "FirestormFireKittyFix`n"
$blank=Folder 'blank-marker'; [IO.File]::WriteAllText((Join-Path $blank 'stellarys-install.txt'),'')
$nested=Folder 'nested-only'; New-Item -ItemType Directory -Path (Join-Path $nested 'another-folder') | Out-Null
$official=Folder 'official-bd'; [IO.File]::WriteAllText((Join-Path $official 'Black Dragon.exe'),'fixture')
$firestorm=Folder 'official-firestorm'; [IO.File]::WriteAllText((Join-Path $firestorm 'Firestorm.exe'),'fixture')
$mixed=Folder 'mixed' "StellarysViewer`n"; [IO.File]::WriteAllText((Join-Path $mixed 'Firestorm.exe'),'fixture')
$file=Join-Path $FixtureRoot 'not-a-folder'; [IO.File]::WriteAllText($file,'fixture')
Check 'new destination allowed' { Assert-KittyDestination (Join-Path $FixtureRoot 'new') }
Check 'empty directory allowed' { Assert-KittyDestination $empty }
Check 'legacy marker accepted for update' { Assert-KittyDestination $valid }
Check 'legacy marker accepted for uninstall' { Assert-KittyDestination $valid $true }
Check 'unrelated nonempty folder refused' { Assert-KittyDestination $unrelated } $true
Check 'folder with only subdirectories refused' { Assert-KittyDestination $nested } $true
Check 'official Black Dragon folder refused' { Assert-KittyDestination $official } $true
Check 'official Firestorm folder refused' { Assert-KittyDestination $firestorm } $true
Check 'mixed marked folder refused' { Assert-KittyDestination $mixed } $true
Check 'foreign marker refused' { Assert-KittyDestination $invalid } $true
Check 'blank marker refused' { Assert-KittyDestination $blank } $true
Check 'uninstall without marker refused' { Assert-KittyDestination $empty $true } $true
Check 'file destination refused' { Assert-KittyDestination $file } $true
Check 'drive root refused' { Assert-KittyDestination 'C:\' } $true
Check 'relative path refused' { Assert-KittyDestination 'relative-folder' } $true
Check 'UNC path refused' { Assert-KittyDestination '\\server\share\folder' } $true
Check 'case and trailing slash normalized' { if (-not (Test-SameInstallPath $valid.ToUpperInvariant() ($valid+'\'))) { throw 'Not matched' } }
$junction=Join-Path $FixtureRoot 'junction'
New-Item -ItemType Junction -Path $junction -Target $valid | Out-Null
Check 'junction destination refused' { Assert-KittyDestination $junction } $true
$inner=Folder 'inner-junction' "StellarysViewer`n"
New-Item -ItemType Junction -Path (Join-Path $inner 'redirect') -Target $empty | Out-Null
Check 'junction within installation refused' { Assert-KittyDestination $inner } $true

# Mock only process discovery, then run the exact production decision functions.
$script:FakeProcesses=@()
function Get-Process { param($Name,$ErrorAction) return $script:FakeProcesses }
Check 'no running viewer allowed' { Assert-KittyClosed $valid }
$script:FakeProcesses=@([pscustomobject]@{Path=(Join-Path $valid 'StellarysViewer.exe')})
Check 'running selected installation refused' { Assert-KittyClosed $valid } $true
Check 'running marked copy in another folder refused' { Assert-KittyClosed $empty } $true
$script:FakeProcesses=@([pscustomobject]@{Path=$null})
Check 'uninspectable viewer fails closed' { Assert-KittyClosed $valid } $true
$script:FakeProcesses=@()

# Registry adapter mocks ensure the same production code cannot modify HKLM/HKU
# while validating registration ownership and per-user migration decisions.
$script:FakeRegistry=@{}
$script:Removed=@()
$script:LoadedHives=@('S-1-5-21-1-2-3-1001','S-1-5-21-1-2-3-1002')
function Test-Path { param($LiteralPath,$PathType)
    if ($LiteralPath -like 'Registry::*') { return $script:FakeRegistry.ContainsKey($LiteralPath) }
    return Microsoft.PowerShell.Management\Test-Path -LiteralPath $LiteralPath
}
function Get-ItemProperty { param($LiteralPath) return [pscustomobject]@{InstallLocation=$script:FakeRegistry[$LiteralPath]} }
function Get-ChildItem { param($LiteralPath,[switch]$Force)
    if ($LiteralPath -eq 'Registry::HKEY_USERS') {
        return @($script:LoadedHives | ForEach-Object { [pscustomobject]@{PSChildName=$_;PSPath=('Registry::HKEY_USERS\'+$_)} })
    }
    return Microsoft.PowerShell.Management\Get-ChildItem -LiteralPath $LiteralPath -Force:$Force
}
function Remove-Item { param($LiteralPath,[switch]$Recurse)
    if ($LiteralPath -notlike 'Registry::HKEY_USERS\*\Software\*\StellarysViewer') { throw 'Unexpected removal target' }
    $script:Removed += $LiteralPath
    $script:FakeRegistry.Remove($LiteralPath)
}
$machine='Registry::HKEY_LOCAL_MACHINE\'+$script:UninstallKey
Check 'no machine registration allowed' { Assert-MachineRegistration $valid }
$script:FakeRegistry[$machine]=$valid.ToUpperInvariant()+'\'
Check 'same machine installation allowed' { Assert-MachineRegistration $valid }
$script:FakeRegistry[$machine]=$unrelated
Check 'other machine installation preserved and refused' { Assert-MachineRegistration $valid } $true
$matching='Registry::HKEY_USERS\'+$script:LoadedHives[0]+'\'+$script:UninstallKey
$other='Registry::HKEY_USERS\'+$script:LoadedHives[1]+'\'+$script:UninstallKey
$script:FakeRegistry[$matching]=$valid.ToUpperInvariant()+'\'
$script:FakeRegistry[$other]=$unrelated
Check 'matching legacy entry removed, different folder preserved' {
    Remove-MatchingLegacyRegistration $valid
    if ($script:Removed.Count -ne 1 -or $script:Removed[0] -ne $matching -or -not $script:FakeRegistry.ContainsKey($other)) { throw 'Registration ownership failure' }
}
[pscustomobject]@{tests=$results;count=$results.Count;all_passed=$true;registry_and_process_checks='Mocked adapters; production decision functions executed. No real registrations or processes modified.';filesystem_checks='Temporary workspace fixtures only; no installer installation or uninstall was run.'} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Report -Encoding UTF8
Write-Output "Passed $($results.Count) guard tests; no installed viewers changed."
