# bot.py
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup
from bot_commands import *
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# טוען את המשתנים מהקובץ .env
load_dotenv()

# גישה למשתנים
BOT_TOKEN = os.getenv('BOT_TOKEN')
OWNER_USERNAME = os.getenv('OWNER_USERNAME')
OWNER_CHAT_ID = os.getenv('OWNER_CHAT_ID')

# בדיקות להבטיח שהמשתנים נטענו נכון (לא חובה לשימוש בקוד הפקה)
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing in .env file.")
if not OWNER_USERNAME:
    raise ValueError("OWNER_USERNAME is missing in .env file.")
if not OWNER_CHAT_ID:
    raise ValueError("OWNER_CHAT_ID is missing in .env file.")


def start_command(update, context):
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


def error(update, context):
    print("Update {} caused error {}".format(update, context.error))


def handle_callback(update, context):
    query = update.callback_query
    query.answer()
    data = query.data
    keys_msg = query.message.text.lower()
    if 'vlc' in keys_msg:
        handle_vlc_command(data)
    elif 'netflix' in keys_msg:
        handle_netflix_command(data)
    elif 'keyboard' in keys_msg:
        keyboard_command(data)


def save_intruder_info(user_info):
    file_path = "intruders.json"

    # If the file does not exist, we will create it with an empty dictionary
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump({}, file)

    # Reading from the file
    with open(file_path, 'r') as file:
        intruders = json.load(file)

    user_id = str(user_info["id"])

    if user_id in intruders.keys():
        # update
        intruders[user_id]["username"] = user_info["username"]
        intruders[user_id]["first_name"] = user_info["first_name"]
        intruders[user_id]["last_name"] = user_info["last_name"]
        intruders[user_id]["last_attempt"] = user_info["timestamp"]
    else:
        # Added a new intruder with the first timestamp
        intruders[user_id] = {
            "username": user_info["username"],
            "first_name": user_info["first_name"],
            "last_name": user_info["last_name"],
            "first_attempt": user_info["timestamp"],
            "last_attempt": user_info["timestamp"]
        }

    # Re-save to file
    with open(file_path, 'w') as file:
        json.dump(intruders, file, indent=4)
class TelegramBot:
    def __init__(self):
        details_dict = {
            "TOKEN": BOT_TOKEN,
            "CHAT_ID": int(OWNER_CHAT_ID)
        }
        self.OWNER_USERNAME = OWNER_USERNAME
        self.TOKEN = details_dict["TOKEN"]
        self.OWNER_CHAT_ID = details_dict["CHAT_ID"]
        self.bot_commands = Commands(self.OWNER_CHAT_ID)

    def handle_message(self, update, context):
        security_check = self.security_check(update, context)
        if security_check:
            usr_msg = update.message.text.strip().lower()
            response = self.bot_commands.execute_command(usr_msg, update)
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
            alert_message = (
                f"[!] Someone tried to use this bot.\n"
                + (f"Their username is: @{user_username}\n" if user_username else "They don't have a username!\n") +
                f"Their first name is: {user_first_name}\n"
                f"Their last name is: {user_last_name}\n"
                f"Their ID is: {user_id}\n"
                f"Their attempt was: {update.message.text.strip().lower()}"
            )

            context.bot.send_message(
                chat_id=self.OWNER_CHAT_ID,
                text=alert_message)

            intruder_info = {
                "username": user_username,
                "first_name": user_first_name,
                "last_name": user_last_name,
                "id": user_id,
                "timestamp": datetime.now().isoformat()  # זמן האירוע
            }
            save_intruder_info(intruder_info)

            if user_username is None:
                # Forwarding the message sent by the hacker to the admin
                context.bot.forward_message(
                    chat_id=self.OWNER_CHAT_ID,
                    from_chat_id=user_id,
                    message_id=update.message.message_id
                )
            # respond to the intruder
            res_to_intruder = (
                    "Only the owner can send commands to the computer.\n"
                    "I have reported your activity to the owner!\n"
                    "The owner will contact you soon, don't worry, he's a very nice guy.\n"
                    + (f"Your username: @{user_username}\n" if user_username else "") +
                    f"Your first name: {user_first_name}\n"
                    f"Your last name: {user_last_name}\n"
                    f"Your ID: {user_id}"
                )
            context.bot.send_message(
                chat_id=user_id,
                text=res_to_intruder)

            return False
        else:
            return True

    def start_bot(self):
        updater = Updater(self.TOKEN, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start_command))
        dp.add_handler(MessageHandler(Filters.text, self.handle_message))
        dp.add_error_handler(error)
        dp.add_handler(CallbackQueryHandler(handle_callback))
        updater.start_polling()
        print("[+] BOT has started")
        updater.idle()


if __name__ == "__main__":
    bot = TelegramBot()
    bot.start_bot()
