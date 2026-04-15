@echo off
echo Restarting...
pm2 restart all
echo ✅ Restarted
echo Use 'pm2 logs' to see logs
pause
