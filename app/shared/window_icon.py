"""Set the bot's icon on the console window when running as a script.

PyInstaller embeds the icon into the .exe at build time; that path doesn't
help when launching directly via `python main.py`. This module attaches the
icon to the current console window via the Win32 API, so the taskbar and
Alt-Tab card show the bot's icon instead of Python's.
"""
from __future__ import annotations

import ctypes
import logging
import sys
from pathlib import Path

log = logging.getLogger(__name__)


def set_console_title(title: str) -> None:
    """Best-effort: set the console window's title."""
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    except Exception:
        pass


def set_console_icon(icon_path: Path,
                     title: str = "Telegram Windows Command Bot") -> bool:
    """Attach `icon_path` (.ico) and `title` to the current console window.

    Returns True on success, False otherwise. Never raises.
    """
    set_console_title(title)
    if sys.platform != "win32":
        return False
    if not icon_path.exists():
        log.warning("icon not found: %s", icon_path)
        return False
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        user32 = ctypes.WinDLL("user32", use_last_error=True)

        IMAGE_ICON = 1
        LR_LOADFROMFILE = 0x10
        LR_DEFAULTSIZE = 0x40
        WM_SETICON = 0x80
        ICON_SMALL = 0
        ICON_BIG = 1

        kernel32.GetConsoleWindow.restype = ctypes.c_void_p
        user32.LoadImageW.restype = ctypes.c_void_p
        user32.LoadImageW.argtypes = [
            ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint,
            ctypes.c_int, ctypes.c_int, ctypes.c_uint,
        ]
        user32.SendMessageW.restype = ctypes.c_void_p
        user32.SendMessageW.argtypes = [
            ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p,
        ]

        hwnd = kernel32.GetConsoleWindow()
        if not hwnd:
            return False  # no console (e.g. pythonw.exe)

        hicon = user32.LoadImageW(
            None, str(icon_path), IMAGE_ICON, 0, 0,
            LR_LOADFROMFILE | LR_DEFAULTSIZE,
        )
        if not hicon:
            return False

        user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon)
        user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon)

        # Also set the AppUserModelID so Windows treats the bot as its own
        # app (separate taskbar group, distinct from generic python.exe).
        try:
            shell32 = ctypes.WinDLL("shell32", use_last_error=True)
            shell32.SetCurrentProcessExplicitAppUserModelID(
                ctypes.c_wchar_p("ori-halevi.TelegramWindowsCommandBot")
            )
        except Exception:
            pass

        return True
    except Exception as e:
        log.warning("set_console_icon failed: %s", e)
        return False
