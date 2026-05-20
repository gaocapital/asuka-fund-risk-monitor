@echo off
REM ============================================================================
REM  Asuka Active Book Daily Risk — First-Run Setup
REM ============================================================================
REM  Guided initial setup for a brand-new install. Runs through:
REM    1. Python version check (need 3.10+)
REM    2. Virtual environment creation (recommended; optional)
REM    3. Dependency install (requirements.txt)
REM    4. Required-file presence check
REM    5. Optional .env creation prompt
REM    6. Dry-run to verify no fatal errors
REM    7. Full real run
REM    8. Open dashboard.html in default browser
REM
REM  Re-runnable: idempotent. Skips already-completed steps.
REM
REM  Usage:  Double-click from File Explorer, or:
REM          first_run.bat
REM ============================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

set INSTALL_DIR=%CD%
set PYTHON=python
set VENV_DIR=venv

echo.
echo  ============================================================================
echo    ASUKA ACTIVE BOOK DAILY RISK - FIRST RUN
echo  ============================================================================
echo    Install dir: %INSTALL_DIR%
echo  ============================================================================
echo.

REM ────────────────────────────────────────────────────────────────────────────
REM  STEP 1: Python version check
REM ────────────────────────────────────────────────────────────────────────────
echo  [1/7] Checking Python installation...
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [ERROR] Python not found in PATH.
    echo          Install Python 3.10+ from https://www.python.org/downloads/
    echo          During install, check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

REM Verify Python version is 3.10+
%PYTHON% -c "import sys; v=sys.version_info; exit(0 if (v.major==3 and v.minor>=10) else 1)" 2>nul
if errorlevel 1 (
    echo.
    echo  [ERROR] Python version is too old. Need 3.10 or newer.
    %PYTHON% --version
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('%PYTHON% --version 2^>^&1') do echo   ^✓ %%v
echo.

REM ────────────────────────────────────────────────────────────────────────────
REM  STEP 2: Virtual environment (optional but recommended)
REM ────────────────────────────────────────────────────────────────────────────
echo  [2/7] Virtual environment...

if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo   ^✓ venv already exists at %VENV_DIR%\
    call "%VENV_DIR%\Scripts\activate.bat"
    echo   ^✓ activated
) else (
    echo   No venv found. Create one? Recommended for isolation.
    set /p CREATE_VENV=  Create venv [Y/n]:
    if /i "!CREATE_VENV!"=="" set CREATE_VENV=Y
    if /i "!CREATE_VENV!"=="Y" (
        echo   Creating venv at %VENV_DIR%\ ...
        %PYTHON% -m venv %VENV_DIR%
        if errorlevel 1 (
            echo  [ERROR] venv creation failed
            pause
            exit /b 1
        )
        call "%VENV_DIR%\Scripts\activate.bat"
        echo   ^✓ venv created and activated
    ) else (
        echo   ^- skipping venv, using system Python
    )
)
echo.

REM ────────────────────────────────────────────────────────────────────────────
REM  STEP 3: Install dependencies
REM ────────────────────────────────────────────────────────────────────────────
echo  [3/7] Installing dependencies from requirements.txt...

if not exist "requirements.txt" (
    echo  [ERROR] requirements.txt not found in %INSTALL_DIR%
    pause
    exit /b 1
)

REM Quick check: are core deps already installed?
%PYTHON% -c "import ddgs, requests; import bs4" 2>nul
if not errorlevel 1 (
    echo   ^✓ core dependencies already present
) else (
    echo   Installing... (may take ^~30 seconds)
    pip install -q -r requirements.txt
    if errorlevel 1 (
        echo  [WARN] Some dependencies failed to install.
        echo         Common: blpapi (needs Bloomberg Terminal license)
        echo                 ib_insync (only needed if using IB Gateway)
        echo         The pipeline will work without these — Yahoo intraday is the default.
        echo.
        echo   Trying core deps only...
        pip install -q requests beautifulsoup4 ddgs python-dateutil
    ) else (
        echo   ^✓ all dependencies installed
    )
)
echo.

REM ────────────────────────────────────────────────────────────────────────────
REM  STEP 4: Required-file check
REM ────────────────────────────────────────────────────────────────────────────
echo  [4/7] Checking required files...
set MISSING=0
for %%F in (
    dashboard_data.json
    generate_dashboard.py
    run_daily_dashboard.py
    yahoo_intraday_price_pull.py
) do (
    if not exist "%%F" (
        echo  [ERROR] Missing: %%F
        set /a MISSING+=1
    )
)
if %MISSING% gtr 0 (
    echo.
    echo  [ERROR] %MISSING% required files missing. Re-extract the v3 zip.
    pause
    exit /b 1
)
echo   ^✓ all required files present
echo.

