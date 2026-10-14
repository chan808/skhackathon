param(
    [ValidateSet('check', 'learn', 'timed', 'case')]
    [string]$Mode = 'check',
    [ValidateSet('RC01', 'RC02', 'RC03')]
    [string]$CaseId = 'RC02',
    [string]$PythonPath = ''
)
$ErrorActionPreference = 'Stop'
$studyRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $studyRoot
& (Join-Path $PSScriptRoot 'setup-study.ps1') -PythonPath $PythonPath
$studyPython = Join-Path $studyRoot '.venv-study\Scripts\python.exe'
switch ($Mode) {
    'check' { & $studyPython (Join-Path $PSScriptRoot 'verify.py') }
    'learn' { & $studyPython -m practice quiz --bank backend --count 20 }
    'timed' { & $studyPython -m practice quiz --bank backend --count 20 --exam --minutes 30 --seed 18 }
    'case' { & $studyPython -m practice.readiness start --case $CaseId }
}
if ($LASTEXITCODE -ne 0) { throw "Study command failed with exit code $LASTEXITCODE." }
