"""Outbound Telegram messages sent by the backend (SOS broadcast, donor confirmations, vouchers).

Uses the plain Bot API over HTTPS so the API process doesn't need the bot's event loop.
If TELEGRAM_BOT_TOKEN is not set, messages are logged and skipped.
"""

import html
import logging
import os
import threading

import requests

from i18n import t

log = logging.getLogger("bloodlink.notifier")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
_bot_username: str | None = os.getenv("TELEGRAM_BOT_USERNAME", "").strip().lstrip("@") or None


def enabled() -> bool:
    return bool(TOKEN)


def bot_username() -> str:
    """Bot username for deep links; asks Telegram once if not configured."""
    global _bot_username
    if _bot_username:
        return _bot_username
    if TOKEN:
        try:
            r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe", timeout=5)
            _bot_username = r.json()["result"]["username"]
            return _bot_username
        except Exception as exc:  # noqa: BLE001
            log.warning("getMe failed: %s", exc)
    return "BloodLinkBot"


def esc(value) -> str:
    return html.escape(str(value or ""))


def send_message(chat_id: str, text: str, buttons: list[list[dict]] | None = None) -> bool:
    if not TOKEN:
        log.info("[telegram disabled] to %s: %s", chat_id, text.replace("\n", " | "))
        return False
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    try:
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload, timeout=10)
        if not r.ok:
            log.warning("sendMessage to %s failed: %s", chat_id, r.text)
        return r.ok
    except requests.RequestException as exc:
        log.warning("sendMessage to %s failed: %s", chat_id, exc)
        return False


def sos_text(request: dict, lang: str | None, km: float | None = None) -> str:
    """The SOS alert in one donor's language (Telegram HTML; push strips the tags)."""
    lang = lang or "en"
    uicon = {"Critical": "🔴", "High": "🟠", "Normal": "🟡"}.get(request["urgency"], "🟠")
    text = t(lang, "sos_alert", group=esc(request["blood_group"]), hospital=esc(request["hospital"]),
             city=esc(request["city"]), units=request["units_needed"], uicon=uicon,
             urgency=t(lang, f"urg_{request['urgency']}"), name=esc(request["requester_name"]))
    return text + ("\n" + t(lang, "dist", km=km) if km is not None else "")


def broadcast_sos(request: dict, donors: list[dict]) -> int:
    """Send the SOS alert, in each donor's language, with a one-tap donate button. Returns number delivered."""
    sent = 0
    for d in donors:
        lang = d.get("language") or "en"
        text = sos_text(request, lang, d.get("km"))
        buttons = [[{"text": t(lang, "donate_btn"), "callback_data": f"donate_{request['id']}"}]]
        sent += bool(send_message(d["telegram_id"], text, buttons))
    return sent


def tell_text(user, text: str, url: str = "/", buttons: list[list[dict]] | None = None) -> None:
    """Send a message to a person on every channel they use: Telegram (with buttons) and browser push."""
    import push

    if user.telegram_id:
        (notify_buttons(user.telegram_id, text, buttons) if buttons else notify(user.telegram_id, text))
    push.to_user(user.id, text, url)


def tell(user, key: str, url: str = "/", buttons: list[list[dict]] | None = None, **kwargs) -> None:
    """Localized tell_text in the person's own language."""
    tell_text(user, t(user.language, key, **kwargs), url, buttons)


def notify_t(chat_id: str | None, lang: str | None, key: str, **kwargs) -> None:
    """Localized fire-and-forget notification."""
    if chat_id:
        notify(chat_id, t(lang, key, **kwargs))


def notify_buttons(chat_id: str | None, text: str, buttons: list[list[dict]]) -> None:
    """Fire-and-forget message with an inline keyboard."""
    if chat_id:
        threading.Thread(target=send_message, args=(chat_id, text, buttons), daemon=True).start()


def notify(chat_id: str | None, text: str) -> None:
    """Fire-and-forget message so API responses never wait on Telegram."""
    if chat_id:
        threading.Thread(target=send_message, args=(chat_id, text), daemon=True).start()
