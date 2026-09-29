param([Parameter(Mandatory=$true)][string]$FixtureRoot)
$ErrorActionPreference='Stop'
. "$PSScriptRoot\RemoveUserData.ps1" -Library
if (Test-Path -LiteralPath $FixtureRoot) { throw 'Fixture root must be new.' }
New-Item -ItemType Directory -Path $FixtureRoot | Out-Null
$base=Join-Path $FixtureRoot 'Roaming'
$target=Join-Path $base 'Stellarys_x64'
$old=Join-Path $base 'FirestormFireKittyPoser_x64'
New-Item -ItemType Directory -Path "$target\user_settings",$old -Force | Out-Null
Set-Content -LiteralPath "$target\user_settings\dummy.xml" -Value 'fixture'
Set-Content -LiteralPath "$old\keep.txt" -Value 'preserve'
Remove-StellarysTree $base
if ((Test-Path -LiteralPath $target) -or -not (Test-Path -LiteralPath "$old\keep.txt")) { throw 'Scoped deletion failed.' }
Remove-StellarysTree $base # missing profile is harmless
New-Item -ItemType Directory -Path $target | Out-Null
New-Item -ItemType Junction -Path "$target\linked" -Target $old | Out-Null
$rejected=$false
try { Remove-StellarysTree $base } catch { $rejected=$true }
if (-not $rejected -or -not (Test-Path -LiteralPath "$old\keep.txt")) { throw 'Junction protection failed.' }
'Profile deletion checks passed: exact profile only, old viewer preserved, missing profile safe, nested junction refused.'
