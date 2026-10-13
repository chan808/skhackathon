$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$result = [ordered]@{
    checked_at = (Get-Date).ToString('o')
    purpose = 'Read-only preliminary inventory, not an official exam system test'
    memory_gib = $null
    displays = @()
    browsers = @()
    inventory_errors = @()
    camera_live_test = 'not_performed'
    microphone_live_test = 'not_performed'
    upload_speed_test = 'not_performed'
    actual_exam_conditions = 'detailed_notice_not_yet_available'
}
try {
    $memoryModules = Get-CimInstance Win32_PhysicalMemory -ErrorAction Stop
    $result.memory_gib = [Math]::Round(($memoryModules | Measure-Object -Property Capacity -Sum).Sum / 1GB, 2)
} catch { $result.inventory_errors += 'Memory inventory unavailable in this execution context.' }
try {
    $result.displays = @(Get-CimInstance Win32_VideoController -ErrorAction Stop | ForEach-Object {
        [ordered]@{ width = $_.CurrentHorizontalResolution; height = $_.CurrentVerticalResolution }
    })
} catch { $result.inventory_errors += 'Display inventory unavailable in this execution context.' }
$browserCandidates = @(
    (Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'Google\Chrome\Application\chrome.exe'),
    (Join-Path $env:LOCALAPPDATA 'Google\Chrome\Application\chrome.exe'),
    (Join-Path $env:ProgramFiles 'Microsoft\Edge\Application\msedge.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'Microsoft\Edge\Application\msedge.exe'),
    (Join-Path $env:ProgramFiles 'Naver\Naver Whale\Application\whale.exe'),
    (Join-Path $env:LOCALAPPDATA 'Naver\Naver Whale\Application\whale.exe')
)
foreach ($candidate in $browserCandidates) {
    if (Test-Path -LiteralPath $candidate) {
        $item = Get-Item -LiteralPath $candidate
        $result.browsers += [ordered]@{ executable = $item.Name; version = $item.VersionInfo.ProductVersion }
    }
}
$output = Join-Path $projectRoot 'reports\windows-preflight.json'
$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $output -Encoding UTF8
$result | ConvertTo-Json -Depth 6
