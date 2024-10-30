import ctypes
import logging
import pyautogui

# Load Windows API libraries
advapi32 = ctypes.WinDLL('advapi32')  # Windows API for registry functions
kernel32 = ctypes.WinDLL('kernel32')  # Core Windows API
user32 = ctypes.WinDLL('user32')  # Windows API for user interactions

# Function to get the current keyboard layout
GetKeyboardLayout = user32.GetKeyboardLayout
GetKeyboardLayout.argtypes = [ctypes.c_ulong]
GetKeyboardLayout.restype = ctypes.c_ulong

# Function to get the handle of the foreground window
GetForegroundWindow = user32.GetForegroundWindow
GetForegroundWindow.restype = ctypes.c_void_p

def get_current_language() -> str | None:
    """
    Returns the current keyboard layout language of the foreground window.

    Returns:
        str | None: The current keyboard layout language as a string, or None if it cannot be retrieved.
    """
    hwnd = GetForegroundWindow()
    layout = GetKeyboardLayout(ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None))
    language_id = layout & 0xFFFF  # Extract the low-order word (language ID)

    buffer = ctypes.create_unicode_buffer(100)
    if ctypes.windll.kernel32.GetLocaleInfoW(language_id, 0x00000002, buffer, len(buffer)):
        return buffer.value
    else:
        logging.error("Could not retrieve the current keyboard layout language.")
        return None

def set_keyboard_layout_language(language: str = "english", rounds: int = 5) -> bool:
    """
    Sets the keyboard layout language to the given language.
    :param language: The wanted keyboard layout language, default is "english".
    :param rounds: The number of time the function will try to set the keyboard layout language to English. Default is 5
    :return: True if the function was successful, False otherwise
    """
    for r in range(rounds):
        if language.lower() in get_current_language().lower():
            return True
        pyautogui.hotkey('win', 'space')
    logging.warning("Some problem occurred while setting english language.")
    return False

if __name__ == "__main__":
    print(set_keyboard_layout_language())