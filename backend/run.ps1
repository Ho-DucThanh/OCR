$ErrorActionPreference = "Stop"

# Ensure relative paths are resolved from this script's folder.
Set-Location $PSScriptRoot

if (!(Test-Path ".venv")) {
  # SQLAlchemy 2.0.x is not yet compatible with Python 3.14.
  # Prefer Python 3.12 if available.
  try {
    py -3.12 -m venv .venv
  } catch {
    py -m venv .venv
  }
}

& "$PSScriptRoot\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r requirements.txt

# Load .env if exists (simple parser)
if (Test-Path "..\.env") {
  Get-Content "..\.env" | ForEach-Object {
    if ($_ -match "^\s*#" -or $_ -match "^\s*$") { return }
    $parts = $_.Split("=", 2)
    if ($parts.Length -eq 2) {
      [System.Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim())
    }
  }
}

uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
