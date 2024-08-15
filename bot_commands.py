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


def handle_vlc_command(command):
    if command == 'play':
        pyautogui.press('space')
    elif command == 'prev':
        pyautogui.press('p')
    elif command == 'stop':
        pyautogui.press('s')
    elif command == 'next':
        pyautogui.press('n')
    elif command == 'next_chapter':
        pyautogui.hotkey('shift', 'n')
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
    elif command == 'delay_sub':
        pyautogui.press('g')
    elif command == 'rush_sub':
        pyautogui.press('h')
    elif command == 'change_lang':
        pyautogui.hotkey('win', 'space')


def handle_netflix_command(command):
    if command == 'esc':
        pyautogui.press('esc')
    if command == 'play':
        pyautogui.press('space')
    elif command == 'next_ep':
        for _ in range(6): pyautogui.hotkey('shift', 'tab')
        pyautogui.press('enter')
        # time.sleep(1)
    elif command == 'tab':
        pyautogui.press('tab')
    elif command == 'shift_tab':
        pyautogui.hotkey('shift', 'tab')
    elif command == 'enter':
        pyautogui.press('enter')
    elif command == 'skip_intro':
        for _ in range(3): pyautogui.press('tab')
        pyautogui.press('enter')
    elif command == 'jump_backward':
        pyautogui.press('ctrl')
        pyautogui.press('left')
    elif command == 'jump_forward':
        pyautogui.press('ctrl')
        pyautogui.press('right')
    elif command == 'jump_backward_x_2':
        pyautogui.press('ctrl')
        pyautogui.press('left')
        pyautogui.press('left')
    elif command == 'jump_forward_x_2':
        pyautogui.press('ctrl')
        pyautogui.press('right')
        pyautogui.press('right')
    elif command == 'vol_up':
        pyautogui.press('up')
    elif command == 'vol_down':
        pyautogui.press('down')
    elif command == 'change_lang':
        pyautogui.hotkey('win', 'space')


def keyboard_command(key):
    if key.split()[0] == "alt_tab":
        pyautogui.keyDown('alt')
        pyautogui.press('tab', presses=int(key.split()[1]),
                        interval=0.5)  # Press 'tab' twice with an interval of 0.5 seconds between the presses
        pyautogui.keyUp('alt')
        return
    elif key == "change_lang":
        pyautogui.hotkey('win', 'space')
        return
    elif key == "caps_lock":
        pyautogui.hotkey('capslock')
        return
    pyautogui.press(str(key))


def toggle_hotspot():
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


def toggle_bluetooth():
    pyautogui.hotkey('win', 's')
    time.sleep(1)
    pyautogui.hotkey('win', 'a')
    time.sleep(1)
    pyautogui.press('right')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('esc')


def clean_screen():
    pyautogui.hotkey('win', 's')
    time.sleep(2)
    pyautogui.press('esc')


def lock_screen():
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Screen locked successfully"
    except:
        return "Error while locking screen"


def record_screen():
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


def start_recording():
    temp_dir = tempfile.gettempdir()
    os.chdir(temp_dir)
    video_file_path = record_screen()
    return video_file_path


def take_screenshot():
    temp_dir = tempfile.gettempdir()
    os.chdir(temp_dir)
    with mss() as sct:
        sct.shot(mon=-1)
    return os.path.join(temp_dir, 'monitor-0.png')


def put_to_sleep():
    try:
        subprocess.run(['start', 'shutdown', '/h'], shell=True)
        return "Windows was put to sleep"
    except:
        return "Cannot put Windows to sleep"


def go_dark():
    try:
        subprocess.run(['start', '%SystemRoot%\\System32\\scrnsave.scr', '/s'], shell=True)
        return "Windows went dark"
    except:
        return "Failed to dim windows"


def list_process():
    try:
        proc_list = []
        for proc in psutil.process_iter():
            if proc.name() not in proc_list:
                proc_list.append(proc.name())
        processes = "\n".join(proc_list)
        return processes
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Error listing processes"


def kill_process(proc_name):
    try:
        for proc in psutil.process_iter():
            if proc.name() == proc_name:
                proc.terminate()
                return 'Process terminated successfully'
        return 'Process not found'
    except:
        return 'Error occurred while killing the process'


def open_url(url):
    try:
        webbrowser.open(url)
        return 'Link opened successfully'
    except:
        return 'Error occurred while opening link'


def change_directory(dir_path):
    try:
        os.chdir(dir_path)
        return os.getcwd()
    except:
        return "Directory not found !"


def execute_shell_command(command):
    res = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           stdin=subprocess.DEVNULL)
    stdout = res.stdout.read().decode("utf-8", 'ignore').strip()
    stderr = res.stderr.read().decode("utf-8", 'ignore').strip()
    if stdout:
        return stdout
    elif stderr:
        return stderr
    else:
        return ''


