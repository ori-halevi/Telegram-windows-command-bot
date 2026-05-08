"""Async handlers for python-telegram-bot v21."""
from __future__ import annotations

import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes

from telegram import InputMediaPhoto

from . import routing, security, state, ui
from .config import CONFIG
from .features import (
    audio,
    brightness,
    clipboard,
    files,
    keys,
    media,
    network,
    screen,
    system_power,
    webcam,
    window_switcher,
)

log = logging.getLogger(__name__)

GITHUB_URL = "https://github.com/ori-halevi/Telegram-windows-command-bot"

INTRUDER_MESSAGE = (
    "🚨 Only the owner can use this bot. Your activity has been logged.\n\n"
    "🚨 केवल मालिक ही इस बॉट का उपयोग कर सकता है। आपकी गतिविधि दर्ज की गई है।\n\n"
    "🚨 Только владелец может использовать этого бота. Ваша активность зарегистрирована.\n\n"
    "🚨 Solo el propietario puede usar este bot. Tu actividad ha sido registrada.\n\n"
    "🚨 仅所有者可以使用此机器人。您的活动已被记录。\n\n"
    "🚨 يمكن للمالك فقط استخدام هذا الروبوت. تم تسجيل نشاطك.\n\n"
    "🚨 Seul le propriétaire peut utiliser ce bot. Votre activité a été enregistrée.\n\n"
    "🚨 Nur der Besitzer darf diesen Bot benutzen. Deine Aktivität wurde protokolliert.\n\n"
    "🚨 Apenas o proprietário pode usar este bot. Sua atividade foi registrada.\n\n"
    "🚨 このボットはオーナーのみ使用できます。あなたの活動は記録されました。\n\n"
    "🚨 Bu botu yalnızca sahibi kullanabilir. Etkinliğiniz kaydedildi.\n\n"
    "🚨 רק הבעלים יכול להשתמש בבוט הזה. הפעילות שלך תועדה.\n\n"
    "ℹ️ This bot is open-source. You can download it and run your own:\n"
    f"{GITHUB_URL}"
)

WELCOME_MESSAGE = (
    "Welcome to your Windows command bot v2 🎛\n"
    "Tap a button or send /help for the full command list.\n\n"
    "ℹ️ Open source — fork it on GitHub:\n"
    f"{GITHUB_URL}"
)

ABOUT_MESSAGE = (
    "🤖 *Telegram Windows Command Bot v2*\n\n"
    "A Telegram bot that controls a Windows PC remotely:\n"
    "• arbitrary keyboard combos (free-text or interactive builder)\n"
    "• system info, power, audio, brightness, mouse, windows, processes\n"
    "• screenshots, screen recording, webcam\n"
    "• Wi-Fi, Bluetooth, hotspot toggling\n"
    "• VLC + Netflix media controls\n"
    "• shell / PowerShell execution\n\n"
    "🌐 *Source code & setup instructions:*\n"
    f"{GITHUB_URL}\n\n"
    "Anyone can clone it and adapt it to their own machine."
)


async def _to_thread(fn, *a, **kw):
    """Run blocking calls off the event loop."""
    return await asyncio.to_thread(fn, *a, **kw)


# ---------- Auth helpers ----------

def _is_owner_msg(update: Update) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return False
    return security.is_owner(user.username, chat.id)


async def _alert_intruder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    msg = update.effective_message
    info = security.make_intruder_dict(chat)
    info["attempt"] = (msg.text if msg else "") or ""
    await _to_thread(security.save_intruder_info, info)

    alert = (
        "🚨 Intrusion attempt\n"
        f"username: @{chat.username}\n"
        f"name: {chat.first_name} {chat.last_name or ''}\n"
        f"id: {chat.id}\n"
        f"text: {info['attempt']}"
    )
    try:
        await context.bot.send_message(CONFIG.owner_chat_id, alert)
        if not chat.username and msg:
            await context.bot.forward_message(
                CONFIG.owner_chat_id, from_chat_id=chat.id, message_id=msg.message_id
            )
    except Exception:
        log.exception("alert send failed")

    try:
        await context.bot.send_message(chat.id, INTRUDER_MESSAGE, disable_web_page_preview=True)
    except Exception:
        pass


