param([string]$PythonPath = '')
$ErrorActionPreference = 'Stop'
# Keep the original entry point aligned with the current .venv-study setup.
& (Join-Path $PSScriptRoot 'setup-study.ps1') -PythonPath $PythonPath
