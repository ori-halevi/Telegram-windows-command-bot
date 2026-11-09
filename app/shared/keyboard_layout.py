"""Make pyautogui's key names layout-independent on Windows.

pyautogui builds its char → virtual-key table once, at import, with
VkKeyScanA under the *active* keyboard layout. If that layout is Hebrew (or
any non-Latin one), letters like 'f' have no mapping, are stored as -1, and
pressing them sends garbage (-1 decodes to Alt+Ctrl+Shift+VK 0xFF). So
`ctrl+f`, `k ctrl+c`, builder letters etc. silently do nothing.

Virtual-key codes for letters/digits are fixed (VK 'A'..'Z' = 0x41..0x5A),
and the OEM punctuation keys are fixed physical positions, so we pin the
table to US-QWERTY codes: a key name always means that physical US key,
whatever language is active.
"""
from __future__ import annotations

import string
import sys

_SHIFT = 0x100  # pyautogui encodes "needs Shift" as + 0x100

_US_OEM = {
    "-": 0xBD, "=": 0xBB, "[": 0xDB, "]": 0xDD, "\\": 0xDC,
    ";": 0xBA, "'": 0xDE, ",": 0xBC, ".": 0xBE, "/": 0xBF, "`": 0xC0,
}
_US_OEM_SHIFTED = {
    "_": "-", "+": "=", "{": "[", "}": "]", "|": "\\",
    ":": ";", '"': "'", "<": ",", ">": ".", "?": "/", "~": "`",
}
_US_DIGITS_SHIFTED = dict(zip("!@#$%^&*()", "1234567890"))


def us_vk_table() -> dict[str, int]:
    table: dict[str, int] = {}
    for c in string.ascii_lowercase:
        table[c] = ord(c.upper())
        table[c.upper()] = ord(c.upper()) + _SHIFT
    for d in string.digits:
        table[d] = ord(d)
    table.update(_US_OEM)
    for shifted, base in _US_OEM_SHIFTED.items():
        table[shifted] = _US_OEM[base] + _SHIFT
    for shifted, digit in _US_DIGITS_SHIFTED.items():
        table[shifted] = ord(digit) + _SHIFT
    return table


def pin_pyautogui_to_us_layout() -> None:
    if sys.platform != "win32":
        return
    from pyautogui import _pyautogui_win

    _pyautogui_win.keyboardMapping.update(us_vk_table())
