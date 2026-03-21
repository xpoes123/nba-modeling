# install_task.ps1
# Register the nightly ratings job in Windows Task Scheduler.
#
# Usage (run once, in an elevated PowerShell):
#   powershell -ExecutionPolicy Bypass -File scripts\install_task.ps1
#
# The task runs daily at 4:00 AM. If the machine is off at that time,
# -StartWhenAvailable causes it to run as soon as the machine is available.
# On failure it retries once after 30 minutes.

$ProjectRoot = "C:\Users\David\CS\hobbies\sports\nba_clv_modeling"
$BatFile     = "$ProjectRoot\scripts\run_nightly.bat"
$TaskName    = "NBA_Nightly_Ratings"

$action = New-ScheduledTaskAction `
    -Execute  $BatFile `
    -WorkingDirectory $ProjectRoot

$trigger = New-ScheduledTaskTrigger -Daily -At "04:00AM"

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit  (New-TimeSpan -Hours 2) `
    -RestartCount        1 `
    -RestartInterval     (New-TimeSpan -Minutes 30) `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action   $action `
    -Trigger  $trigger `
    -Settings $settings `
    -RunLevel Highest `
    -Force

Write-Host ""
Write-Host "Task '$TaskName' registered. Next steps:"
Write-Host "  - Trigger manually: schtasks /run /tn $TaskName"
Write-Host "  - Check status:     schtasks /query /tn $TaskName /fo LIST"
Write-Host "  - View logs:        Get-Content $ProjectRoot\logs\nightly_*.log | Select -Last 50"
Write-Host "  - Uninstall:        Unregister-ScheduledTask -TaskName $TaskName -Confirm:`$false"
