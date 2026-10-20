$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    & python "$PSScriptRoot/pipeline.py" --root "$PSScriptRoot/data"
    if ($LASTEXITCODE -ne 0) { throw 'NIFTY refresh failed or was partial. See data/last-run.json.' }
} finally { Pop-Location }
