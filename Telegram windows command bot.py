# bot.py
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup
from bot_commands import Commands
import os

class TelegramBot:
    def __init__(self):
        detailsDic = {
            "TOKEN": "7054064997:AAGXTjyaqq7ftF28lem1hHane_D_mORXyjI",
            "CHAT_ID": 7189933239
        }
        self.OWNER_USERNAME = "Oh_tech"
        self.TOKEN = detailsDic["TOKEN"]
        self.CHAT_ID = detailsDic["CHAT_ID"]
        self.bot_commands = Commands(self.CHAT_ID)

    def start_command(self, update, context):
        buttons = [
            [KeyboardButton("📡 Turn Hot-spot on and off")],
            [KeyboardButton("🎧 Turn Bluetooth on and off")],
            [KeyboardButton("🖥 Go dark")],
            [KeyboardButton("💤 Sleep")],
            [KeyboardButton("⚠ Screen status")],
            [KeyboardButton("🔒 Lock screen")],
            [KeyboardButton("📸 Take screenshot")],
            [KeyboardButton("🎥 Screen recording")],
            [KeyboardButton("✂ Paste clipboard")],
            [KeyboardButton("📄 List process")],
            [KeyboardButton("💡 More commands")],
            [KeyboardButton("🎦 VLC commands")],
            [KeyboardButton("⌨️ Keyboard")]
        ]
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text="I will do what you command.",
            reply_markup=ReplyKeyboardMarkup(buttons)
        )

    def handle_message(self, update, context):
        usr_msg = update.message.text.strip().lower()
        response = self.bot_commands.execute_command(usr_msg, update)
        if response:
            if len(response) > 4096:
                for i in range(0, len(response), 4096):
                    context.bot.send_message(chat_id=self.CHAT_ID, text=response[i:4096+i])
            else:
                context.bot.send_message(chat_id=self.CHAT_ID, text=response)

    def handle_callback(self, update, context):
        query = update.callback_query
        query.answer()
        data = query.data

        # טיפול בפקודות VLC
        if data in ['play', 'prev', 'stop', 'next', 'short_jump_forward', 'short_jump_backward',
                    'medium_short_jump_forward', 'medium_short_jump_backward', 'vol_up', 'vol_down', 'next_audio_track',
                    'next_sub', 'change_lang']:
            self.bot_commands.handle_vlc_command(data)

        # טיפול בלחיצות מקלדת
        else:
            self.bot_commands.keyboard_command(data)

    def error(self, update, context):
        print(f"Update {update} caused error {context.error}")

    def start_bot(self):
        updater = Updater(self.TOKEN, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start_command))
        dp.add_handler(MessageHandler(Filters.text, self.handle_message))
        dp.add_error_handler(self.error)
        dp.add_handler(CallbackQueryHandler(self.handle_callback))
        updater.start_polling()
        print("[+] BOT has started")
        updater.idle()

if __name__ == "__main__":
    bot = TelegramBot()
    bot.start_bot()
