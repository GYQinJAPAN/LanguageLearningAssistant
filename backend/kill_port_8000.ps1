# $port = 8000
#
# Write-Host "Searching processes using port $port..."
#
# $lines = netstat -ano | findstr ":$port"
#
# if (-not $lines) {
#     Write-Host "No process found using port $port."
#     exit 0
# }
#
# $killed = @()
#
# $lines | ForEach-Object {
#     $line = $_.Trim()
#     $parts = $line -split '\s+'
#     $pid = $parts[-1]
#
#     if ($pid -match '^\d+$' -and -not ($killed -contains $pid)) {
#         Write-Host "Killing PID $pid ..."
#         taskkill /PID $pid /F
#         $killed += $pid
#     }
# }
#
# Write-Host "Done."
$port = 8000

Write-Host "Checking TCP listeners on port $port..."

$connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue

if (-not $connections)
{
    Write-Host "No process found using port $port."
    exit 0
}

$killed = @()

$connections | ForEach-Object {
    $pid = $_.OwningProcess

    if ($pid -and -not ($killed -contains $pid))
    {
        try
        {
            $proc = Get-Process -Id $pid -ErrorAction Stop
            Write-Host "Killing PID $pid ($( $proc.ProcessName )) ..."
            Stop-Process -Id $pid -Force
            $killed += $pid
        }
        catch
        {
            Write-Host "Could not stop PID $pid. It may already be gone or require admin privileges."
        }
    }
}

Write-Host "Done."

#启动前先查端口,比如手动查："netstat -ano | findstr :8000"
#会看到类似："TCP    127.0.0.1:8000    ...    LISTENING    12345"
#记下最后那个 PID，然后执行："taskkill /PID 12345 /F"
#如果有输出，说明端口被占用了。有多个 PID，都杀掉。
#
