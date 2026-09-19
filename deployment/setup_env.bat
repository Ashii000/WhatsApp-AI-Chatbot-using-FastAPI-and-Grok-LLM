@echo off
title Environment Setup - WhatsApp AI Bot
echo ===================================================
echo   WhatsApp AI Bot - Windows Server Environment Setup
echo ===================================================
echo.

echo [1/3] Checking Python Installation...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.10+ and make sure to check "Add to PATH" during installation.
    pause
    exit /b
)
echo Python is successfully installed!

echo.
echo [2/3] Creating Virtual Environment (venv)...
cd %~dp0\..
python -m venv venv
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b
)
echo Virtual environment created successfully!

echo.
echo [3/3] Activating venv and Installing Dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install requirements. Check if requirements.txt exists.
    pause
    exit /b
)

echo.
echo ===================================================
echo   Setup Complete! The system is fully ready to run.
echo ===================================================
pause