# ---------- /start, /help ----------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_owner_msg(update):
        await _alert_intruder(update, context)
        return
    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=ui.main_menu(),
        disable_web_page_preview=True,
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_owner_msg(update):
        await _alert_intruder(update, context)
        return
    await update.message.reply_text(routing._help_text(), parse_mode="Markdown")


async def cmd_release_keys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Safety net: release any stuck modifier keys (Alt, Ctrl, Shift, Win)."""
    if not _is_owner_msg(update):
        await _alert_intruder(update, context)
        return
    msg = await _to_thread(window_switcher.force_release)
    await update.message.reply_text(msg)


async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Public — anyone can read this; it's just bot info + GitHub link."""
    await update.message.reply_text(
        ABOUT_MESSAGE, parse_mode="Markdown", disable_web_page_preview=False
    )


# ---------- Generic text ----------

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_owner_msg(update):
        await _alert_intruder(update, context)
        return

    chat_id = update.effective_chat.id
    if security.rate_limited(chat_id):
        await update.message.reply_text("⏱ Slow down — rate limit hit.")
        return

    text = (update.message.text or "").strip()
    if not text:
        return

    # Special: download <path> (uploads file)
    if text.lower().startswith("download "):
        path = text[len("download "):].strip().strip('"')
        await _send_file(update, context, path)
        return

    # Special: screenshot/record/webcam are heavy — handle here
    low = text.lower()
    if low in ("📸 screenshot", "screenshot"):
        await _send_screenshot(update, context)
        return
    if low.startswith("🎥 record screen") or low.startswith("record"):
        secs_str = text.split(maxsplit=1)
        try:
            secs = int(secs_str[1]) if len(secs_str) > 1 else CONFIG.screen_record_default_seconds
        except ValueError:
            secs = CONFIG.screen_record_default_seconds
        await _send_recording(update, context, secs)
        return
    if low in ("📷 webcam", "webcam"):
        await _send_webcam(update, context)
        return
    if low in ("🔀 switcher", "switcher"):
        await _start_switcher_message(update, context)
        return

    # Default routing
    result = await _to_thread(routing.route_text, text, chat_id)
    if result is None:
        await update.message.reply_text(
            "🤔 Unknown — send /help.",
            reply_markup=ui.main_menu(),
        )
        return
    if result.text:
        await _send_long(update.message, result.text, result.reply_markup, result.parse_mode)


async def _send_long(message, text: str, reply_markup=None, parse_mode=None) -> None:
    """Send `text` in 4096-char chunks."""
    LIMIT = 4000
    if len(text) <= LIMIT:
        try:
            await message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception:
            await message.reply_text(text, reply_markup=reply_markup)
        return
    chunks = [text[i:i+LIMIT] for i in range(0, len(text), LIMIT)]
    for i, chunk in enumerate(chunks):
        rm = reply_markup if i == len(chunks) - 1 else None
        try:
            await message.reply_text(chunk, reply_markup=rm, parse_mode=parse_mode)
        except Exception:
            await message.reply_text(chunk, reply_markup=rm)


# ---------- Heavy helpers ----------

async def _send_file(update: Update, context: ContextTypes.DEFAULT_TYPE, path: str) -> None:
    from pathlib import Path
    p = Path(path)
    if not p.exists() or not p.is_file():
        await update.message.reply_text(f"❌ File not found: {p}")
        return
    if p.stat().st_size > 50 * 1024 * 1024:
        await update.message.reply_text("❌ File >50MB (Telegram bot limit)")
        return
    try:
        with open(p, "rb") as f:
            await context.bot.send_document(update.effective_chat.id, document=f, filename=p.name)
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def _send_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("📸 Capturing…")
    try:
        path = await _to_thread(screen.take_screenshot)
        with open(path, "rb") as f:
            await context.bot.send_document(update.effective_chat.id, document=f, filename=path.name)
    except Exception as e:
        log.exception("screenshot")
        await update.message.reply_text(f"❌ {e}")