class Commands:
    def __init__(self, chat_id):
        self.CHAT_ID = chat_id

    def execute_command(self, input_text, update):
        usr_msg = input_text.split()
        if input_text == "🎦 vlc commands":
            buttons = [
                [InlineKeyboardButton("⏯", callback_data='play')],
                [InlineKeyboardButton("⏮", callback_data='prev'), InlineKeyboardButton("⏹", callback_data='stop'),
                 InlineKeyboardButton("⏭", callback_data='next')],
                [InlineKeyboardButton("next chapter ⤵", callback_data='next_chapter')],
                [InlineKeyboardButton("⏪ x10s", callback_data='short_jump_backward'),
                 InlineKeyboardButton("⏩ x10s", callback_data='short_jump_forward')],
                [InlineKeyboardButton("⏪ x1m", callback_data='medium_short_jump_backward'),
                 InlineKeyboardButton("⏩ x1m", callback_data='medium_short_jump_forward')],
                [InlineKeyboardButton("➖", callback_data='vol_down'),
                 InlineKeyboardButton("➕", callback_data='vol_up')],
                [InlineKeyboardButton("🗣", callback_data='next_audio_track'),
                 InlineKeyboardButton("✍️", callback_data='next_sub')],
                [InlineKeyboardButton("✍️➖", callback_data='delay_sub'),
                 InlineKeyboardButton("✍️➕", callback_data='rush_sub')],
                [InlineKeyboardButton("🌍", callback_data='change_lang')]
            ]
            keyboard_markup = InlineKeyboardMarkup(buttons)
            update.message.reply_text("Choose a VLC command:", reply_markup=keyboard_markup)
            return

        if input_text == "🎬 netflix commands":
            buttons = [
                [InlineKeyboardButton("Esc", callback_data='esc')],
                [InlineKeyboardButton("⏯", callback_data='play')],
                [InlineKeyboardButton("⏭", callback_data='next_ep')],
                [InlineKeyboardButton("↹", callback_data='tab'),
                 InlineKeyboardButton("⇧ + ↹", callback_data='shift_tab')],
                [InlineKeyboardButton("⏎", callback_data='enter')],
                [InlineKeyboardButton("Skip intro", callback_data='skip_intro')],
                [InlineKeyboardButton("⏪", callback_data='jump_backward'),
                 InlineKeyboardButton("⏩", callback_data='jump_forward')],
                [InlineKeyboardButton("⏪ x2", callback_data='jump_backward_x_2'),
                 InlineKeyboardButton("⏩ x2 ", callback_data='jump_forward_x_2')],
                [InlineKeyboardButton("➖", callback_data='vol_down'),
                 InlineKeyboardButton("➕", callback_data='vol_up')],
                [InlineKeyboardButton("🌍", callback_data='change_lang')]
            ]
            keyboard_markup = InlineKeyboardMarkup(buttons)
            update.message.reply_text("Choose a NETFLIX command:", reply_markup=keyboard_markup)
            return

        if input_text == "⌨️ keyboard":
            buttons = [
                # Esc Backspace
                [InlineKeyboardButton(" ", callback_data='noop'), InlineKeyboardButton("Esc", callback_data='esc'),
                 InlineKeyboardButton("Backspace", callback_data='backspace'),
                 InlineKeyboardButton(" ", callback_data='noop')],

                # F1 F2 F3 F4 F5 F6
                [InlineKeyboardButton("F1", callback_data='f1'), InlineKeyboardButton("F2", callback_data='f2'),
                 InlineKeyboardButton("F3", callback_data='f3'), InlineKeyboardButton("F4", callback_data='f4'),
                 InlineKeyboardButton("F5", callback_data='f5'), InlineKeyboardButton("F6", callback_data='f6')],

                # F7 F8 F9 F10 F11 F12
                [InlineKeyboardButton("F7", callback_data='f7'), InlineKeyboardButton("F8", callback_data='f8'),
                 InlineKeyboardButton("F9", callback_data='f9'), InlineKeyboardButton("F10", callback_data='f10'),
                 InlineKeyboardButton("F11", callback_data='f11'), InlineKeyboardButton("F12", callback_data='f12')],

                # 1 2 3 4 5 6 7 8
                [InlineKeyboardButton("1", callback_data='1'), InlineKeyboardButton("2", callback_data='2'),
                 InlineKeyboardButton("3", callback_data='3'), InlineKeyboardButton("4", callback_data='4'),
                 InlineKeyboardButton("5", callback_data='5'), InlineKeyboardButton("6", callback_data='6'),
                 InlineKeyboardButton("7", callback_data='7'), InlineKeyboardButton("8", callback_data='8')],

                # 9 0 ( ) - = `
                [InlineKeyboardButton("9", callback_data='9'), InlineKeyboardButton("0", callback_data='0'),
                 InlineKeyboardButton("(", callback_data='('), InlineKeyboardButton(")", callback_data=')'),
                 InlineKeyboardButton("-", callback_data='-'), InlineKeyboardButton("+", callback_data='+'),
                 InlineKeyboardButton("=", callback_data='='), InlineKeyboardButton("`", callback_data='`')],

                # Q W E R T Y U
                [InlineKeyboardButton("Q", callback_data='q'), InlineKeyboardButton("W", callback_data='w'),
                 InlineKeyboardButton("E", callback_data='e'), InlineKeyboardButton("R", callback_data='r'),
                 InlineKeyboardButton("T", callback_data='t'), InlineKeyboardButton("Y", callback_data='y'),
                 InlineKeyboardButton("U", callback_data='u')],

                # I O P A S D F
                [InlineKeyboardButton("I", callback_data='i'), InlineKeyboardButton("O", callback_data='o'),
                 InlineKeyboardButton("P", callback_data='p'), InlineKeyboardButton("A", callback_data='a'),
                 InlineKeyboardButton("S", callback_data='s'), InlineKeyboardButton("D", callback_data='d'),
                 InlineKeyboardButton("F", callback_data='f')],

                # G H J K L Z X
                [InlineKeyboardButton("G", callback_data='g'), InlineKeyboardButton("H", callback_data='h'),
                 InlineKeyboardButton("J", callback_data='j'), InlineKeyboardButton("K", callback_data='k'),
                 InlineKeyboardButton("L", callback_data='l'), InlineKeyboardButton("Z", callback_data='z'),
                 InlineKeyboardButton("X", callback_data='x')],

                # C V B N M
                [InlineKeyboardButton(" ", callback_data='noop'), InlineKeyboardButton("C", callback_data='c'),
                 InlineKeyboardButton("V", callback_data='v'), InlineKeyboardButton("B", callback_data='b'),
                 InlineKeyboardButton("N", callback_data='n'), InlineKeyboardButton("M", callback_data='m'),
                 InlineKeyboardButton(" ", callback_data='noop')],

                # [ ] ; '
                [InlineKeyboardButton("[", callback_data='['),
                 InlineKeyboardButton("]", callback_data=']'),
                 InlineKeyboardButton(";", callback_data=';'),
                 InlineKeyboardButton("'", callback_data="'")],

                # / \ , .
                [InlineKeyboardButton("/", callback_data='/'), InlineKeyboardButton("\\", callback_data='\\'),
                 InlineKeyboardButton(",", callback_data=','), InlineKeyboardButton(".", callback_data='.')],

                # Tab Enter Space
                [InlineKeyboardButton("Tab", callback_data='tab'), InlineKeyboardButton("Enter", callback_data='enter'),
                 InlineKeyboardButton("Space", callback_data='space')],

                # Ctrl Alt Shift
                [InlineKeyboardButton("Ctrl", callback_data='ctrl'), InlineKeyboardButton("Alt", callback_data='alt'),
                 InlineKeyboardButton("Shift", callback_data='shift')],

                # ↑
                [InlineKeyboardButton("↑", callback_data='up')],

                # ← ↓ →
                [InlineKeyboardButton("←", callback_data='left'), InlineKeyboardButton("↓", callback_data='down'),
                 InlineKeyboardButton("→", callback_data='right')],

                # Change lang Caps
                [InlineKeyboardButton("🌍", callback_data='change_lang'),
                 InlineKeyboardButton("Caps", callback_data='caps_lock')],

                [InlineKeyboardButton("Alt + Tab, 1", callback_data='alt_tab 1'),
                 InlineKeyboardButton("Alt + Tab, 2", callback_data='alt_tab 2')],
                [InlineKeyboardButton("Alt + Tab, 3", callback_data='alt_tab 3'),
                 InlineKeyboardButton("Alt + Tab, 4", callback_data='alt_tab 4')]
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
            toggle_hotspot()
            return 'Hot-spot command has been activated! /CleanScreen'

        if input_text == '🎧 turn bluetooth on and off':
            toggle_bluetooth()
            return 'Bluetooth command has been activated! /CleanScreen'

        if input_text == '/cleanscreen':
            clean_screen()

        if input_text == '🔒 lock screen':
            return lock_screen()

        if input_text == "📸 take screenshot":
            update.message.bot.send_document(
                chat_id=self.CHAT_ID, document=open(take_screenshot(), 'rb'))
            return

        if input_text == "🎥 screen recording":
            update.message.bot.send_message(
                chat_id=self.CHAT_ID, text="Wait 30 seconds")
            update.message.bot.send_video(
                chat_id=self.CHAT_ID, video=open(start_recording(), 'rb'))
            return

        if input_text == "✂ paste clipboard":
            return pyperclip.paste()

        if input_text == "💤 sleep":
            return put_to_sleep()

        if input_text == "🖥 go dark":
            return go_dark()

        if input_text == "📄 list process":
            return list_process()

        if usr_msg[0] == 'kill':
            return kill_process(usr_msg[1])

        if usr_msg[0] == 'url':
            return open_url(usr_msg[1])

        if usr_msg[0] == "cd":
            return change_directory(usr_msg[1])

        if usr_msg[0] == "download":
            return self.download_file(usr_msg[1], update)

        if usr_msg[0] == "cmd":
            return execute_shell_command(usr_msg[1:])

    def download_file(self, file_path, update):
        if os.path.exists(file_path):
            try:
                document = open(file_path, 'rb')
                update.message.bot.send_document(self.CHAT_ID, document)
            except:
                return "Something went wrong !"
        else:
            return "File not found"
