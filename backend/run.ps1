$ErrorActionPreference = "Stop"

# Ensure relative paths are resolved from this script's folder.
Set-Location $PSScriptRoot

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (!(Test-Path $venvPython)) {
  Set-Location $repoRoot
  try {
    py -3.12 -m venv .venv
  } catch {
    py -m venv .venv
  }
}

Set-Location $repoRoot
& $venvPython -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")

# Load .env if exists (simple parser)
$envPath = Join-Path $repoRoot ".env"
if (Test-Path $envPath) {
  Get-Content $envPath | ForEach-Object {
    if ($_ -match "^\s*#" -or $_ -match "^\s*$") { return }
    $parts = $_.Split("=", 2)
    if ($parts.Length -eq 2) {
      [System.Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim())
    }
  }
}

# Free port 8001 if something is already listening (common after a previous run)
$conns = Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue
if ($conns) {
  $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
  foreach ($procId in $pids) {
    Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
  }
}

& $venvPython -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
