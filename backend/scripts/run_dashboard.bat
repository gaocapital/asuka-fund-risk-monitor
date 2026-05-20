@echo off
REM ============================================================
REM   Asuka Daily Dashboard - One-Click Refresh
REM ============================================================
REM   Runs the full pipeline:
REM     1. Price refresh (IB > Bloomberg > Yahoo)
REM     2. EDINET filings ingest
REM     3. WAC extractor + apply (if EDINET_API_KEY set)
REM     4. TDNet adhoc scan
REM     5. News scan (DuckDuckGo)
REM     6. Dashboard render
REM     7. Verification audit
REM   Then opens dashboard.html in your browser.
REM ============================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo  ============================================================
echo    ASUKA DAILY DASHBOARD
echo  ============================================================
echo.

REM ---- Activate venv if present ----
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo  [warn] No venv found at venv\ -- using system Python
)

REM ---- First-run dependency check ----
python -c "import ddgs" 2>nul
if errorlevel 1 (
    echo  [first-run] Installing news scan dependency: ddgs
    pip install ddgs --quiet
)

REM ---- Load EDINET_API_KEY from .env if present ----
if exist ".env" (
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        if "%%a"=="EDINET_API_KEY" set EDINET_API_KEY=%%b
    )
    if defined EDINET_API_KEY (
        echo  [config] EDINET_API_KEY loaded from .env
    )
) else (
    echo  [config] No .env found - WAC extractor will be skipped
)

echo.
echo  Starting orchestrator...
echo.

REM ---- Run the orchestrator with any args passed through ----
python run_daily_dashboard.py %*
set RC=%ERRORLEVEL%

REM ---- Open the dashboard if render succeeded ----
echo.
if %RC%==0 (
    if exist "dashboard.html" (
        echo  Opening dashboard in your default browser...
        start "" "dashboard.html"
    )
) else (
    echo  [error] Orchestrator exited with code %RC%
    echo  Check logs\orchestrator_*.log for details
)

echo.
pause
exit /b %RC%
