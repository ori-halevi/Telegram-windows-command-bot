@echo off
cd /d "%~dp0"
call "venv2\Scripts\activate.bat"
python "Telegram windows command bot.py"
pause
