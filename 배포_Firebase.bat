@echo off
cd /d "%~dp0"
echo Firebase Hosting(theedufore-505c8)로 배포합니다...
firebase deploy --only hosting
pause
