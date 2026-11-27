Get-CimInstance Win32_Process |
    Where-Object {
        $_.Name -eq "python.exe" -and $_.CommandLine -match "uvicorn main:app"
    } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

Get-CimInstance Win32_Process |
    Where-Object {
        $_.Name -eq "node.exe" -and $_.CommandLine -match "vite"
    } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

Get-CimInstance Win32_Process |
    Where-Object {
        $_.Name -eq "powershell.exe" -and (
            $_.CommandLine -match "uvicorn main:app" -or
            $_.CommandLine -match "npm run dev"
        )
    } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

Write-Host "Stopped SnapKart backend and frontend processes." -ForegroundColor Green
