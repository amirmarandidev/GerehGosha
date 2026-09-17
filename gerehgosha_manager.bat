@echo off
setlocal enabledelayedexpansion
title GerehGosha (گره‌گشا) - Windows Management Console

:menu
cls
echo ==============================================================
echo           GerehGosha (گره‌گشا) Manager [Windows]
echo              Developed by Amir (@amirmarandidev)
echo ==============================================================
echo.
echo  1. Start GerehGosha (Unified Gateway + Tor Engine)
echo  2. View Active Admin Credentials (Login Info)
echo  3. Manage Admin Accounts (Interactive CLI)
echo  4. Quick Reset Admin Password
echo  5. Network & System Diagnostics (Health Check)
echo  6. Download / Update Tor Expert Bundle ^& GeoIP
echo  7. Flush Tor Cache ^& Circuit State
echo  8. Fetch PasarGuard Admin Token
echo  9. Force Stop Background Processes (tor.exe)
echo 10. Open Web Dashboard in Browser (http://127.0.0.1:5000)
echo  0. Exit
echo.
echo ==============================================================
set /p opt="Select an option [0-10]: "

if "%opt%"=="1" goto start_services
if "%opt%"=="2" goto view_credentials
if "%opt%"=="3" goto manage_admins
if "%opt%"=="4" goto quick_reset
if "%opt%"=="5" goto diagnostics
if "%opt%"=="6" goto update_tor
if "%opt%"=="7" goto flush_cache
if "%opt%"=="8" goto fetch_token
if "%opt%"=="9" goto stop_all
if "%opt%"=="10" goto open_browser
if "%opt%"=="0" exit /b 0

echo Invalid option. Press any key to retry...
pause >nul
goto menu

:start_services
cls
call run_windows.bat
goto menu

:view_credentials
cls
python gerehgosha-cli.py --show-credentials
pause
goto menu

:manage_admins
cls
python gerehgosha-cli.py
pause
goto menu

:quick_reset
cls
echo ==============================================================
echo            Quick Reset Admin Password
echo ==============================================================
set /p reset_u="Enter username to reset [admin]: "
if "!reset_u!"=="" set "reset_u=admin"
set /p reset_p="Enter new password (leave empty to auto-generate): "
echo.
if "!reset_p!"=="" (
    python gerehgosha-cli.py --reset-user !reset_u!
) else (
    python gerehgosha-cli.py --reset-user !reset_u! --password "!reset_p!"
)
echo.
pause
goto menu

:diagnostics
cls
python gerehgosha-cli.py --status
pause
goto menu

:update_tor
cls
echo ==============================================================
echo   Downloading Tor Expert Bundle and GeoIP for Windows...
echo ==============================================================
if not exist "assets\Tor" mkdir "assets\Tor"
echo [*] Downloading from dist.torproject.org...
curl -sSL "https://dist.torproject.org/torbrowser/15.0.17/tor-expert-bundle-windows-x86_64-15.0.17.tar.gz" -o "%TEMP%\tor_bundle.tar.gz"
if exist "%TEMP%\tor_bundle.tar.gz" (
    tar -xzf "%TEMP%\tor_bundle.tar.gz" -C "assets"
    del "%TEMP%\tor_bundle.tar.gz" >nul 2>&1
    echo [+] Successfully updated Tor Engine and GeoIP database!
) else (
    echo [!] Download failed. Check your internet connection.
)
echo.
pause
goto menu

:flush_cache
cls
python gerehgosha-cli.py --flush-cache
pause
goto menu

:stop_all
cls
echo [*] Terminating any running tor.exe background instances...
taskkill /F /IM tor.exe >nul 2>&1
echo [+] All Tor background processes terminated.
pause
goto menu

:fetch_token
cls
echo ==============================================================
echo            PasarGuard Admin Token Fetcher
echo ==============================================================
set /p pg_host="Enter PasarGuard IP/Host (Default 127.0.0.1): "
if "!pg_host!"=="" set "pg_host=127.0.0.1"
set /p pg_port="Enter PasarGuard Port (Default 54321): "
if "!pg_port!"=="" set "pg_port=54321"
set /p pg_user="Enter PasarGuard Username: "
set /p pg_pass="Enter PasarGuard Password: "
echo.

python gerehgosha-cli.py --fetch-token 2>nul || python -c "
import urllib.request, urllib.parse, json, ssl
url = f'http://!pg_host!:!pg_port!/api/admin/token'
data = urllib.parse.urlencode({'username': '!pg_user!', 'password': '!pg_pass!'}).encode('utf-8')
req = urllib.request.Request(url, data=data)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
try:
    with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
        if resp.status == 200:
            res = json.loads(resp.read().decode())
            tok = res.get('access_token')
            if tok:
                print(f'\n[+] SUCCESS! Your PasarGuard Admin API Token:\n\n{tok}\n')
            else:
                print('\n[!] Logged in, but token not found in response.')
except Exception as e:
    print(f'\n[!] Error fetching token: {e}')
"
pause
goto menu

:open_browser
start http://127.0.0.1:5000
goto menu
