param([switch]$VerifyPackage)
$ErrorActionPreference = 'Stop'
$examRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$failures = @()
$checks = @()
$rootMarkdown = @(Get-ChildItem -LiteralPath $examRoot -File -Filter '*.md')
if ($rootMarkdown.Count -ne 1 -or $rootMarkdown[0].Name -ne 'README.md') { $failures += 'README.md must be the only Markdown file at project root.' }
$checks += 'Single root handbook'
$requiredFiles = @('README.md','etc\README.md','etc\analysis\preview-analysis.md','tools\check.ps1','tools\verify.ps1','tools\package.ps1','tools\installers.json','.gitignore','.gitattributes')
foreach ($relativeFile in $requiredFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $examRoot $relativeFile) -PathType Leaf)) { $failures += ('Missing required file: ' + $relativeFile) }
}
$checks += 'Required files'
foreach ($scriptFile in (Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.ps1' -File)) {
    $parseTokens = $null
    $parseErrors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($scriptFile.FullName, [ref]$parseTokens, [ref]$parseErrors) | Out-Null
    foreach ($parseError in $parseErrors) { $failures += ($scriptFile.Name + ': ' + $parseError.Message) }
}
$checks += 'PowerShell syntax'
$activeDocuments = @((Join-Path $examRoot 'README.md'),(Join-Path $examRoot 'etc\README.md'),(Join-Path $examRoot 'etc\analysis\preview-analysis.md'))
foreach ($documentPath in $activeDocuments) {
    if (-not (Test-Path -LiteralPath $documentPath)) { continue }
    $markdown = Get-Content -LiteralPath $documentPath -Raw -Encoding UTF8
    foreach ($match in [regex]::Matches($markdown, '\]\(([^)]+)\)')) {
        $target = $match.Groups[1].Value.Trim('<','>')
        if ($target -match '^(https?://|mailto:|#)') { continue }
        $target = [Uri]::UnescapeDataString(($target -split '#',2)[0])
        $resolvedTarget = [IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $documentPath) $target))
        if (-not $resolvedTarget.StartsWith($examRoot + '\', [StringComparison]::OrdinalIgnoreCase) -or -not (Test-Path -LiteralPath $resolvedTarget)) { $failures += ('Broken local link: ' + $target) }
    }
}
$checks += 'Active document links'
$ignoreRules = Get-Content -LiteralPath (Join-Path $examRoot '.gitignore') -Raw -Encoding UTF8
foreach ($rule in @('/private/','/offline/','/etc/legacy-project/.venv-study/','/etc/legacy-project/tmp/')) {
    if (-not $ignoreRules.Contains($rule)) { $failures += ('Missing Git exclusion: ' + $rule) }
}
$checks += 'Private and binary exclusions'
$manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'installers.json') -Raw -Encoding UTF8 | ConvertFrom-Json
foreach ($entry in $manifest.files) {
    if ($entry.sha256 -notmatch '^[0-9a-f]{64}$' -or $entry.bytes -le 0 -or $entry.source -notmatch '^https://(dl\.google\.com|www\.python\.org)/') { $failures += ('Invalid installer specification: ' + $entry.name) }
}
$checks += 'Installer specifications'
if ($VerifyPackage) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zipPath = Join-Path $examRoot 'offline\contest-kit.zip'
    if (-not (Test-Path -LiteralPath $zipPath -PathType Leaf)) { $failures += 'Portable ZIP is missing.' }
    else {
        $expectedHash = ((Get-Content -LiteralPath ($zipPath + '.sha256') -Raw).Trim() -split '\s+')[0]
        if ((Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) { $failures += 'Portable ZIP checksum mismatch.' }
        $archive = [IO.Compression.ZipFile]::OpenRead($zipPath)
        try {
            $names = @($archive.Entries | ForEach-Object { $_.FullName.Replace('\','/') })
            foreach ($name in $names) {
                if ($name -match '(^/|(^|/)\.\.(/|$)|^(private|offline|\.git)/|^etc/legacy-project/|^[A-Za-z]:)') { $failures += ('Disallowed ZIP path: ' + $name) }
            }
            foreach ($relativeFile in $requiredFiles) {
                if ($names -notcontains $relativeFile.Replace('\','/')) { $failures += ('Missing ZIP file: ' + $relativeFile) }
            }
            foreach ($entry in $archive.Entries) {
                if (-not $entry.Name) { continue }
                $sourcePath = Join-Path $examRoot $entry.FullName
                if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) { $failures += ('Unknown ZIP file: ' + $entry.FullName); continue }
                $stream = $entry.Open()
                $algorithm = [Security.Cryptography.SHA256]::Create()
                try { $entryHash = [BitConverter]::ToString($algorithm.ComputeHash($stream)).Replace('-','').ToLowerInvariant() }
                finally { $algorithm.Dispose(); $stream.Dispose() }
                if ($entryHash -ne (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash.ToLowerInvariant()) { $failures += ('ZIP file differs from current source: ' + $entry.FullName) }
            }
        } finally { $archive.Dispose() }
    }
    $checks += 'Portable ZIP scope, contents and source checksums'
}
$privateDirectory = Join-Path $examRoot 'private'
New-Item -ItemType Directory -Path $privateDirectory -Force | Out-Null
$result = [ordered]@{ checked_at = (Get-Date).ToString('o'); passed = $failures.Count -eq 0; checks = $checks; failures = $failures }
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $privateDirectory 'project-verification.json') -Encoding UTF8
$result | ConvertTo-Json -Depth 5
if ($failures.Count -gt 0) { exit 1 }
