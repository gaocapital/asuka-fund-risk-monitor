@echo off
REM Diagnostic wrapper for wac_xbrl_dump.py — opens a cmd, runs the dump,
REM keeps the window open so you can read the output.
setlocal enabledelayedexpansion
cd /d "%~dp0"
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat

if exist ".env" (
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        if "%%a"=="EDINET_API_KEY" set EDINET_API_KEY=%%b
    )
)

echo.
echo  Running wac_xbrl_dump.py (uses most recent docID from wac_output)...
echo.

python wac_xbrl_dump.py %*

echo.
pause
