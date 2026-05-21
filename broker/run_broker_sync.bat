@echo off
REM Daily broker-email sync - fetch CGSI Position CSV, sync the book, re-render.
REM Register this file as a Windows scheduled task; output goes to broker_sync.log.
cd /d "%~dp0.."
set PYTHONUTF8=1
echo ===== %DATE% %TIME% ===== >> broker\broker_sync.log
python broker\run_broker_sync.py >> broker\broker_sync.log 2>&1
