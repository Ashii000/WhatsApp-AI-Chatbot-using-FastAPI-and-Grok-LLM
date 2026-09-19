# PowerShell Watchdog Script to ensure 24/7 Uptime
$Host.UI.RawUI.WindowTitle = "WhatsApp AI Bot - 24/7 Supervisor"
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$batchFile = Join-Path $scriptPath "start_server.bat"

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   SYSTEM SUPERVISOR ACTIVE - WATCHING FOR CRASHES     " -ForegroundColor Yellow
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "Monitoring target: $batchFile"

while ($true) {
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Starting Bot Engine..." -ForegroundColor Green
    
    # Start the batch file and wait for it to exit or crash
    $process = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$batchFile`"" -Wait -NoNewWindow -PassThru
    
    # If the script reaches this line, it means the bot server crashed
    $exitCode = $process.ExitCode
    Write-Host "-------------------------------------------------------" -ForsegroundColor Red
    Write-Host "⚠️ WARNING: Bot Engine crashed or stopped (Exit Code: $exitCode)!" -ForegroundColor Red
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Supervisor is automatically restarting the bot in 3 seconds..." -ForegroundColor Yellow
    Write-Host "-------------------------------------------------------" -ForegroundColor Red
    
    Start-Sleep -Seconds 3
}