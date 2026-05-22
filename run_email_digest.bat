@echo off
REM Asuka Fund morning risk digest - emails associates@gao-cap.com via the Gmail API.
REM Registered as the Windows scheduled task "AsukaEmailDigest"; output -> digest.log.
cd /d "%~dp0"
set PYTHONUTF8=1
echo ===== %DATE% %TIME% ===== >> digest.log
python email_digest.py --send >> digest.log 2>&1
