$ErrorActionPreference = 'Stop'
$projectPath = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$buildPath = $projectPath

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Install Docker Desktop and start its Linux engine first.'
}

# Docker Bake on Windows rejects some Unicode context paths. A junction preserves all files.
if ($projectPath -match '[^\x00-\x7F]') {
    $digest = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hash = [BitConverter]::ToString($digest.ComputeHash([Text.Encoding]::UTF8.GetBytes($projectPath))).Replace('-', '').Substring(0, 12)
    } finally {
        $digest.Dispose()
    }
    $buildPath = Join-Path ([IO.Path]::GetPathRoot($projectPath)) "academy-workspaces\academy-$hash"
    if ($buildPath -match '[^\x00-\x7F]') {
        throw 'An ASCII checkout path is required by this Docker Bake installation.'
    }
    if (Test-Path -LiteralPath $buildPath) {
        $existing = Get-Item -LiteralPath $buildPath
        if ($existing.LinkType -ne 'Junction' -or $existing.Target -ne $projectPath) {
            throw "Refusing to use an unrelated existing path: $buildPath"
        }
    } else {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $buildPath) | Out-Null
        New-Item -ItemType Junction -Path $buildPath -Target $projectPath | Out-Null
    }
}

Push-Location -LiteralPath $buildPath
try {
    docker compose up --build -d --wait
    if ($LASTEXITCODE -ne 0) { throw 'Docker Compose failed. Review its output above.' }
    $port = if ($env:ACADEMY_PORT) { $env:ACADEMY_PORT } else { '8080' }
    Write-Host "Academy is running. Default address: http://localhost:$port (a .env file may override the port)."
    Write-Host 'Progress persists in the Docker database volume.'
} finally {
    Pop-Location
}
