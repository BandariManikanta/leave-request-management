# Starts the backend and frontend in separate windows, then opens the app in Edge.
# Run from the project root:
#   powershell -ExecutionPolicy Bypass -File .\start.ps1

$backendDir = Join-Path $PSScriptRoot "backend"
$frontendDir = Join-Path $PSScriptRoot "frontend"
$appUrl = "http://localhost:5173"

Start-Process powershell -WorkingDirectory $backendDir -ArgumentList '-NoExit -Command "python -m uvicorn app.main:app --reload"'
Start-Process powershell -WorkingDirectory $frontendDir -ArgumentList '-NoExit -Command "npm.cmd run dev"'

# Wait until the frontend answers before opening the browser (up to 60 seconds).
for ($attempt = 0; $attempt -lt 60; $attempt++) {
    try {
        Invoke-WebRequest -Uri $appUrl -UseBasicParsing -TimeoutSec 2 | Out-Null
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}

Start-Process msedge $appUrl
