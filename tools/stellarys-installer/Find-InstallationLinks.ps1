# Read-only: inspects directory entries, never follows reparse points or changes files.
param([string]$Installation = 'C:\Program Files\StellarysViewer')
$ErrorActionPreference = 'Stop'
$full = [IO.Path]::GetFullPath($Installation)
Write-Output ('Inspecting: ' + $full)
$parents = $full
while ($parents) {
    $item = Get-Item -LiteralPath $parents -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Write-Output ('FLAGGED PATH: ' + $item.FullName + ' | ' + $item.Attributes)
        Write-Output 'Stopped: a path component is a reparse point. Nothing changed.'
        return
    }
    $parents = [IO.Path]::GetDirectoryName($parents)
}
$pending = New-Object 'System.Collections.Generic.Stack[string]'
$pending.Push($full)
$count = 0
while ($pending.Count -gt 0) {
    foreach ($item in Get-ChildItem -LiteralPath $pending.Pop() -Force) {
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            Write-Output ('FLAGGED ITEM: ' + $item.FullName + ' | ' + $item.Attributes)
            $count++
        } elseif ($item.PSIsContainer) { $pending.Push($item.FullName) }
    }
}
Write-Output ('Flagged items: ' + $count + '. No links followed and no files changed.')
