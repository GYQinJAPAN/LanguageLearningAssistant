$port = 8000

Write-Host "Checking port $port..."

$connections = netstat -ano | findstr ":$port"

if ($connections) {
    Write-Host "Port $port is already in use:"
    Write-Host $connections
    Write-Host ""
    Write-Host "Please stop the existing process or run kill_port_8001.ps1 first."
    exit 1
}

Write-Host "Starting FastAPI on 127.0.0.1:$port ..."
uvicorn app.main:app --reload --host 127.0.0.1 --port $port