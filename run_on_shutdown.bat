@echo off
REM ===========================================
REM Lab Session Logout on Shutdown
REM ===========================================

REM Change to script directory
cd /d "%~dp0"

REM Write to log
echo. >> shutdown_log.txt
echo ========================================== >> shutdown_log.txt
echo Batch Script Executed >> shutdown_log.txt
echo Date: %date% >> shutdown_log.txt
echo Time: %time% >> shutdown_log.txt
echo ========================================== >> shutdown_log.txt

REM Run Python script (use pythonw for no console)
pythonw shutdown_handler.py

REM If pythonw fails, try python
if errorlevel 1 (
    python shutdown_handler.py
)

REM Wait a moment to ensure completion
timeout /t 2 /nobreak >nul 2>&1

exit /b 0
