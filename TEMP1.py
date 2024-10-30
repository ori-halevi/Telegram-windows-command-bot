import ctypes
import time

# Load user32.dll
user32 = ctypes.windll.user32

# Get the handle to the taskbar
taskbar_handle = user32.FindWindowW("Shell_TrayWnd", None)

# Define constants
WM_SETTINGCHANGE = 0x001A

def refresh_taskbar():
    # Send the setting change message directly to the taskbar
    user32.SendMessageW(taskbar_handle, WM_SETTINGCHANGE, 0, "ImmersiveColorSet")

# Run the function every 2 seconds
while True:
    refresh_taskbar()
    time.sleep(2)  # Sleep for 2 seconds
