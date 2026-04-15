@echo off
echo Stopping Nur Scents CRM...
pm2 stop all
pm2 delete all
echo ✅ Stopped
pause
