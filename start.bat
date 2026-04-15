@echo off
echo 🌹 Starting Nur Scents CRM...

REM Logs folder
if not exist logs mkdir logs

REM PM2
echo Starting app processes...
pm2 start ecosystem.config.js
timeout /t 3 /nobreak > nul
pm2 status

echo.
echo ✅ Nur Scents CRM Started!
echo 📡 API:       http://localhost:8000
echo 📊 Logs:      pm2 logs
echo 🛑 Stop:      stop.bat
echo 🔄 Restart:   restart.bat
pause
