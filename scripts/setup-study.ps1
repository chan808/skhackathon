param([string]$PythonPath = '')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$studyPython = Join-Path $projectRoot '.venv-study\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $studyPython)) {
    if (-not $PythonPath) {
        $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
        $PythonPath = if (Test-Path -LiteralPath $bundledPython) { $bundledPython } else { (Get-Command python -ErrorAction Stop).Source }
    }
    & $PythonPath -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
    if ($LASTEXITCODE -ne 0) { throw 'Provide Python 3.11 or newer with -PythonPath.' }
    & $PythonPath -m venv .venv-study --without-pip
    if ($LASTEXITCODE -ne 0) { throw 'Study environment creation failed.' }
}
& $studyPython -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
if ($LASTEXITCODE -ne 0) { throw 'Existing .venv-study needs Python 3.11 or newer. Create a new environment with a supported Python.' }
& $studyPython -m practice doctor
if ($LASTEXITCODE -ne 0) { throw 'Study environment validation failed.' }
