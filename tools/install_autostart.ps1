<#
.SYNOPSIS
    Auto-start the bot at logon WITH admin rights, via Task Scheduler.

.DESCRIPTION
    Items in the Startup folder can never run elevated, so admin-only shortcuts
    launched by the bot would hang on a UAC prompt nobody can click. This script
    registers a scheduled task that starts the bot elevated at logon, with no
    prompt, in the interactive session (so screenshots/keyboard/mouse still work).

    It also:
      * moves the old Startup-folder launcher into <project>\legacy\ (archived, not deleted)
      * stops the currently running (non-elevated) bot and starts the task

    Run it once. It re-launches itself elevated if needed (one UAC prompt).

.PARAMETER Uninstall
    Remove the scheduled task (and stop the bot it started). The archived
    Startup launcher is left in legacy\ - copy it back by hand if wanted.
#>
param([switch]$Uninstall)

$ErrorActionPreference = 'Stop'
$TaskName   = 'Telegram-Windows-Command-Bot'
$ProjectDir = Split-Path -Parent $PSScriptRoot
$Pythonw    = Join-Path $ProjectDir 'venv\Scripts\pythonw.exe'
$StartupBat = Join-Path ([Environment]::GetFolderPath('Startup')) 'activate bot.bat'
$LegacyDir  = Join-Path $ProjectDir 'legacy'

# --- self-elevate -----------------------------------------------------------
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
           ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    $argList = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-NoExit', '-File', "`"$PSCommandPath`"")
    if ($Uninstall) { $argList += '-Uninstall' }
    Start-Process powershell.exe -Verb RunAs -ArgumentList $argList
    return
}

function Stop-Bot {
    # The venv's pythonw.exe is a launcher that spawns the real interpreter as a
    # child, so stop the launcher and its children.
    $all = Get-CimInstance Win32_Process
    $launchers = $all | Where-Object {
        $_.Name -eq 'pythonw.exe' -and $_.ExecutablePath -eq $Pythonw -and $_.CommandLine -match 'main\.py'
    }
    foreach ($p in $launchers) {
        $all | Where-Object { $_.ParentProcessId -eq $p.ProcessId } |
            ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        Write-Host "Stopped running bot (PID $($p.ProcessId))"
    }
}

if ($Uninstall) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Removed task '$TaskName'."
    } else {
        Write-Host "Task '$TaskName' not found."
    }
    Stop-Bot
    return
}

if (-not (Test-Path $Pythonw)) { throw "Not found: $Pythonw (create the venv first)" }

# --- register the task ------------------------------------------------------
$user    = "$env:USERDOMAIN\$env:USERNAME"
$action  = New-ScheduledTaskAction -Execute $Pythonw -Argument 'main.py' -WorkingDirectory $ProjectDir
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $user
$trigger.Delay = 'PT10S'   # let the network come up
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Highest
$settings  = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -MultipleInstances IgnoreNew `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Principal $principal -Settings $settings -Force `
    -Description 'Telegram Windows Command Bot - elevated, at logon.' | Out-Null
Write-Host "Registered task '$TaskName' (runs elevated at logon)."

# --- archive the old Startup launcher (so the bot doesn't start twice) -------
if (Test-Path $StartupBat) {
    New-Item -ItemType Directory -Force -Path $LegacyDir | Out-Null
    Move-Item -LiteralPath $StartupBat -Destination $LegacyDir -Force
    Write-Host "Archived '$StartupBat' -> $LegacyDir"
}

# --- swap the running bot for the elevated one ------------------------------
Stop-Bot
Start-ScheduledTask -TaskName $TaskName
Write-Host "Started elevated bot. Open 'Launchers' in the bot to check - the admin warning should be gone."
