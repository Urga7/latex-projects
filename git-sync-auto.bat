@echo off
cd /d "%~dp0"
git pull
git add .
git commit -m "Auto-Sync: %date% %time%"
git push
exit