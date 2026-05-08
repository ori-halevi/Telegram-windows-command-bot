"""Static user-facing strings — welcome, intruder, about."""
from __future__ import annotations

GITHUB_URL = "https://github.com/ori-halevi/Telegram-windows-command-bot"

INTRUDER_MESSAGE = (
    "🚨 Only the owner can use this bot. Your activity has been logged.\n\n"
    "🚨 केवल मालिक ही इस बॉट का उपयोग कर सकता है। आपकी गतिविधि दर्ज की गई है।\n\n"
    "🚨 Только владелец может использовать этого бота. Ваша активность зарегистрирована.\n\n"
    "🚨 Solo el propietario puede usar este bot. Tu actividad ha sido registrada.\n\n"
    "🚨 仅所有者可以使用此机器人。您的活动已被记录。\n\n"
    "🚨 يمكن للمالك فقط استخدام هذا الروبوت. تم تسجيل نشاطك.\n\n"
    "🚨 Seul le propriétaire peut utiliser ce bot. Votre activité a été enregistrée.\n\n"
    "🚨 Nur der Besitzer darf diesen Bot benutzen. Deine Aktivität wurde protokolliert.\n\n"
    "🚨 Apenas o proprietário pode usar este bot. Sua atividade foi registrada.\n\n"
    "🚨 このボットはオーナーのみ使用できます。あなたの活動は記録されました。\n\n"
    "🚨 Bu botu yalnızca sahibi kullanabilir. Etkinliğiniz kaydedildi.\n\n"
    "🚨 רק הבעלים יכול להשתמש בבוט הזה. הפעילות שלך תועדה.\n\n"
    "ℹ️ This bot is open-source. You can download it and run your own:\n"
    f"{GITHUB_URL}"
)

WELCOME_MESSAGE = (
    "Welcome to your Windows command bot v2 🎛\n"
    "Tap a button or send /help for the full command list.\n\n"
    "ℹ️ Open source — fork it on GitHub:\n"
    f"{GITHUB_URL}"
)

ABOUT_MESSAGE = (
    "🤖 *Telegram Windows Command Bot v2*\n\n"
    "A Telegram bot that controls a Windows PC remotely:\n"
    "• arbitrary keyboard combos (free-text or interactive builder)\n"
    "• system info, power, audio, brightness, mouse, windows, processes\n"
    "• screenshots, screen recording, webcam\n"
    "• Wi-Fi, Bluetooth, hotspot toggling\n"
    "• VLC + Netflix media controls\n"
    "• shell / PowerShell execution\n\n"
    "🌐 *Source code & setup instructions:*\n"
    f"{GITHUB_URL}\n\n"
    "Anyone can clone it and adapt it to their own machine."
)

HELP_TEXT = (
    "*Telegram Windows Command Bot v2*\n\n"
    "*Keyboard combos (the killer feature):*\n"
    "• `k ctrl+alt+del` — send any combo\n"
    "• `k win+shift+s` — Windows snip tool\n"
    "• `type <text>` — type Unicode text (Hebrew works)\n"
    "• ⌨️ Builder — toggle modifiers (L/R) and tap a key\n"
    "• 🔀 Switcher — interactive Alt+Tab with live screenshots\n\n"
    "*Macros:* `/macro <name>`, `/save_macro <n> <combo>[;<combo>]`, `/list_macros`\n\n"
    "*System:* `info`, `lock`, `sleep`, `hibernate`, `shutdown [s]`, `restart [s]`, `abort_shutdown`\n"
    "*Audio:* `vol <0-100>`, `mute`\n"
    "*Brightness:* `bright <0-100>`\n"
    "*Mouse:* `mouse pos`, `mouse move x y`, `mouse click [left|right]`, `mouse scroll N`\n"
    "*Process:* `ps`, `kill <name|pid>`\n"
    "*Windows:* `focus <title>`, `close <title>`\n"
    "*Files:* `ls [path]`, `pwd`, `cd <path>`, `download <path>`\n"
    "*Network:* `wifi`, `ip`\n"
    "*Clipboard:* `copy <text>`, `paste`\n"
    "*Shell:* `cmd <command>`, `ps1 <command>`, `launch <program>`, `url <link>`\n"
    "*Media:* 🎦 VLC menu, 🎬 Netflix menu\n"
    "*Capture:* 📸 Screenshot, 🎥 Record, 📷 Webcam\n"
    "*Safety:* `/release_keys` — releases any stuck modifier keys\n"
)
