$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"
$venvActivate = Join-Path $root ".venv\Scripts\Activate.ps1"

$backendCommand = @"
if (Test-Path '$venvActivate') { . '$venvActivate' }
Set-Location '$backendDir'
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
"@

$frontendCommand = @"
Set-Location '$frontendDir'
npm run dev
"@

Write-Host "Starting backend at http://127.0.0.1:8000 ..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand

Write-Host "Starting frontend dev server ..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand

Write-Host "Health check: http://127.0.0.1:8000/health"

#"-NoExit"：命令跑完后窗口别关（方便看日志）。
#
#"-Command", $backendCommand：在窗口中执行 $backendCommand 里的具体代码。