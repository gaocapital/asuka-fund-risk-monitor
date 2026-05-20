@echo off
REM Render-only: regenerate dashboard.html from the current dashboard_data.json
REM Skips price/news/EDINET/WAC. Use after manual JSON edits when you just need fresh HTML.

cd /d "%~dp0"
echo.
echo ==============================================================
echo   RENDER-ONLY: dashboard_data.json -^> dashboard.html
echo ==============================================================
echo.

set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

python generate_dashboard.py
if errorlevel 1 (
    echo.
    echo [FAIL] generate_dashboard.py exited with error.
    pause
    exit /b 1
)

echo.
echo [OK] Render complete. Opening dashboard.html...
start "" "dashboard.html"
timeout /t 2 /nobreak >nul
