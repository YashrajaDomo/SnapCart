$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = "python"

$services = @(
    @{ Name = "Catalog"; Port = 8001; Path = "backend\catalog_service" },
    @{ Name = "Cart"; Port = 8002; Path = "backend\cart_service" },
    @{ Name = "Order"; Port = 8003; Path = "backend\order_service" },
    @{ Name = "Payment"; Port = 8004; Path = "backend\payment_service" },
    @{ Name = "Notification"; Port = 8005; Path = "backend\notification_service" },
    @{ Name = "AI"; Port = 8006; Path = "backend\ai_service" },
    @{ Name = "API Gateway"; Port = 8000; Path = "backend\api_gateway" }
)

Write-Host "Starting SnapKart backend services..." -ForegroundColor Green
foreach ($service in $services) {
    $workingDirectory = Join-Path $root $service.Path
    $command = "Set-Location -LiteralPath '$workingDirectory'; python -m uvicorn main:app --host 127.0.0.1 --port $($service.Port)"
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit","-Command",$command -WindowStyle Normal
}

Write-Host "Starting SnapKart frontend..." -ForegroundColor Green
$frontendDirectory = Join-Path $root "frontend"
$frontendCommand = "Set-Location -LiteralPath '$frontendDirectory'; npm run dev -- --host 127.0.0.1"
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit","-Command",$frontendCommand -WindowStyle Normal

Write-Host "`nSnapKart is starting."
Write-Host "Frontend:  http://127.0.0.1:5173"
Write-Host "Gateway:   http://127.0.0.1:8000/docs"
