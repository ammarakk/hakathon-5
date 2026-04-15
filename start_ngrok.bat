@echo off
echo ============================================
echo NGROK SETUP - Nur Scents WhatsApp
echo ============================================
echo.

echo Step 1: Checking ngrok...
cd C:\Users\User\Downloads
if exist ngrok.exe (
    echo [OK] ngrok found
) else (
    echo [ERROR] ngrok not found
    pause
    exit /b 1
)

echo.
echo Step 2: Starting ngrok tunnel...
echo This will expose localhost:8000 to the internet
echo.
echo IMPORTANT: You will see a URL like:
echo https://xxxx-xxxx-xxxx.ngrok-free.app
echo.
echo Copy this URL and press Ctrl+C to stop
echo.

ngrok.exe http 8000

pause
