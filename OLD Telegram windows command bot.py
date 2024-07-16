"""
This bot works on Python 3.11
"""
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
from mss import mss
import tempfile
import os
import psutil
import ctypes
import webbrowser
import pyperclip
import subprocess
import pyautogui
import cv2
import numpy as np
import time




class TelegramBot:

    def __init__(self):
        """
        # נתיב לתיקיית הסקריפט בלבד
        script_directory = os.path.dirname(os.path.realpath(__file__))
        f = open(script_directory + '\\auth.json')
        """

        detailsDic = {
        "TOKEN":"7054064997:AAGXTjyaqq7ftF28lem1hHane_D_mORXyjI",
        "CHAT_ID": 7189933239
        }
        self.OWNER_USERNAME = "Oh_tech"

        self.TOKEN = detailsDic["TOKEN"]
        self.CHAT_ID = detailsDic["CHAT_ID"]

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
                    [KeyboardButton("🎦 VLC commands")]

        ]
        context.bot.send_message(
            chat_id=update.message.chat.id, text="I will do what you command.", reply_markup=ReplyKeyboardMarkup(buttons))

    def handle_message(self, update, input_text):
        usr_msg = input_text.split()

        if input_text == "vLC commands":

            buttons = [
                [InlineKeyboardButton("⏯", callback_data='play')],
                [InlineKeyboardButton("⏮", callback_data='prev'), InlineKeyboardButton("⏹", callback_data='stop'), InlineKeyboardButton("⏭", callback_data='next')],
                [InlineKeyboardButton("⏪ x10s", callback_data='short_jump_backward'), InlineKeyboardButton("⏩ x10s", callback_data='short_jump_forward')],
                [InlineKeyboardButton("⏪ x1m", callback_data='medium_short_jump_backward'), InlineKeyboardButton("⏩ x1m", callback_data='medium_short_jump_forward')],
                [InlineKeyboardButton("➖", callback_data='vol_down'), InlineKeyboardButton("➕", callback_data='vol_up')],
                [InlineKeyboardButton("🔊", callback_data='next_audio_track'), InlineKeyboardButton("✍️", callback_data='next_sub')],
                [InlineKeyboardButton("🌍", callback_data='change_lang')]
            ]
            keyboard_markup = InlineKeyboardMarkup(buttons)
            update.message.reply_text("Choose a VLC command:", reply_markup=keyboard_markup)

        if input_text == "more commands":
            return """url <link>: open a link on the browser\nkill <proc>: terminate process\ncmd <command>: execute shell command\ncd <dir>: change directory\ndownload <file>: download a file"""

        if input_text == 'screen status':
            for proc in psutil.process_iter():
                if (proc.name() == "LogonUI.exe"):
                    return 'Screen is Locked'
            return 'Screen is Unlocked'

        if input_text == 'turn Hot-spot on and off':
            pyautogui.hotkey('win', 's')
            time.sleep(1)
            pyautogui.hotkey('win', 'a')  # דומה ללחיצה על WIN+A
            time.sleep(1)
            pyautogui.press('down')
            time.sleep(1)
            pyautogui.press('right')
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.press('esc')
            return 'Hot-spot command has been activated! /CleanScreen'

        if input_text == 'turn Bluetooth on and off':
            pyautogui.hotkey('win', 's')
            time.sleep(1)
            pyautogui.hotkey('win', 'a')  # דומה ללחיצה על WIN+A
            time.sleep(1)
            pyautogui.press('right')
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.press('esc')
            return 'Bluetooth command has been activated! /CleanScreen'
        if input_text == '/CleanScreen':
            pyautogui.hotkey('win', 's')
            time.sleep(2)
            pyautogui.press('esc')
        if input_text == 'lock screen':
            try:
                ctypes.windll.user32.LockWorkStation()
                return "Screen locked successfully"
            except:
                return "Error while locking screen"

        if input_text == "take screenshot":
            update.message.bot.send_document(
                chat_id=self.CHAT_ID, document=open(self.take_screenshot(), 'rb'))
            return None


        if input_text == "screen recording":
            update.message.bot.send_message(
                chat_id=self.CHAT_ID, text="Wait 30 seconds")
            update.message.bot.send_video(
                chat_id=self.CHAT_ID, video=open(self.start_recording(), 'rb'))
            return None

        if input_text == "paste clipboard":
            return pyperclip.paste()

        if input_text == "sleep":
            try:
                #os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                subprocess.run(['start', 'shutdown', '/h'], shell=True)
                return "Windows was put to sleep"
            except:
                return "Cannot put Windows to sleep"

        if input_text == "go dark":
            try:
                subprocess.run(['start', '%SystemRoot%\\System32\\scrnsave.scr', '/s'], shell=True)
                return "Windows went dark"
            except:
                return "Failed to dim windows"

        if input_text == "list process":
            try:
                proc_list = []
                for proc in psutil.process_iter():
                    if proc.name() not in proc_list:
                        proc_list.append(proc.name())
                processes = "\n".join(proc_list)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            return processes

        if usr_msg[0] == 'kill':
            proc_list = []
            for proc in psutil.process_iter():
                p = proc_list.append([proc.name(), str(proc.pid)])
            try:
                for p in proc_list:
                    if p[0] == usr_msg[1]:
                        psutil.Process(int(p[1])).terminate()
                return 'Process terminated successfully'
            except:
                return 'Error occurred while killing the process'

        if usr_msg[0] == 'url':
            try:
                webbrowser.open(usr_msg[1])
                return 'Link opened successfully'
            except:
                return 'Error occurred while opening link'

        if usr_msg[0] == "cd":
            if usr_msg[1]:
                try:
                    os.chdir(usr_msg[1])
                except:
                    return "Directory not found !"
                res = os.getcwd()
                if res:
                    return res

        if usr_msg[0] == "download":
            if usr_msg[1]:
                if os.path.exists(usr_msg[1]):
                    try:
                        document = open(usr_msg[1], 'rb')
                        update.message.bot.send_document(
                            self.CHAT_ID, document)
                    except:
                        return "Something went wrong !"

        if usr_msg[0] == "cmd":
            res = subprocess.Popen(
                usr_msg[1:], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
            stdout = res.stdout.read().decode("utf-8", 'ignore').strip()
            stderr = res.stderr.read().decode("utf-8", 'ignore').strip()
            if stdout:
                return (stdout)
            elif stderr:
                return (stderr)
            else:
                return ''

    def handle_callback(self, update, context):
        query = update.callback_query
        query.answer()

        # Execute the command based on the callback_data
        command = query.data
        if command == 'play':
            pyautogui.press('space')
        elif command == 'prev':
            pass
        elif command == 'stop':
            pyautogui.press('s')
        elif command == 'next':
            pyautogui.press('n')
        elif command == 'short_jump_forward':
            pyautogui.hotkey('alt', 'right')
        elif command == 'short_jump_backward':
            pyautogui.hotkey('alt', 'left')
        elif command == 'medium_short_jump_forward':
            pyautogui.hotkey('ctrl', 'right')
        elif command == 'medium_short_jump_backward':
            pyautogui.hotkey('ctrl', 'left')
        elif command == 'vol_up':
            pyautogui.press('up')
        elif command == 'vol_down':
            pyautogui.press('down')
        elif command == 'next_audio_track':
            pyautogui.press('b')
        elif command == 'next_sub':
            pyautogui.press('v')
        elif command == 'change_lang':
            pyautogui.hotkey('win', 'space')

    def error(self, update, context):
        print(f"Update {update} caused error {context.error}")

    def start_recording(self):
        TEMPDIR = tempfile.gettempdir()
        os.chdir(TEMPDIR)

        video_file_path = self.record_screen()  # הקלטת המסך למשך דקה

        # שליחת הסרטון לצ'אט
        return video_file_path

    def record_screen(self):
        # יצירת סרטון במסך
        duration = 30  # זמן בשניות
        video_file_path = os.path.join(tempfile.gettempdir(), 'screen_record.mkv')

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        screen_size = pyautogui.size()
        out = cv2.VideoWriter(video_file_path, fourcc, 20.0, (screen_size.width, screen_size.height))

        start_time = time.time()

        while (time.time() - start_time) < duration:
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)

        out.release()
        return video_file_path
    def take_screenshot(self):
        TEMPDIR = tempfile.gettempdir()
        os.chdir(TEMPDIR)
        with mss() as sct:
            sct.shot(mon=-1)
        return os.path.join(TEMPDIR, 'monitor-0.png')

    def send_response(self, update, context):
        user_message = update.message.text
        # Please modify this
        if update.message.chat["username"] != self.OWNER_USERNAME:
            context.bot.send_message(
                chat_id=self.CHAT_ID,
                text="[!] " + update.message.chat["username"] + ' tried to use this bot')
            context.bot.send_message(
                chat_id=update.message.chat.id,
                text="Only the owner can send commands to the computer,\nI have reported your activity to the owner!")
        else:
            user_message = user_message.encode(
                'ascii', 'ignore').decode('ascii').strip(' ')
            user_message = user_message[0].lower() + user_message[1:]
            response = self.handle_message(update, user_message)
            if response:
                if (len(response) > 4096):
                    for i in range(0, len(response), 4096):
                        context.bot.send_message(
                            chat_id=self.CHAT_ID, text=response[i:4096+i])
                else:
                    context.bot.send_message(
                        chat_id=self.CHAT_ID, text=response)

    def start_bot(self):
        updater = Updater(self.TOKEN, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start_command))
        dp.add_handler(MessageHandler(Filters.text, self.send_response))
        dp.add_error_handler(self.error)
        dp.add_handler(CallbackQueryHandler(self.handle_callback))
        updater.start_polling()
        print("[+] BOT has started")
        updater.idle()


bot = TelegramBot()
bot.start_bot()
