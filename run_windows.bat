@echo off
setlocal enabledelayedexpansion
title GerehGosha (گره‌گشا) - Unified Console Runner

echo ==============================================================
echo    GerehGosha (گره‌گشا) - Windows Automated Runner
echo    Developed by Amir (@amirmarandidev)
echo ==============================================================
echo.

:: 1. Check Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not added to your system PATH!
    echo Please install Python 3.10+ from https://www.python.org/
    echo Make sure to check 'Add Python to PATH' during installation.
    pause
    exit /b 1
)

:: 2. Check and install Python dependencies
echo [*] Checking Python dependencies...
python -m pip install -q -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [!] Warning: Some dependencies could not be verified automatically. Proceeding...
) else (
    echo [+] Dependencies verified.
)
echo.

:: 3. Check for Tor Expert Bundle on Windows
set "TOR_FOUND=0"
if exist "assets\Tor\tor.exe" set "TOR_FOUND=1"
if exist "assets\tor\tor.exe" set "TOR_FOUND=1"
if exist "pasarguard-tor\Tor\tor.exe" set "TOR_FOUND=1"
if exist "pasarguard-tor\tor\tor.exe" set "TOR_FOUND=1"
if exist "Tor\tor.exe" set "TOR_FOUND=1"
if exist "tor\tor.exe" set "TOR_FOUND=1"
where tor.exe >nul 2>&1
if %ERRORLEVEL% equ 0 set "TOR_FOUND=1"

if "%TOR_FOUND%"=="0" (
    echo [*] Tor binary not detected. Downloading Tor Expert Bundle for Windows...
    if not exist "assets\Tor" mkdir "assets\Tor"
    curl -sSL "https://dist.torproject.org/torbrowser/15.0.17/tor-expert-bundle-windows-x86_64-15.0.17.tar.gz" -o "%TEMP%\tor_bundle.tar.gz"
    if exist "%TEMP%\tor_bundle.tar.gz" (
        tar -xzf "%TEMP%\tor_bundle.tar.gz" -C "assets"
        del "%TEMP%\tor_bundle.tar.gz" >nul 2>&1
        echo [+] Tor Expert Bundle downloaded and extracted.
    ) else (
        echo [!] Note: Tor will be auto-downloaded on first engine startup.
    )
    echo.
)

:: 4. Clean up any hanging tor processes from previous runs
taskkill /F /IM tor.exe >nul 2>&1

:: 5. Display Admin Credentials (just like Linux install.sh)
echo [*] Checking administrator credentials...
python gerehgosha-cli.py --ensure-admin
echo.

:: 6. Open browser in background after 4 second delay
echo [*] Launching Web Dashboard in browser (http://127.0.0.1:5000)...
start /b cmd /c "timeout /t 4 /nobreak >nul && start http://127.0.0.1:5000"

:: 7. Launch Unified Services
echo [*] Starting GerehGosha Gateway and Routing Engine...
echo [*] Press Ctrl+C anytime in this window to stop all services.
echo.
python start_all.py

pause