REM ────────────────────────────────────────────────────────────────────────────
REM  STEP 5: Optional .env setup
REM ────────────────────────────────────────────────────────────────────────────
echo  [5/7] EDINET API key (optional — enables WAC extractor)...

if exist ".env" (
    findstr /C:"EDINET_API_KEY=" .env >nul
    if not errorlevel 1 (
        echo   ^✓ .env exists with EDINET_API_KEY
    ) else (
        echo   ^- .env exists but no EDINET_API_KEY set
    )
) else (
    echo   No .env file found.
    echo   The pipeline works without an API key, but the WAC extractor will skip.
    set /p CREATE_ENV=  Create .env now? [y/N]:
    if /i "!CREATE_ENV!"=="Y" (
        echo   Get your free key at: https://disclosure.edinet-fsa.go.jp/api/v2/
        set /p APIKEY=  Paste your EDINET_API_KEY (or press Enter to skip):
        if not "!APIKEY!"=="" (
            echo EDINET_API_KEY=!APIKEY!> .env
            echo   ^✓ .env created
        ) else (
            echo   ^- skipped
        )
    ) else (
        echo   ^- skipped (you can create .env later)
    )
)
echo.

REM ────────────────────────────────────────────────────────────────────────────
REM  STEP 6: Dry run — verify no fatal errors before doing a real run
REM ────────────────────────────────────────────────────────────────────────────
echo  [6/7] Dry run (no writes — just verify pipeline can execute)...
echo.
%PYTHON% run_daily_dashboard.py --dry-run --skip-wac --skip-news
set DRY_RC=%ERRORLEVEL%
echo.
if %DRY_RC% neq 0 (
    echo  [WARN] Dry run exited with code %DRY_RC%. Continuing to real run...
    echo         Most often this is fine — check logs for details.
) else (
    echo   ^✓ dry run completed without fatal errors
)
echo.

REM ────────────────────────────────────────────────────────────────────────────
REM  STEP 7: Real run + open dashboard
REM ────────────────────────────────────────────────────────────────────────────
echo  [7/7] Running the full pipeline...
echo         This pulls Yahoo intraday prices, EDINET filings, TDNet, news.
echo         First run typically takes 3-5 minutes.
echo.
set /p PROCEED=  Proceed with full run? [Y/n]:
if /i "!PROCEED!"=="" set PROCEED=Y
if /i not "!PROCEED!"=="Y" (
    echo   ^- skipped real run. To run later: run_dashboard.bat
    echo.
    pause
    exit /b 0
)

echo.
%PYTHON% run_daily_dashboard.py
set REAL_RC=%ERRORLEVEL%
echo.

REM ────────────────────────────────────────────────────────────────────────────
REM  Done
REM ────────────────────────────────────────────────────────────────────────────
echo  ============================================================================
echo    FIRST RUN COMPLETE
echo  ============================================================================

if %REAL_RC% equ 0 (
    if exist "dashboard.html" (
        echo   ^✓ Pipeline succeeded. Opening dashboard.html in your browser...
        start "" "dashboard.html"
    ) else (
        echo   [WARN] Pipeline reported success but dashboard.html missing.
        echo          Check logs\orchestrator_*.log for details.
    )
) else (
    echo   [WARN] Pipeline exited with code %REAL_RC%.
    echo.
    echo   Most likely:
    echo     - Yahoo blocked your IP (rare^) — wait 30 min and retry
    echo     - EDINET API was down — non-fatal, dashboard still rendered
    echo     - Check logs\orchestrator_*.log for the failing step
    echo.
    if exist "dashboard.html" (
        echo   dashboard.html still exists — opening it...
        start "" "dashboard.html"
    )
)

echo.
echo  ============================================================================
echo    NEXT STEPS
echo  ============================================================================
echo.
echo    Daily routine:
echo      run_dashboard.bat                           ^(double-click^)
echo      OR python run_daily_dashboard.py
echo.
echo    Mid-day refresh:
echo      python yahoo_intraday_price_pull.py         ^(prices only, ~10s^)
echo      python generate_dashboard.py                ^(re-render^)
echo.
echo    Interactive mode (click-to-refresh from browser^):
echo      python dashboard_server.py
echo.
echo    Schedule daily auto-run at 08:00 SGT:
echo      install_task.bat                            ^(needs admin rights^)
echo.
echo    Audit data quality:
echo      python source_attribution_audit.py
echo.
echo    Logs and snapshots:
echo      logs\                                       ^(orchestrator runs^)
echo      attribution_snapshots\                      ^(daily provenance audits^)
echo      state\                                      ^(daily delta snapshots^)
echo.
echo  ============================================================================
echo.
pause
exit /b %REAL_RC%
