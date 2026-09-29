param(
    [ValidateSet('Install','Uninstall','CleanupLegacy','Library')]
    [string]$Mode = 'Library',
    [string]$Destination
)
$ErrorActionPreference = 'Stop'
$script:UninstallKey = 'Software\Microsoft\Windows\CurrentVersion\Uninstall\StellarysViewer'

function Get-NormalizedInstallPath([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path) -or $Path -notmatch '^[A-Za-z]:[\\/]') {
        throw 'Choose an absolute folder on a local Windows drive.'
    }
    $full = [IO.Path]::GetFullPath($Path).TrimEnd('\','/')
    if ($full.Length -le 3) { throw 'A drive root cannot be used as the installation folder.' }
    return $full
}

function Test-SameInstallPath([string]$Left, [string]$Right) {
    if ([string]::IsNullOrWhiteSpace($Left) -or [string]::IsNullOrWhiteSpace($Right)) { return $false }
    return [string]::Equals((Get-NormalizedInstallPath $Left), (Get-NormalizedInstallPath $Right), [StringComparison]::OrdinalIgnoreCase)
}

function Test-KittyMarker([string]$Path) {
    $marker = Join-Path $Path 'stellarys-install.txt'
    if (-not [IO.File]::Exists($marker)) { return $false }
    return [string]::Equals([IO.File]::ReadAllLines($marker)[0], 'StellarysViewer', [StringComparison]::Ordinal)
}

function Assert-NoReparsePoint([string]$Path) {
    $p = $Path
    while ($p) {
        if (Test-Path -LiteralPath $p) {
            $item = Get-Item -LiteralPath $p -Force
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw 'Choose a normal folder, without junctions or symbolic links in its path.'
            }
        }
        $p = [IO.Path]::GetDirectoryName($p)
    }
}

function Assert-KittyDestination([string]$Path, [bool]$RequireMarker = $false) {
    $full = Get-NormalizedInstallPath $Path
    Assert-NoReparsePoint $full
    if (-not (Test-Path -LiteralPath $full)) {
        if ($RequireMarker) { throw 'The Stellarys installation folder is missing.' }
        return $full
    }
    if (-not (Test-Path -LiteralPath $full -PathType Container)) { throw 'The destination is a file, not a folder.' }
    $children = @(Get-ChildItem -LiteralPath $full -Force)
    if ($children.Count -eq 0 -and -not $RequireMarker) { return $full }
    if (-not (Test-KittyMarker $full)) {
        throw 'This nonempty folder has no valid Stellarys installation marker. Choose an empty folder or an existing Stellarys installation.'
    }
    foreach ($item in $children) {
        if ($item.Name -match '^(Black Dragon\.exe|BlackDragon\.exe|BlackDragonViewer\.exe|Firestorm.*\.exe|fire-kitty-fix-install\.txt)$') {
            throw 'This folder also contains an official Black Dragon or Firestorm installation. It will not be overwritten or uninstalled.'
        }
    }
    # Do not let an application subdirectory redirect extraction/deletion to
    # another viewer or profile. Enumerate without following links.
    $pending = New-Object 'System.Collections.Generic.Stack[string]'
    $pending.Push($full)
    while ($pending.Count -gt 0) {
        foreach ($item in Get-ChildItem -LiteralPath $pending.Pop() -Force) {
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw 'The installation contains a junction or symbolic link. No files will be changed.'
            }
            if ($item.PSIsContainer) { $pending.Push($item.FullName) }
        }
    }
    return $full
}

function Assert-KittyClosed([string]$Path) {
    # Get-Process covers all Windows sessions, unlike FindWindow alone.
    foreach ($process in @(Get-Process -Name StellarysViewer,StellarysUpdater -ErrorAction SilentlyContinue)) {
        $exe = $null
        try { $exe = $process.Path } catch { }
        if (-not $exe) { throw 'A viewer process cannot be inspected. Close Stellarys and its updater in all Windows sessions and retry.' }
        $folder = [IO.Path]::GetDirectoryName($exe)
        if ((Test-SameInstallPath $folder $Path) -or (Test-KittyMarker $folder)) {
            throw 'Close Stellarys and its updater in all Windows sessions before installing, updating or uninstalling it.'
        }
        # Also cover an unmarked copy of the renamed release binary.
        if ((Get-Item -LiteralPath $exe).VersionInfo.FileDescription -like '*Stellarys*') {
            throw 'Close Stellarys and its updater in all Windows sessions before continuing.'
        }
    }
}

function Assert-MachineRegistration([string]$Path) {
    $key = 'Registry::HKEY_LOCAL_MACHINE\' + $script:UninstallKey
    if (Test-Path -LiteralPath $key) {
        $existing = (Get-ItemProperty -LiteralPath $key).InstallLocation
        if ($existing -and -not (Test-SameInstallPath $existing $Path)) {
            throw 'A machine-wide Stellarys installation is registered in another folder. Update that folder, or uninstall it yourself before choosing a new folder. No installation will be moved or removed automatically.'
        }
    }
}

function Remove-MatchingLegacyRegistration([string]$Path) {
    # Enumerate loaded user hives, including the original user when UAC used
    # another administrator's credentials. Never load/unload another profile.
    foreach ($hive in Get-ChildItem 'Registry::HKEY_USERS') {
        if ($hive.PSChildName -notmatch '^S-1-5-21-(\d+-){3}\d+$') { continue }
        foreach ($suffix in @($script:UninstallKey, ('Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\StellarysViewer'))) {
            $key = Join-Path $hive.PSPath $suffix
            if (Test-Path -LiteralPath $key) {
                $existing = (Get-ItemProperty -LiteralPath $key).InstallLocation
                if ($existing -and (Test-SameInstallPath $existing $Path)) {
                    # Only this product's registration, only this exact folder.
                    Remove-Item -LiteralPath $key -Recurse
                }
            }
        }
    }
}

if ($Mode -ne 'Library') {
    try {
        $full = Assert-KittyDestination $Destination ($Mode -ne 'Install')
        Assert-KittyClosed $full
        if ($Mode -eq 'Install') { Assert-MachineRegistration $full }
        if ($Mode -eq 'CleanupLegacy') { Remove-MatchingLegacyRegistration $full }
        Write-Output 'OK'
        exit 0
    } catch {
        Write-Output $_.Exception.Message
        exit 3
    }
}