async def _send_recording(update: Update, context: ContextTypes.DEFAULT_TYPE, seconds: int) -> None:
    await update.message.reply_text(f"🎥 Recording {seconds}s…")
    try:
        path = await _to_thread(screen.record_screen, seconds)
        with open(path, "rb") as f:
            await context.bot.send_video(update.effective_chat.id, video=f, filename=path.name, supports_streaming=True)
    except Exception as e:
        log.exception("recording")
        await update.message.reply_text(f"❌ {e}")


async def _start_switcher_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Initial 🔀 Switcher entry point — start switcher, send live photo + keyboard."""
    await update.message.reply_text("🔀 Starting switcher (holding Alt)…")
    try:
        path = await _to_thread(window_switcher.start)
    except Exception as e:
        log.exception("switcher start")
        await update.message.reply_text(f"❌ {e}")
        return
    try:
        with open(path, "rb") as f:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=f,
                caption=ui.switcher_caption(active=True, position_hint="started — Tab+1"),
                parse_mode="Markdown",
                reply_markup=ui.switcher_menu(active=True),
            )
    except Exception as e:
        log.exception("switcher photo")
        # If photo send fails, make sure Alt isn't stuck
        await _to_thread(window_switcher.force_release)
        await update.message.reply_text(f"❌ {e}")


async def _switcher_update_photo(update: Update, path, hint: str) -> None:
    """Edit the inline switcher photo with a fresh screenshot + keyboard."""
    q = update.callback_query
    try:
        with open(path, "rb") as f:
            await q.edit_message_media(
                media=InputMediaPhoto(
                    media=f,
                    caption=ui.switcher_caption(active=True, position_hint=hint),
                    parse_mode="Markdown",
                ),
                reply_markup=ui.switcher_menu(active=True),
            )
    except Exception:
        log.exception("switcher edit_message_media")


async def _send_webcam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("📷 Snapping…")
    try:
        path = await _to_thread(webcam.snapshot)
        if path is None:
            await update.message.reply_text("❌ No webcam available")
            return
        with open(path, "rb") as f:
            await context.bot.send_photo(update.effective_chat.id, photo=f)
    except Exception as e:
        log.exception("webcam")
        await update.message.reply_text(f"❌ {e}")


# ---------- Inline callback router ----------

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if not q:
        return
    if not _is_owner_msg(update):
        await q.answer("⛔ Not authorized", show_alert=True)
        return

    data = q.data or ""
    try:
        result = await _route_callback(data, update, context)
    except Exception as e:
        log.exception("callback %r failed", data)
        result = f"❌ {e}"

    try:
        await q.answer(result[:200] if isinstance(result, str) and result else None)
    except Exception:
        pass


async def _route_callback(data: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat_id = update.effective_chat.id
    parts = data.split(":")
    ns = parts[0]

    # Keyboard builder
    if ns == "kb":
        sub = parts[1] if len(parts) > 1 else ""
        if sub == "mod" and len(parts) > 2:
            await _to_thread(state.toggle_modifier, chat_id, parts[2])
            await _refresh_builder(update, chat_id)
            return f"toggled {parts[2]}"
        if sub == "key" and len(parts) > 2:
            key = ":".join(parts[2:])  # in case key contained ':'
            msg = await _to_thread(keys.builder_press_key, chat_id, key)
            await _refresh_builder(update, chat_id)
            return msg
        if sub == "reset":
            await _to_thread(state.clear_modifiers, chat_id)
            await _refresh_builder(update, chat_id)
            return "cleared"
        if sub == "refresh":
            await _refresh_builder(update, chat_id)
            return "refreshed"
        if sub == "special" and len(parts) > 2 and parts[2] == "lang":
            # Win+Space toggles keyboard layout. Bypass modifier pills.
            return await _to_thread(keys.send_combo, "win+space")
        if sub == "fire":
            msg = await _to_thread(keys.builder_fire_modifiers, chat_id)
            await _refresh_builder(update, chat_id)
            return msg
        return "?"

    # Window switcher
    if ns == "sw":
        sub = parts[1]
        if sub == "start":
            path = await _to_thread(window_switcher.start)
            await _switcher_update_photo(update, path, "started — Tab+1")
            return "started"
        if sub == "fwd":
            n = int(parts[2])
            path = await _to_thread(window_switcher.tab_forward, n)
            await _switcher_update_photo(update, path, f"+{n} tab(s)")
            return f"tab+{n}"
        if sub == "back":
            n = int(parts[2])
            path = await _to_thread(window_switcher.tab_backward, n)
            if path is None:
                return "switcher not active"
            await _switcher_update_photo(update, path, f"-{n} tab(s)")
            return f"tab-{n}"
        if sub == "commit":
            msg = await _to_thread(window_switcher.commit)
            try:
                await update.callback_query.edit_message_caption(
                    caption=msg, reply_markup=ui.switcher_menu(active=False)
                )
            except Exception:
                pass
            return msg
        if sub == "cancel":
            msg = await _to_thread(window_switcher.cancel)
            try:
                await update.callback_query.edit_message_caption(
                    caption=msg, reply_markup=ui.switcher_menu(active=False)
                )
            except Exception:
                pass
            return msg
        if sub == "release":
            msg = await _to_thread(window_switcher.force_release)
            try:
                await update.callback_query.edit_message_caption(
                    caption=msg, reply_markup=ui.switcher_menu(active=False)
                )
            except Exception:
                pass
            return msg

    # VLC / Netflix
    if ns == "vlc":
        return await _to_thread(media.handle_vlc, parts[1])
    if ns == "nfx":
        return await _to_thread(media.handle_netflix, parts[1])

    # Power
    if ns == "power":
        sub = parts[1]
        return await _to_thread({
            "lock": system_power.lock_screen,
            "sleep": system_power.sleep_pc,
            "hibernate": system_power.hibernate_pc,
            "dark": system_power.go_dark,
            "restart": system_power.restart_pc,
            "shutdown": system_power.shutdown_pc,
            "abort": system_power.abort_shutdown,
            "status": system_power.screen_status,
        }[sub])

    # Volume
    if ns == "vol":
        sub = parts[1]
        if sub == "get":
            return await _to_thread(audio.get_volume)
        if sub == "mute_on":
            return await _to_thread(audio.mute, True)
        if sub == "mute_off":
            return await _to_thread(audio.mute, False)
        if sub == "set":
            return await _to_thread(audio.set_volume, int(parts[2]))
        if sub == "step":
            return await _to_thread(audio.step_volume, int(parts[2]))

    # Brightness
    if ns == "bright":
        sub = parts[1]
        if sub == "get":
            return await _to_thread(brightness.get_brightness)
        if sub == "set":
            return await _to_thread(brightness.set_brightness, int(parts[2]))
        if sub == "step":
            return await _to_thread(brightness.step_brightness, int(parts[2]))

    # Network
    if ns == "net":
        if parts[1] == "hotspot" and parts[2] == "toggle":
            return await _to_thread(network.toggle_hotspot)
        if parts[1] == "hotspot" and parts[2] == "status":
            return await _to_thread(network.hotspot_status)
        if parts[1] == "bt" and parts[2] == "toggle":
            return await _to_thread(network.toggle_bluetooth)
        if parts[1] == "wifi" and parts[2] == "list":
            await update.effective_chat.send_message(network.list_wifi(), parse_mode="Markdown")
            return "ok"
        if parts[1] == "wifi" and parts[2] == "current":
            await update.effective_chat.send_message(network.wifi_current(), parse_mode="Markdown")
            return "ok"
        if parts[1] == "ip" and parts[2] == "local":
            return network.local_ip()
        if parts[1] == "ip" and parts[2] == "public":
            return await _to_thread(network.public_ip)

    return "?"


async def _refresh_builder(update: Update, chat_id: int) -> None:
    q = update.callback_query
    try:
        await q.edit_message_text(
            ui.builder_caption(chat_id),
            reply_markup=ui.builder_menu(chat_id),
            parse_mode="Markdown",
        )
    except Exception:
        # message may already match — ignore
        pass


# ---------- Error handler ----------

async def on_error(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.error("Telegram error: %s", context.error)
