$ErrorActionPreference = 'Stop'
$examRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$offlineDirectory = [IO.Path]::GetFullPath((Join-Path $examRoot 'offline'))
$privateDirectory = [IO.Path]::GetFullPath((Join-Path $examRoot 'private'))
foreach ($path in @($offlineDirectory,$privateDirectory)) {
    if (-not $path.StartsWith($examRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Output path outside project.' }
    New-Item -ItemType Directory -Path $path -Force | Out-Null
}
$stageDirectory = Join-Path $privateDirectory ('package-stage-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $stageDirectory | Out-Null
$includedFiles = @('README.md','.gitignore','.gitattributes','etc\README.md','etc\analysis\preview-analysis.md','etc\analysis\study-guide.md','etc\analysis\study-guide-check.json','output\pdf\AI-prelim-complete-textbook.pdf')
$includedFiles += @(Get-ChildItem -LiteralPath $PSScriptRoot -File | ForEach-Object { 'tools\' + $_.Name })
foreach ($relativeFile in $includedFiles) {
    $sourcePath = [IO.Path]::GetFullPath((Join-Path $examRoot $relativeFile))
    $destinationPath = [IO.Path]::GetFullPath((Join-Path $stageDirectory $relativeFile))
    if (-not $sourcePath.StartsWith($examRoot + '\', [StringComparison]::OrdinalIgnoreCase) -or -not $destinationPath.StartsWith($stageDirectory + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'File outside package scope.' }
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) { throw ('Missing package file: ' + $relativeFile) }
    New-Item -ItemType Directory -Path (Split-Path -Parent $destinationPath) -Force | Out-Null
    Copy-Item -LiteralPath $sourcePath -Destination $destinationPath
}
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zipPath = Join-Path $offlineDirectory 'contest-kit.zip'
$temporaryZip = Join-Path $offlineDirectory ('contest-kit-' + [Guid]::NewGuid().ToString('N') + '.zip')
[IO.Compression.ZipFile]::CreateFromDirectory($stageDirectory, $temporaryZip)
Move-Item -LiteralPath $temporaryZip -Destination $zipPath -Force
$hash = (Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash.ToLowerInvariant()
($hash + '  contest-kit.zip') | Set-Content -LiteralPath ($zipPath + '.sha256') -Encoding ASCII
[ordered]@{ created_at = (Get-Date).ToString('o'); package = 'offline/contest-kit.zip'; sha256 = $hash; excluded = @('private/','offline/installers/','etc/legacy-project/','.git/'); files = $includedFiles } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $privateDirectory 'package-receipt.json') -Encoding UTF8
Write-Output ('Portable kit created: ' + $zipPath)
Write-Output ('SHA256: ' + $hash)
