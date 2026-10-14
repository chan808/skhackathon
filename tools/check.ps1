param([switch]$VerifyInstallers)
$ErrorActionPreference = 'Stop'
$examRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$privateDirectory = Join-Path $examRoot 'private'
New-Item -ItemType Directory -Path $privateDirectory -Force | Out-Null
$result = [ordered]@{
    checked_at = (Get-Date).ToString('o')
    scope = 'Local inventory, not an official exam system test'
    os = [Environment]::OSVersion.VersionString
    powershell = $PSVersionTable.PSVersion.ToString()
    memory_gib = $null
    browsers = @()
    monito = $null
    inventory_errors = @()
    installer_checks = @()
    manual_checks = [ordered]@{
        official_invitation_and_precheck = 'unverified'
        japan_connection_and_proctoring = 'unverified'
        overseas_and_vpn_policy = 'unverified'
        permitted_tools_and_recovery = 'unverified'
        camera_microphone_and_submission = 'unverified'
    }
}
try {
    $memoryBytes = (Get-CimInstance Win32_PhysicalMemory -ErrorAction Stop | Measure-Object -Property Capacity -Sum).Sum
    $result.memory_gib = [Math]::Round($memoryBytes / 1GB, 2)
} catch { $result.inventory_errors += 'Memory inventory unavailable; check hardware using the official precheck.' }
$candidates = @(
    (Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'Google\Chrome\Application\chrome.exe'),
    (Join-Path $env:LOCALAPPDATA 'Google\Chrome\Application\chrome.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'Microsoft\Edge\Application\msedge.exe')
)
foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate -PathType Leaf) {
        $item = Get-Item -LiteralPath $candidate
        $result.browsers += [ordered]@{ executable = $item.Name; version = $item.VersionInfo.ProductVersion }
    }
}
$monitoPath = Join-Path $env:LOCALAPPDATA 'Programs\monito-pc\MonitoPlus.exe'
if (Test-Path -LiteralPath $monitoPath -PathType Leaf) {
    $item = Get-Item -LiteralPath $monitoPath
    $result.monito = [ordered]@{ executable = $item.Name; version = $item.VersionInfo.ProductVersion }
}
if ($VerifyInstallers) {
    $specifications = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'installers.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($specification in $specifications.files) {
        $installerPath = Join-Path $examRoot ('offline\installers\' + $specification.name)
        if (-not (Test-Path -LiteralPath $installerPath -PathType Leaf)) { throw ('Missing recovery installer: ' + $specification.name) }
        $item = Get-Item -LiteralPath $installerPath
        $hash = (Get-FileHash -LiteralPath $installerPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($item.Length -ne $specification.bytes -or $hash -ne $specification.sha256) { throw ('Installer integrity mismatch: ' + $specification.name) }
        $signature = Get-AuthenticodeSignature -LiteralPath $installerPath
        $signer = $null
        if ($signature.SignerCertificate) { $signer = $signature.SignerCertificate.Subject }
        if ([string]$signature.Status -ne 'Valid' -or -not $signer -or -not $signer.Contains($specification.publisher)) { throw ('Publisher signature could not be verified: ' + $specification.name) }
        $result.installer_checks += [ordered]@{ file = $specification.name; bytes = $item.Length; sha256 = $hash; signature = [string]$signature.Status; publisher_matched = $true }
    }
}
$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $privateDirectory 'system-check.json') -Encoding UTF8
$result | ConvertTo-Json -Depth 6
Write-Output 'Local inventory completed. Manual checks in README.md determine exam readiness.'
