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
            'TOKEN': '7054064997:AAGXTjyaqq7ftF28lem1hHane_D_mORXyjI',
            'CHAT_ID': 7189933239
        }
        self.OWNER_USERNAME = 'Oh_tech'
        self.TOKEN = detailsDic['TOKEN']
        self.CHAT_ID = detailsDic['CHAT_ID']


    def start_command(self, update, context):
        buttons = [
            [
                KeyboardButton('≡ƒôí Turn Hot-spot on and off')],
            [
                KeyboardButton('≡ƒÄº Turn Bluetooth on and off')],
            [
                KeyboardButton('≡ƒûÑ Go dark')],
            [
                KeyboardButton('≡ƒÆñ Sleep')],
            [
                KeyboardButton('≡ƒô╕ Take screenshot')],
            [
                KeyboardButton('≡ƒÄÑ Screen recording')],
            [
                KeyboardButton('≡ƒº⌐Start Minecraft server')],
            [
                KeyboardButton('ΓÜá Screen status')],
            [
                KeyboardButton('≡ƒöÆ Lock screen')],
            [
                KeyboardButton('Γ£é Paste clipboard')],
            [
                KeyboardButton('≡ƒôä List process')],
            [
                KeyboardButton('≡ƒÆí More commands')],
            [
                KeyboardButton('≡ƒÄª VLC commands')]]
        context.bot.send_message(chat_id = update.message.chat.id, text = 'I will do what you command.', reply_markup = ReplyKeyboardMarkup(buttons))


    def handle_message(self, update, input_text):
        usr_msg = input_text.split()
        if input_text == 'vLC commands':
            buttons = [
                [
                    InlineKeyboardButton('ΓÅ»', callback_data = 'play')],
                [
                    InlineKeyboardButton('ΓÅ«', callback_data = 'prev'),
                    InlineKeyboardButton('ΓÅ╣', callback_data = 'stop'),
                    InlineKeyboardButton('ΓÅ¡', callback_data = 'next')],
                [
                    InlineKeyboardButton('ΓÅ¬ x10s', callback_data = 'short_jump_backward'),
                    InlineKeyboardButton('ΓÅ⌐ x10s', callback_data = 'short_jump_forward')],
                [
                    InlineKeyboardButton('ΓÅ¬ x1m', callback_data = 'medium_short_jump_backward'),
                    InlineKeyboardButton('ΓÅ⌐ x1m', callback_data = 'medium_short_jump_forward')],
                [
                    InlineKeyboardButton('Γ₧û', callback_data = 'vol_down'),
                    InlineKeyboardButton('Γ₧ò', callback_data = 'vol_up')],
                [
                    InlineKeyboardButton('≡ƒîì', callback_data = 'change_lang')]]
            keyboard_markup = InlineKeyboardMarkup(buttons)
            update.message.reply_text('Choose a VLC command:', reply_markup = keyboard_markup)
        if input_text == 'more commands':
            return 'url <link>: open a link on the browser\nkill <proc>: terminate process\ncmd <command>: execute shell command\ncd <dir>: change directory\ndownload <file>: download a file'
        if None == 'screen status':
            for proc in psutil.process_iter():
                if proc.name() == 'LogonUI.exe':
                    return 'Screen is Locked'
                return 'Screen is Unlocked'
        if input_text == 'turn Hot-spot on and off':
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
            return 'Hot-spot command has been activated! /CleanScreen'
        if None == 'turn Bluetooth on and off':
            pyautogui.hotkey('win', 's')
            time.sleep(1)
            pyautogui.hotkey('win', 'a')
            time.sleep(1)
            pyautogui.press('right')
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.press('esc')
            return 'Bluetooth command has been activated! /CleanScreen'
        if None == '/CleanScreen':
            pyautogui.hotkey('win', 's')
            time.sleep(2)
            pyautogui.press('esc')
        if input_text == 'start Minecraft server':
            batch_file_path = 'C:\\Users\\OH\\Desktop\\Minecraft SERVER 1.20.5\\START.BAT - Shortcut'
            os.startfile(batch_file_path)
            return 'Server started!'
        if None == 'lock screen':
            ctypes.windll.user32.LockWorkStation()
            return 'Screen locked successfully'
        return 'Error while locking screen'
    # WARNING: Decompyle incomplete


    def handle_callback(self, update, context):
        query = update.callback_query
        query.answer()
        command = query.data
        if command == 'play':
            pyautogui.press('space')
            return None
        if None == 'prev':
            return None
        if None == 'stop':
            pyautogui.press('s')
            return None
        if None == 'next':
            pyautogui.press('n')
            return None
        if None == 'short_jump_forward':
            pyautogui.hotkey('alt', 'right')
            return None
        if None == 'short_jump_backward':
            pyautogui.hotkey('alt', 'left')
            return None
        if None == 'medium_short_jump_forward':
            pyautogui.hotkey('ctrl', 'right')
            return None
        if None == 'medium_short_jump_backward':
            pyautogui.hotkey('ctrl', 'left')
            return None
        if None == 'vol_up':
            pyautogui.press('up')
            return None
        if None == 'vol_down':
            pyautogui.press('down')
            return None
        if None == 'change_lang':
            pyautogui.hotkey('win', 'space')
            return None


    def error(self, update, context):
        print(f'''Update {update} caused error {context.error}''')


    def start_recording(self):
        TEMPDIR = tempfile.gettempdir()
        os.chdir(TEMPDIR)
        video_file_path = self.record_screen()
        return video_file_path


    def record_screen(self):
Unsupported opcode: CALL_FUNCTION_EX
        duration = 30
        video_file_path = os.path.join(tempfile.gettempdir(), 'screen_record.mkv')
    # WARNING: Decompyle incomplete


    def take_screenshot(self):
Unsupported opcode: BEFORE_WITH
        TEMPDIR = tempfile.gettempdir()
        os.chdir(TEMPDIR)
    # WARNING: Decompyle incomplete


    def send_response(self, update, context):
Unsupported opcode: JUMP_BACKWARD
        user_message = update.message.text
        if update.message.chat['username'] != self.OWNER_USERNAME:
            context.bot.send_message(chat_id = self.CHAT_ID, text = '[!] ' + update.message.chat['username'] + ' tried to use this bot')
            context.bot.send_message(chat_id = update.message.chat.id, text = 'Only the owner can send commands to the computer,\nI have reported your activity to the owner!')
            return None
        user_message = None.encode('ascii', 'ignore').decode('ascii').strip(' ')
        user_message = user_message[0].lower() + user_message[1:]
        response = self.handle_message(update, user_message)
    # WARNING: Decompyle incomplete


    def start_bot(self):
        updater = Updater(self.TOKEN, use_context = True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler('start', self.start_command))
        dp.add_handler(MessageHandler(Filters.text, self.send_response))
        dp.add_error_handler(self.error)
        dp.add_handler(CallbackQueryHandler(self.handle_callback))
        updater.start_polling()
        print('[+] BOT has started')
        updater.idle()


bot = TelegramBot()
bot.start_bot()