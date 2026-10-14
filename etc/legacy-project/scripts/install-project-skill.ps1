$ErrorActionPreference = 'Stop'
$skillProjectRoot = Split-Path -Parent $PSScriptRoot
$skillSource = Join-Path $skillProjectRoot 'templates\project-skills\hackathon-preflight\SKILL.md'
$skillDestination = Join-Path $skillProjectRoot '.agents\skills\hackathon-preflight\SKILL.md'
if (-not (Test-Path -LiteralPath $skillSource -PathType Leaf)) { throw 'Skill source is missing.' }
if (Test-Path -LiteralPath $skillDestination) {
    if ((Get-Content -LiteralPath $skillDestination -Raw) -eq (Get-Content -LiteralPath $skillSource -Raw)) {
        Write-Output 'Project skill is already installed.'
        return
    }
    throw 'An existing different skill was kept. Review the source and installed skill before replacing it.'
}
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $skillDestination) | Out-Null
Copy-Item -LiteralPath $skillSource -Destination $skillDestination
Write-Output 'Installed .agents/skills/hackathon-preflight/SKILL.md. Reopen this project if the skill selector is stale.'
