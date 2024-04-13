pyinstaller --onefile -w -i "bot.png" "Telegram windows command bot.py"
move "dist\Telegram windows command bot.exe"
rd /s /q build
rd /s /q dist
del "Telegram windows command bot.spec"
