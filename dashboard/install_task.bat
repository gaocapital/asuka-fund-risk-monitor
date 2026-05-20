@echo off
REM ============================================================================
REM  Asuka Active Book Daily Risk - Task Scheduler Installer
REM ============================================================================
REM  Installs a Windows scheduled task that runs the dashboard every weekday
REM  at 08:00 local time (SGT, since the GAO machine is set to Asia/Singapore).
REM
REM  Usage: Right-click -> "Run as administrator" -> done.
REM         Or run from cmd: install_task.bat
REM
REM  To uninstall:  schtasks /Delete /TN "Asuka_ActiveBook_DailyRisk" /F
REM  To run now:    schtasks /Run /TN "Asuka_ActiveBook_DailyRisk"
REM  To check:      schtasks /Query /TN "Asuka_ActiveBook_DailyRisk" /V /FO LIST
REM ============================================================================

setlocal

set TASK_NAME=Asuka_ActiveBook_DailyRisk
set INSTALL_DIR=C:\Users\GAO\GAO\Asuka_EDINET
set SCRIPT=run_daily_dashboard.py
set SCHEDULE_TIME=08:00

echo.
echo ============================================================================
echo  Asuka Active Book Daily Risk - Installing scheduled task
echo ============================================================================
echo  Task name:   %TASK_NAME%
echo  Run time:    %SCHEDULE_TIME% local (SGT) every weekday
echo  Install dir: %INSTALL_DIR%
echo  Script:      %SCRIPT%
echo ============================================================================
echo.

REM Verify the install directory exists
if not exist "%INSTALL_DIR%\%SCRIPT%" (
    echo ERROR: %INSTALL_DIR%\%SCRIPT% not found.
    echo Edit INSTALL_DIR at top of this batch file or copy the package there.
    exit /b 1
)

REM Delete prior task if it exists (idempotent install)
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1

REM Create new task. /SC WEEKLY + /D MON,TUE,WED,THU,FRI = weekdays only.
schtasks /Create ^
    /TN "%TASK_NAME%" ^
    /TR "python.exe \"%INSTALL_DIR%\%SCRIPT%\"" ^
    /SC WEEKLY ^
    /D MON,TUE,WED,THU,FRI ^
    /ST %SCHEDULE_TIME% ^
    /RL LIMITED ^
    /F

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Task creation failed.
    exit /b 1
)

REM Set working directory for the task (schtasks doesn't set this directly,
REM so we use PowerShell to add it to the action).
powershell -NoProfile -Command ^
    "$task = Get-ScheduledTask -TaskName '%TASK_NAME%';" ^
    "$action = $task.Actions[0];" ^
    "$action.WorkingDirectory = '%INSTALL_DIR%';" ^
    "Set-ScheduledTask -TaskName '%TASK_NAME%' -Action $action | Out-Null"

echo.
echo ============================================================================
echo  Installed.
echo ============================================================================
echo  - Task will fire at %SCHEDULE_TIME% Mon-Fri (SGT local time)
echo  - To verify:  schtasks /Query /TN "%TASK_NAME%" /V /FO LIST
echo  - To run now: schtasks /Run /TN "%TASK_NAME%"
echo  - Output:     %INSTALL_DIR%\dashboard.html
echo  - State log:  %INSTALL_DIR%\state\dashboard_state_YYYYMMDD.json
echo ============================================================================
echo.

endlocal
