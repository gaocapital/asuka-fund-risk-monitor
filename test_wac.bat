@echo off
REM Quick test of edinet_wac_extractor.py + apply_verified_wac.py
REM Skips the full 6-min orchestrator — runs just WAC extraction + apply
REM so we can verify the XBRL tag fix worked end-to-end.
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
echo ============================================================
echo   WAC EXTRACTOR + APPLY (standalone test)
echo ============================================================
echo.

python edinet_wac_extractor.py --mode auto --lookback-days 90
if errorlevel 1 (
    echo  [error] wac extractor failed
    pause
    exit /b 1
)

REM Find newest wac_extract_*.json (auto OR legacy hardcoded mode)
for /f "delims=" %%i in ('dir /b /o-d wac_output\wac_extract_*.json 2^>nul') do (
    set LATEST=wac_output\%%i
    goto :found
)
echo  [error] no wac_output\wac_extract_*.json found
pause
exit /b 1

:found
echo.
echo  Applying verified WACs from !LATEST!...
python apply_verified_wac.py "!LATEST!"

echo.
echo  Done. Re-run generate_dashboard.py to refresh the dashboard HTML.
pause
