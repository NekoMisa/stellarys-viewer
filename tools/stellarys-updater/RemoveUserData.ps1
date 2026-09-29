param([switch]$Settings, [switch]$Cache, [switch]$Library)
$ErrorActionPreference = 'Stop'
# The uninstaller explicitly names this Windows account on its opt-in page.
# Never infer another user's profile, follow reparse points, or read a custom
# CacheLocation from settings. Old Fire Kitty/official viewer profiles are excluded.
function Remove-StellarysTree([string]$Base) {
    $baseFull = [IO.Path]::GetFullPath($Base).TrimEnd('\')
    $target = [IO.Path]::GetFullPath((Join-Path $baseFull 'Stellarys_x64'))
    if ([IO.Path]::GetDirectoryName($target) -ne $baseFull -or [IO.Path]::GetFileName($target) -ne 'Stellarys_x64') { throw 'Invalid profile target.' }
    if (-not (Test-Path -LiteralPath $target)) { return }
    $parent = $target
    while ($parent) {
        if ((Get-Item -LiteralPath $parent -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Profile path contains a junction or symbolic link. Remove it manually.' }
        $parent = [IO.Path]::GetDirectoryName($parent)
    }
    $pending = New-Object 'System.Collections.Generic.Stack[string]'
    $pending.Push($target)
    while ($pending.Count -gt 0) {
        foreach ($item in Get-ChildItem -LiteralPath $pending.Pop() -Force) {
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Profile contains a junction or symbolic link. Remove it manually.' }
            if ($item.PSIsContainer) { $pending.Push($item.FullName) }
        }
    }
    Remove-Item -LiteralPath $target -Recurse -Force
}
if ($Library) { return }
try {
    if (@(Get-Process -Name StellarysViewer -ErrorAction SilentlyContinue).Count) { throw 'Close all Stellarys windows before removing data.' }
    if ($Settings) { Remove-StellarysTree ([Environment]::GetFolderPath('ApplicationData')) }
    if ($Cache) { Remove-StellarysTree ([Environment]::GetFolderPath('LocalApplicationData')) }
    exit 0
} catch { Write-Output $_.Exception.Message; exit 3 }
