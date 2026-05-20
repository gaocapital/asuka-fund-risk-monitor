@echo off
REM ============================================================
REM   One-shot WAC backfill — 365-day lookback
REM ============================================================
REM   Designed to find the older Sankei × CIE / Ines × AVI /
REM   Sanyo Shokai × AVI filings that the daily 90-day window
REM   doesn't catch.
REM ============================================================

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
echo   WAC BACKFILL  (365-day lookback)
echo ============================================================
echo   ~36s of EDINET API walk + ~1 XBRL fetch per target.
echo   Expect ~60-120s total wall time.
echo.

python edinet_wac_extractor.py --mode auto --lookback-days 365
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
echo  Re-rendering dashboard...
python generate_dashboard.py

echo.
echo  Done. Attribution pill should now reflect any newly-verified WACs.
pause
