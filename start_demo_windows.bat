@echo off
title IoT Demo - Multiple Publishers and Subscribers

:: Store the current directory
set "PROJECT_DIR=%~dp0"

:: Check for admin privileges and restart with admin rights if needed
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :continue
) else (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs -WorkingDirectory '%PROJECT_DIR%'"
    exit /b
)

:continue
:: Start Mosquitto broker if not already running
net start mosquitto >nul 2>&1

:: Clear screen
cls
echo Starting IoT Demo with Multiple Publishers and Subscribers...
echo Current Directory: %PROJECT_DIR%
echo.

:: Start Publishers
echo Starting Publishers...
start "Publisher 1" cmd /k "cd /d "%PROJECT_DIR%" && python group_5_publisher.py"
start "Publisher 2" cmd /k "cd /d "%PROJECT_DIR%" && python group_5_publisher.py"
start "Publisher 3" cmd /k "cd /d "%PROJECT_DIR%" && python group_5_publisher.py"

echo.
echo Starting Subscribers...

:: Start Subscribers
start "Subscriber 1" cmd /k "cd /d "%PROJECT_DIR%" && python group_5_subscriber.py"
start "Subscriber 2" cmd /k "cd /d "%PROJECT_DIR%" && python group_5_subscriber.py"
start "Subscriber 3" cmd /k "cd /d "%PROJECT_DIR%" && python group_5_subscriber.py"

echo.
echo Demo is running! All publishers and subscribers are active.
echo Press any key to close all windows...
pause >nul

:: Kill all python processes (cleanup)
echo Cleaning up...
taskkill /F /IM python.exe >nul 2>&1
echo Done!
exit



