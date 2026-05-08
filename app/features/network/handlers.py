"""Network handlers."""
from __future__ import annotations

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from ...core import menu
from ...core.types import TextResult
from ...shared.telegram_utils import to_thread
from . import service, ui


def match_text(text: str, chat_id: int) -> TextResult | None:
    low = text.strip().lower()
    if low == menu.HOTSPOT.lower():
        return TextResult(text="📡 Hotspot:", reply_markup=ui.hotspot_menu())
    if low == menu.BLUETOOTH.lower():
        return TextResult(text="🎧 Bluetooth:", reply_markup=ui.bluetooth_menu())
    if low == menu.WIFI.lower():
        return TextResult(text="📶 Wi-Fi:", reply_markup=ui.wifi_menu())

    parts = text.strip().split(maxsplit=1)
    verb = parts[0].lower().lstrip("/") if parts else ""

    if verb == "wifi":
        return TextResult(text=service.list_wifi(), parse_mode="Markdown")
    if verb == "ip":
        return TextResult(text=service.local_ip() + "\n" + service.public_ip())
    return None


async def _on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if q is None:
        return
    parts = (q.data or "").split(":")
    msg = "?"
    try:
        if parts[1] == "hotspot" and parts[2] == "toggle":
            msg = await to_thread(service.toggle_hotspot)
        elif parts[1] == "hotspot" and parts[2] == "status":
            msg = await to_thread(service.hotspot_status)
        elif parts[1] == "bt" and parts[2] == "toggle":
            msg = await to_thread(service.toggle_bluetooth)
        elif parts[1] == "wifi" and parts[2] == "list":
            await q.message.reply_text(service.list_wifi(), parse_mode="Markdown")
            msg = "ok"
        elif parts[1] == "wifi" and parts[2] == "current":
            await q.message.reply_text(service.wifi_current(), parse_mode="Markdown")
            msg = "ok"
        elif parts[1] == "ip" and parts[2] == "local":
            msg = service.local_ip()
        elif parts[1] == "ip" and parts[2] == "public":
            msg = await to_thread(service.public_ip)
    except Exception as e:
        msg = f"❌ {e}"
    try:
        await q.answer(msg[:200])
    except Exception:
        pass


def register(app: Application) -> None:
    app.add_handler(CallbackQueryHandler(_on_callback, pattern=r"^net:"))
