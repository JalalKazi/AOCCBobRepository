@echo off
echo =============================================
echo  RCA Analyzer - Root Cause Analysis Tool
echo =============================================
echo.

:: Check Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

:: Install dependencies if needed
IF NOT EXIST ".deps_installed" (
    echo Installing dependencies...
    pip install -r requirements.txt
    IF %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install dependencies.
        pause
        exit /b 1
    )
    echo. > .deps_installed
)

:: Launch app
echo Launching RCA Analyzer...
python app.py
