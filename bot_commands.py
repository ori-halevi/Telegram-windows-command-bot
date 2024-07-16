# bot_commands.py
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
import tempfile
from mss import mss
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Commands:
    def __init__(self, chat_id):
        self.CHAT_ID = chat_id

    def execute_command(self, input_text, update):
        usr_msg = input_text.split()
        if input_text == "🎦 vlc commands":
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
            return

        if input_text == "⌨️ keyboard":
            buttons = [
                [InlineKeyboardButton("Ctrl", callback_data='ctrl'), InlineKeyboardButton("Shift", callback_data='shift'), InlineKeyboardButton("Alt", callback_data='alt')],
                [InlineKeyboardButton("A", callback_data='a'), InlineKeyboardButton("B", callback_data='b'), InlineKeyboardButton("C", callback_data='c')],
                [InlineKeyboardButton("D", callback_data='d'), InlineKeyboardButton("E", callback_data='e'), InlineKeyboardButton("F", callback_data='f')],
                [InlineKeyboardButton("G", callback_data="g"), InlineKeyboardButton("H", callback_data='h'), InlineKeyboardButton("I", callback_data='i')],
            ]
            keyboard_markup = InlineKeyboardMarkup(buttons)
            update.message.reply_text("Choose a keyboard key:", reply_markup=keyboard_markup)
            return

        if input_text == "💡 more commands":
            return "url <link>: open a link on the browser\nkill <proc>: terminate process\ncmd <command>: execute shell command\ncd <dir>: change directory\ndownload <file>: download a file"

        if input_text == '⚠ screen status':
            for proc in psutil.process_iter():
                if proc.name() == "LogonUI.exe":
                    return 'Screen is Locked'
            return 'Screen is Unlocked'

        if input_text == '📡 turn hot-spot on and off':
            self.toggle_hotspot()
            return 'Hot-spot command has been activated! /CleanScreen'

        if input_text == '🎧 turn bluetooth on and off':
            self.toggle_bluetooth()
            return 'Bluetooth command has been activated! /CleanScreen'

        if input_text == '/cleanscreen':
            self.clean_screen()

        if input_text == '🔒 lock screen':
            return self.lock_screen()

        if input_text == "📸 take screenshot":
            update.message.bot.send_document(
                chat_id=self.CHAT_ID, document=open(self.take_screenshot(), 'rb'))
            return

        if input_text == "🎥 screen recording":
            update.message.bot.send_message(
                chat_id=self.CHAT_ID, text="Wait 30 seconds")
            update.message.bot.send_video(
                chat_id=self.CHAT_ID, video=open(self.start_recording(), 'rb'))
            return

        if input_text == "✂ paste clipboard":
            return pyperclip.paste()

        if input_text == "💤 sleep":
            return self.put_to_sleep()

        if input_text == "🖥 go dark":
            return self.go_dark()

        if input_text == "📄 list process":
            return self.list_process()

        if usr_msg[0] == 'kill':
            return self.kill_process(usr_msg[1])

        if usr_msg[0] == 'url':
            return self.open_url(usr_msg[1])

        if usr_msg[0] == "cd":
            return self.change_directory(usr_msg[1])

        if usr_msg[0] == "download":
            return self.download_file(usr_msg[1], update)

        if usr_msg[0] == "cmd":
            return self.execute_shell_command(usr_msg[1:])

    def handle_vlc_command(self, command):
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

    def keyboard_command(self, key):
        print(key)
        pyautogui.press(key)

    def toggle_hotspot(self):
        pyautogui.hotkey('win', 's')
        time.sleep(1)
        pyautogui.hotkey('win', 'a')
        time.sleep(1)
        pyautogui.press('down')
        time.sleep(1)
        pyautogui.press('right')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('esc')

    def toggle_bluetooth(self):
        pyautogui.hotkey('win', 's')
        time.sleep(1)
        pyautogui.hotkey('win', 'a')
        time.sleep(1)
        pyautogui.press('right')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('esc')

    def clean_screen(self):
        pyautogui.hotkey('win', 's')
        time.sleep(2)
        pyautogui.press('esc')

    def lock_screen(self):
        try:
            ctypes.windll.user32.LockWorkStation()
            return "Screen locked successfully"
        except:
            return "Error while locking screen"

    def start_recording(self):
        TEMPDIR = tempfile.gettempdir()
        os.chdir(TEMPDIR)
        video_file_path = self.record_screen()
        return video_file_path

    def record_screen(self):
        duration = 30
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

    def put_to_sleep(self):
        try:
            subprocess.run(['start', 'shutdown', '/h'], shell=True)
            return "Windows was put to sleep"
        except:
            return "Cannot put Windows to sleep"

    def go_dark(self):
        try:
            subprocess.run(['start', '%SystemRoot%\\System32\\scrnsave.scr', '/s'], shell=True)
            return "Windows went dark"
        except:
            return "Failed to dim windows"

    def list_process(self):
        try:
            proc_list = []
            for proc in psutil.process_iter():
                if proc.name() not in proc_list:
                    proc_list.append(proc.name())
            processes = "\n".join(proc_list)
            return processes
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return "Error listing processes"

    def kill_process(self, proc_name):
        try:
            for proc in psutil.process_iter():
                if proc.name() == proc_name:
                    proc.terminate()
                    return 'Process terminated successfully'
            return 'Process not found'
        except:
            return 'Error occurred while killing the process'

    def open_url(self, url):
        try:
            webbrowser.open(url)
            return 'Link opened successfully'
        except:
            return 'Error occurred while opening link'

    def change_directory(self, dir_path):
        try:
            os.chdir(dir_path)
            return os.getcwd()
        except:
            return "Directory not found !"

    def download_file(self, file_path, update):
        if os.path.exists(file_path):
            try:
                document = open(file_path, 'rb')
                update.message.bot.send_document(self.CHAT_ID, document)
            except:
                return "Something went wrong !"
        else:
            return "File not found"

    def execute_shell_command(self, command):
        res = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
        stdout = res.stdout.read().decode("utf-8", 'ignore').strip()
        stderr = res.stderr.read().decode("utf-8", 'ignore').strip()
        if stdout:
            return stdout
        elif stderr:
            return stderr
        else:
            return ''
