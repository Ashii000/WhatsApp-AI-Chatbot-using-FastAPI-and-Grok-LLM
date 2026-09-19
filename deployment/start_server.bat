@echo off
title WhatsApp AI Bot Engine
echo =========================================
echo   Starting WhatsApp AI Bot Webhook Server
echo =========================================

:: Move to the root directory of the project
cd %~dp0\..

echo Activating Virtual Environment...
call venv\Scripts\activate

echo Launching High-Performance ASGI Server...
:: Runs Uvicorn with 4 worker processes to handle massive concurrent traffic
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

echo.
echo [WARNING] Server stopped unexpectedly!