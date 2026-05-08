@echo off
cd /d "%~dp0"
call "venv\Scripts\activate.bat"
python "Telegram windows command bot.py"
pause
