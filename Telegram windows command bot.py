# bot.py
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup
from bot_commands import Commands


class TelegramBot:
    def __init__(self):
        detailsDic = {
            "TOKEN": "7054064997:AAGXTjyaqq7ftF28lem1hHane_D_mORXyjI",
            "CHAT_ID": 7189933239
        }
        self.OWNER_USERNAME = "Oh_tech"
        self.TOKEN = detailsDic["TOKEN"]
        self.OWNER_CHAT_ID = detailsDic["CHAT_ID"]
        self.bot_commands = Commands(self.OWNER_CHAT_ID)

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
            [KeyboardButton("🎬 NETFLIX commands")],
            [KeyboardButton("⌨️ Keyboard")]
        ]
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text="""
            Welcome to Ori's bot, this bot controls my computer!\nThis bot is private! But you can download the source code from Github and adapt it to your computer!
            """,
            reply_markup=ReplyKeyboardMarkup(buttons)
        )

    def handle_message(self, update, context):
        security_check = self.security_check(update, context)
        if security_check:
            usr_msg = update.message.text.strip().lower()
            response = self.bot_commands.execute_command (usr_msg, update)
            if response:
                if len(response) > 4096:
                    for i in range(0, len(response), 4096):
                        context.bot.send_message(chat_id=self.OWNER_CHAT_ID, text=response[i:4096 + i])
                else:
                    context.bot.send_message(chat_id=self.OWNER_CHAT_ID, text=response)

    def security_check(self, update, context):
        user_info = update.message.chat
        user_username = user_info["username"]
        user_first_name = user_info["first_name"]
        user_last_name = user_info["last_name"]
        user_id = user_info["id"]
        if str(user_info["username"]) != self.OWNER_USERNAME:
            context.bot.send_message(
                chat_id=self.OWNER_CHAT_ID,
                text='[!] Someone tried to use this bot.\n' +
                     'their username is: @' + str(user_username) + '\n' +
                     'their first name is: ' + str(user_first_name) + '\n' +
                     'their last name is: ' + str(user_last_name) + '\n' +
                     'their id is: ' + str(user_id) + '\n'
                     'their attempt was: ' + update.message.text.strip().lower())
            context.bot.send_message(
                chat_id=user_id,
                text="Only the owner can send commands to the computer,\nI have reported your activity to the " +
                     "owner!\nThe owner will text to you soon, don't worry, He is a very nice person.")
            return False
        else:
            return True

    def handle_callback(self, update, context):
        query = update.callback_query
        query.answer()
        data = query.data
        keys_msg = query.message.text.lower()
        if 'VLC' in keys_msg:
            self.bot_commands.handle_vlc_command(data)
        elif 'netflix' in keys_msg:
            self.bot_commands.handle_netflix_command(data)
        elif 'keyboard' in keys_msg:
            self.bot_commands.keyboard_command(data)

    def error(self, update, context):
        print("Update {} caused error {}".format(update, context.error))

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
