param([string]$PythonPath = '')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$studyPython = Join-Path $projectRoot '.venv-study\Scripts\python.exe'
$studyEnvironment = Join-Path $projectRoot '.venv-study'
$recovery = 'Existing .venv-study was kept. Rename it to a backup name and retry with installed Python 3.11+. Do not copy virtual environments between PCs.'
if ((Test-Path -LiteralPath $studyEnvironment) -and -not (Test-Path -LiteralPath $studyPython)) {
    throw $recovery
}
if (-not (Test-Path -LiteralPath $studyPython)) {
    if (-not $PythonPath) {
        $pythonCandidates = @()
        $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
        if (Test-Path -LiteralPath $bundledPython) { $pythonCandidates += $bundledPython }
        # py is often available on a new Windows laptop even when python is not on PATH.
        $pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
        if ($pythonLauncher) {
            try {
                $launcherOutput = & $pythonLauncher.Source -3 -c "import sys; print(sys.executable)" 2>$null
                if ($LASTEXITCODE -eq 0 -and $launcherOutput) {
                    $pythonCandidates += ([string]($launcherOutput | Select-Object -Last 1)).Trim()
                }
            } catch { }
        }
        foreach ($commandName in @('python', 'python3')) {
            $installedCommand = Get-Command $commandName -ErrorAction SilentlyContinue
            if ($installedCommand -and $installedCommand.Source -notlike '*\Microsoft\WindowsApps\*') {
                $pythonCandidates += $installedCommand.Source
            }
        }
        foreach ($candidate in ($pythonCandidates | Select-Object -Unique)) {
            try {
                & $candidate -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>$null
                if ($LASTEXITCODE -eq 0) { $PythonPath = $candidate; break }
            } catch { }
        }
        if (-not $PythonPath) {
            throw 'Install Python 3.11+ from python.org, or provide its executable with -PythonPath. This script does not download Python.'
        }
    }
    & $PythonPath -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
    if ($LASTEXITCODE -ne 0) { throw 'Provide Python 3.11 or newer with -PythonPath.' }
    & $PythonPath -m venv .venv-study --without-pip
    if ($LASTEXITCODE -ne 0) { throw 'Study environment creation failed.' }
}
try {
    & $studyPython -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
} catch { throw $recovery }
if ($LASTEXITCODE -ne 0) { throw $recovery }
& $studyPython -m practice doctor
if ($LASTEXITCODE -ne 0) { throw 'Study environment validation failed.' }
