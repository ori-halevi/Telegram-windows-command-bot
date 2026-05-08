# bot.py
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup
from bot_commands import *
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import time
import tempfile
import traceback
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
    """
    Safe atomic save with backup, fsync and error logging.
    """
    file_path = "intruders.json"
    backup_path = f"{file_path}.bak"
    ts = time.strftime("%Y%m%d-%H%M%S")

    try:
        # ensure directory exists (if needed)
        dirpath = os.path.dirname(os.path.abspath(file_path))
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

        # create file if doesn't exist
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)

        # read safely
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                intruders = json.load(f)
            except json.JSONDecodeError:
                # If JSON is corrupted, keep a backup and start fresh dict
                intruders = {}
                # save corrupted content to a timestamped file for later inspection
                corrupted_dump = f"{file_path}.corrupted.{ts}"
                try:
                    with open(corrupted_dump, 'wb') as cf:
                        f.seek(0)
                        cf.write(f.read().encode('utf-8', errors='replace'))
                except Exception:
                    pass

        user_id = str(user_info["id"])

        if user_id in intruders:
            intruders[user_id]["username"] = user_info.get("username")
            intruders[user_id]["first_name"] = user_info.get("first_name")
            intruders[user_id]["last_name"] = user_info.get("last_name")
            intruders[user_id]["last_attempt"] = user_info.get("timestamp")
        else:
            intruders[user_id] = {
                "username": user_info.get("username"),
                "first_name": user_info.get("first_name"),
                "last_name": user_info.get("last_name"),
                "first_attempt": user_info.get("timestamp"),
                "last_attempt": user_info.get("timestamp")
            }

        # create a backup copy before overwriting
        try:
            if os.path.exists(file_path):
                # keep only one rotating backup
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.replace(file_path, backup_path)
        except Exception:
            # if backup fails, continue but log
            pass

        # atomic write to temp file then replace
        dir_for_temp = os.path.dirname(os.path.abspath(file_path))
        fd, temp_path = tempfile.mkstemp(dir=dir_for_temp)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as tmpf:
                json.dump(intruders, tmpf, indent=4, ensure_ascii=False)
                tmpf.flush()
                os.fsync(tmpf.fileno())
            # atomic replace
            os.replace(temp_path, file_path)
        except Exception:
            # if something goes wrong, attempt to restore backup
            try:
                if os.path.exists(backup_path):
                    os.replace(backup_path, file_path)
            except Exception:
                pass
            raise

    except Exception as e:
        # Log exception to an error file with traceback for diagnosis
        try:
            with open("intruders_save_error.log", "a", encoding='utf-8') as logf:
                logf.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Exception: {e}\n")
                logf.write(traceback.format_exc())
                logf.write("\n\n")
        except Exception:
            # last resort: print (or silently fail if running as service)
            print("Failed to save intruder info:", e)
            print(traceback.format_exc())

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
            else:
                context.bot.send_message(chat_id=self.OWNER_CHAT_ID, text="/start")
        else:
            self.handle_hacker(update, context)

    def handle_hacker(self, update, context):
        user_info = update.message.chat
        user_username = user_info["username"]
        user_first_name = user_info["first_name"]
        user_last_name = user_info["last_name"]
        user_id = user_info["id"]

        alert_message = (
                f"[!] Someone tried to use this bot.\n" +
                (f"Their username is: @{user_username}\n" if user_username else "They don't have a username!\n") +
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

        # Forwarding the message sent by the hacker to the admin
        if user_username is None:
            context.bot.forward_message(
                chat_id=self.OWNER_CHAT_ID,
                from_chat_id=user_id,
                message_id=update.message.message_id
            )

        # respond to the intruder
        res_to_intruder = (
                "🚨 ALERT! 🚨 Only the owner can send commands to this computer.\n"
                "Your activity has been recorded and logged in full detail.\n"
                "Any further attempts will trigger automated countermeasures.\n"
                "This includes IP tracing, account logging, and immediate blocking.\n"
                "Think twice before sending more commands.\n"
                + (f"Username: @{user_username}\n" if user_username else "") +
                f"First Name: {user_first_name}\n"
                f"Last Name: {user_last_name}\n"
                f"ID: {user_id}\n\n"
                "⚠️ चेतावनी! केवल मालिक ही इस कंप्यूटर को कमांड भेज सकता है।\n"
                "आपकी गतिविधि पूरी तरह दर्ज की गई है।\n"
                "कोई भी आगे की कोशिश स्वत: प्रतिक्रिया को सक्रिय करेगी।\n"
                "इसमें IP ट्रेसिंग, खाता लॉगिंग और तुरंत ब्लॉक करना शामिल है।\n"
                "कृपया आगे कमांड भेजने से पहले दो बार सोचें।"
        )
        context.bot.send_message(
            chat_id=user_id,
            text=res_to_intruder)


    def security_check(self, update, context):
        user_info = update.message.chat
        if str(user_info["username"]) != self.OWNER_USERNAME:
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
