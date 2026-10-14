$ErrorActionPreference = 'Stop'
$installerProjectRoot = Split-Path -Parent $PSScriptRoot
$installerDirectory = Join-Path $installerProjectRoot 'output\laptop-kit\installers'
$installerSpecifications = @(
    @{ name = 'python-3.13.16-amd64.exe'; source = 'https://www.python.org/ftp/python/3.13.16/python-3.13.16-amd64.exe'; publisher = 'Python Software Foundation'; expected_sha256 = 'fb4f9f5d438b2396da0086dc70b935c530cb578e37adc6d354f7ad2037fee83b' },
    @{ name = 'googlechromestandaloneenterprise64.msi'; source = 'https://dl.google.com/dl/chrome/install/googlechromestandaloneenterprise64.msi'; publisher = 'Google LLC'; expected_sha256 = $null }
)
$installerChecks = @()
foreach ($specification in $installerSpecifications) {
    $installerPath = Join-Path $installerDirectory $specification.name
    if (-not (Test-Path -LiteralPath $installerPath -PathType Leaf)) { throw ('Missing cached installer: ' + $specification.name) }
    $installerSignature = Get-AuthenticodeSignature -LiteralPath $installerPath
    $installerHash = (Get-FileHash -LiteralPath $installerPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $installerSigned = [string]$installerSignature.Status -eq 'Valid' -and $installerSignature.SignerCertificate.Subject.Contains($specification.publisher)
    $installerMatches = $null
    if ($specification.expected_sha256) { $installerMatches = $installerHash -eq $specification.expected_sha256 }
    if (-not $installerSigned -or $installerMatches -eq $false) { throw ('Installer signature or publisher checksum failed: ' + $specification.name) }
    $installerChecks += [ordered]@{
        file = $specification.name
        os = 'Windows'
        architecture = 'x64'
        bytes = (Get-Item -LiteralPath $installerPath).Length
        sha256 = $installerHash
        source = $specification.source
        signature_status = [string]$installerSignature.Status
        signer = $installerSignature.SignerCertificate.Subject
        publisher_sha256_matched = $installerMatches
        installed_by_this_task = $false
    }
}
$installerReceipt = [ordered]@{
    checked_at = (Get-Date).ToString('o')
    scope = 'Cached full installers, not installation or login verification'
    passed = $true
    files = $installerChecks
    vpn_installer = 'not_cached; optional download authorization was declined'
    study_pip_packages_required = 0
}
$installerReceipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $installerDirectory 'manifest.json') -Encoding utf8
$installerReceipt | ConvertTo-Json -Depth 5
