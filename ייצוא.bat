pyinstaller --onefile -w -i "bot.png" "Windows DHSP Client.py"
move "dist\Windows DHSP Client.exe"
rd /s /q build
rd /s /q dist
del "Windows DHSP Client.spec"

