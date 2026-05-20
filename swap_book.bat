@echo off
REM Apply the May 15 2026 ticker-list swap from the xlsx, then re-render.
setlocal enabledelayedexpansion
cd /d "%~dp0"
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat

echo.
echo ============================================================
echo   BOOK TICKER SWAP  (May 15 2026 list)
echo ============================================================
echo.

python apply_position_list.py
if errorlevel 1 (
    echo  [error] swap failed
    pause
    exit /b 1
)

echo.
echo  Re-rendering dashboard.html...
python generate_dashboard.py

echo.
echo  Done. Open dashboard.html to see the new book.
pause
