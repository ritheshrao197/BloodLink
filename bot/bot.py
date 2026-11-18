"""BLOODLINK Telegram bot — the zero-friction interface.

Everything is tap-driven: language picker, main menu buttons, blood group / state / district /
hospital / units / urgency buttons, one-tap name and Telegram's "share phone" button.
Typing is only needed for a name, city or hospital that isn't in the list.

Languages: English, Kannada, Hindi (see i18n.py). SOS alerts are broadcast by the backend in each
donor's language; the "🩸 I Can Donate" button on them is handled here.
"""

import html
import logging
import os
import re
import sys
import warnings
from pathlib import Path

import httpx
from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)
from telegram.warnings import PTBUserWarning

from i18n import CHOOSE_LANGUAGE, COMMANDS, LANGS, t

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:  # pragma: no cover
    pass

warnings.filterwarnings("ignore", category=PTBUserWarning)  # per_message notice for mixed conversations
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("bloodlink.bot")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
API_URL = os.getenv("BLOODLINK_API_URL", "http://localhost:8000/api").rstrip("/")
WEB_URL = os.getenv("BLOODLINK_WEB_URL", "http://localhost:5173").rstrip("/")

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
BADGE_ICON = {"Bronze": "🥉", "Silver": "🥈", "Gold": "🥇", "Platinum": "💎"}
URGENCIES = ["Critical", "High", "Normal"]
END = ConversationHandler.END

# conversation states (one conversation handles both flows so they never steal each other's input)
(REG_NAME, REG_GROUP, REG_STATE, REG_DISTRICT, REG_CITY, REG_PHONE,
 SOS_GROUP, SOS_STATE, SOS_DISTRICT, SOS_HOSPITAL, SOS_HOSP_TEXT, SOS_PLACE_TEXT,
 SOS_UNITS, SOS_URGENCY, SOS_PHONE) = range(15)


# ------------------------------------------------------------------ API + helpers
class ApiError(Exception):
    def __init__(self, message, data: dict | None = None):
        super().__init__(message)
        self.data = data or {}


async def api(method: str, path: str, **kwargs):
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.request(method, f"{API_URL}{path}", **kwargs)
    except httpx.HTTPError as exc:
        raise ApiError("server_down") from exc
    data = r.json() if r.content else {}
    if r.status_code >= 400:
        detail = data.get("detail", f"Error {r.status_code}") if isinstance(data, dict) else str(data)
        if isinstance(detail, list):
            detail = "; ".join(d.get("msg", str(d)) for d in detail)
        elif isinstance(detail, dict):
            raise ApiError(detail.get("message", str(detail)), detail)
        raise ApiError(detail)
    return data


def err_text(lang: str, e: ApiError) -> str:
    return t(lang, "server_down") if str(e) == "server_down" else f"⚠️ {esc(e)}"


_locations: list[dict] | None = None


async def locations() -> list[dict]:
    """State -> district -> hospital tree from the backend (cached; it is static)."""
    global _locations
    if _locations is None:
        _locations = (await api("GET", "/locations"))["states"]
    return _locations


async def current_user(update: Update):
    try:
        return await api("GET", f"/users/by-telegram/{update.effective_user.id}")
    except ApiError:
        return None


async def ensure_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    """Chosen language from this chat, else from the user's account; None if never chosen."""
    lang = context.user_data.get("lang")
    if lang:
        return lang
    user = await current_user(update)
    if user and user.get("language"):
        context.user_data["lang"] = user["language"]
        return user["language"]
    return None


def L(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "en")


def esc(v) -> str:
    return html.escape(str(v or ""))


def btn(text: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text, callback_data=data)


def chunk(items: list, n: int) -> list[list]:
    return [items[i:i + n] for i in range(0, len(items), n)]


def cancel_row(lang: str) -> list[InlineKeyboardButton]:
    return [btn(t(lang, "btn_cancel"), "x_cancel")]


async def ack(update: Update, text: str | None = None, alert: bool = False):
    if update.callback_query:
        try:
            await update.callback_query.answer(text, show_alert=alert)
        except BadRequest:
            pass


async def reply(update: Update, text: str, **kwargs):
    return await update.effective_message.reply_text(
        text, parse_mode=ParseMode.HTML, disable_web_page_preview=True, **kwargs)


async def show(update: Update, text: str, kb: InlineKeyboardMarkup | None = None):
    """Edit the tapped message in place (keeps the chat tidy); otherwise send a new one."""
    q = update.callback_query
    if q:
        try:
            await q.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=kb,
                                      disable_web_page_preview=True)
            return
        except BadRequest as e:
            if "not modified" in str(e).lower():
                return
    await reply(update, text, reply_markup=kb)


# ------------------------------------------------------------------ keyboards
def menu_kb(lang: str, user: dict | None) -> InlineKeyboardMarkup:
    rows = [[btn(t(lang, "btn_sos"), "m_sos")]]
    if not user:
        rows.append([btn(t(lang, "btn_register"), "m_register")])
    rows += [
        [btn(t(lang, "btn_requests"), "m_requests"), btn(t(lang, "btn_me"), "m_me")],
        [btn(t(lang, "btn_rewards"), "m_rewards"), btn(t(lang, "btn_leaderboard"), "m_leaderboard")],
        [btn(t(lang, "btn_achievements"), "m_achievements"), btn(t(lang, "btn_invite"), "m_invite")],
        [btn(t(lang, "btn_camps"), "m_camps"), btn(t(lang, "btn_teams"), "m_teams")],
        [btn(t(lang, "btn_language"), "m_language")],
    ]
    if user:
        rows.append([btn(t(lang, "btn_busy"), "m_busy") if user["is_available"]
                     else btn(t(lang, "btn_available"), "m_available")])
    return InlineKeyboardMarkup(rows)


def group_kb(lang: str, prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([*chunk([btn(bg, f"{prefix}{bg}") for bg in BLOOD_GROUPS], 4), cancel_row(lang)])


def state_kb(lang: str, prefix: str, locs: list[dict], saved: tuple[str, str] | None = None) -> InlineKeyboardMarkup:
    rows = []
    if saved:
        rows.append([btn(f"📍 {saved[1]}, {saved[0]}", f"{prefix}s_saved")])
    rows += chunk([btn(s["name"], f"{prefix}s_{i}") for i, s in enumerate(locs)], 2)
    rows.append([btn(t(lang, "btn_other"), f"{prefix}s_other")])
    rows.append(cancel_row(lang))
    return InlineKeyboardMarkup(rows)


def district_kb(lang: str, prefix: str, state: dict) -> InlineKeyboardMarkup:
    rows = chunk([btn(d["name"], f"{prefix}d_{j}") for j, d in enumerate(state["districts"])], 3)
    rows.append([btn(t(lang, "btn_back"), f"{prefix}d_back"), *cancel_row(lang)])
    return InlineKeyboardMarkup(rows)


def hospital_kb(lang: str, hospitals: list[str]) -> InlineKeyboardMarkup:
    rows = [[btn(f"🏥 {h}", f"sh_{k}")] for k, h in enumerate(hospitals)]
    rows.append([btn(t(lang, "btn_other"), "sh_other")])
    rows.append([btn(t(lang, "btn_back"), "sh_back"), *cancel_row(lang)])
    return InlineKeyboardMarkup(rows)


def phone_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton(t(lang, "btn_share_phone"), request_contact=True)], [KeyboardButton(t(lang, "btn_skip"))]],
        resize_keyboard=True, one_time_keyboard=True)


def extract_phone(update: Update) -> str | None:
    msg = update.effective_message
    if msg.contact:
        return msg.contact.phone_number
    text = (msg.text or "").strip()
    return text if len(re.sub(r"\D", "", text)) >= 7 else None  # anything else (e.g. "Skip") = no phone


def find_location(locs: list[dict], state: str | None, district: str | None) -> tuple[int, int] | None:
    for i, s in enumerate(locs):
        if s["name"] == state:
            for j, d in enumerate(s["districts"]):
                if d["name"] == district:
                    return i, j
    return None


# ------------------------------------------------------------------ texts
def profile_text(lang: str, u: dict) -> str:
    info = u["badge_info"]
    nxt = info.get("next")
    progress = ("\n➡️ " + t(lang, "lbl_to_next", n=nxt["min_points"] - u["points"],
                             badge=f"{nxt['icon']} {nxt['name']}")) if nxt else ""
    extra = " · 🗣️" if "Influencer" in u.get("extra_badges", []) else ""
    place = ", ".join(x for x in (u.get("city"), u.get("state")) if x)
    return (
        f"{info['icon']} <b>{esc(u['name'])}</b> — {info['title']}{extra}\n"
        f"🩸 {u['blood_group']} · 📍 {esc(place)}\n"
        f"⭐ <b>{u['points']} BLP</b> · {u['badge']}{progress}\n"
        f"💉 {t(lang, 'lbl_donations')}: {u['total_donations']}\n"
        f"🤝 {t(lang, 'lbl_referrals')}: {u['referrals']['total']} "
        f"({t(lang, 'lbl_donated')}: {u['referrals']['donated']})\n"
        f"{t(lang, 'lbl_available') if u['is_available'] else t(lang, 'lbl_unavailable')}\n"
        f"🔑 {t(lang, 'lbl_code')}: <code>{u['referral_code']}</code>"
    )


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, header: str | None = None):
    lang = L(context)
    user = await current_user(update)
    text = (header + "\n\n" if header else "") + t(lang, "menu_prompt")
    await reply(update, text, reply_markup=menu_kb(lang, user))


# ------------------------------------------------------------------ language + start
async def ask_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    kb = InlineKeyboardMarkup([[btn(name, f"lang_{code}") for code, name in LANGS.items()]])
    await reply(update, CHOOSE_LANGUAGE, reply_markup=kb)


async def language_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.callback_query.data.removeprefix("lang_")
    if code not in LANGS:
        code = "en"
    await ack(update)
    context.user_data["lang"] = code
    try:
        await api("PATCH", f"/users/by-telegram/{update.effective_user.id}/language", json={"language": code})
    except ApiError:
        pass  # not registered yet: the choice is sent along at registration
    await show(update, t(code, "lang_set"))
    if "pending_start" in context.user_data:
        await do_start(update, context, context.user_data.pop("pending_start"))
    else:
        await show_menu(update, context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arg = context.args[0] if context.args else None
    if not await ensure_lang(update, context):
        context.user_data["pending_start"] = arg  # continue after the language is picked
        await ask_language(update, context)
        return
    await do_start(update, context, arg)


async def do_start(update: Update, context: ContextTypes.DEFAULT_TYPE, arg: str | None):
    lang = L(context)
    tg = update.effective_user

    if arg and arg.startswith("link_"):  # deep link from the web dashboard
        try:
            res = await api("POST", "/users/link-telegram", json={
                "referral_code": arg[5:], "telegram_id": str(tg.id), "telegram_username": tg.username})
            await api("PATCH", f"/users/by-telegram/{tg.id}/language", json={"language": lang})
            await show_menu(update, context, t(lang, "linked", name=esc(res["user"]["name"])))
        except ApiError as e:
            await reply(update, err_text(lang, e))
        return

    user = await current_user(update)
    if arg and not user:
        context.user_data["ref"] = arg
        kb = InlineKeyboardMarkup([[btn(t(lang, "btn_register"), "m_register")]])
        await reply(update, t(lang, "invited", code=esc(arg)), reply_markup=kb)
        return
    header = t(lang, "welcome_back", name=esc(user["name"])) if user else t(lang, "welcome")
    await show_menu(update, context, header)


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start while inside a flow: drop the flow and start fresh."""
    context.user_data.pop("reg", None)
    context.user_data.pop("sos", None)
    await reply(update, "🔄", reply_markup=ReplyKeyboardRemove())
    await start(update, context)
    return END


async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ensure_lang(update, context)
    await show_menu(update, context)
    return END


async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """All main-menu buttons (m_*). Also a conversation fallback, so the menu always works."""
    action = update.callback_query.data.removeprefix("m_")
    await ensure_lang(update, context)
    if action == "sos":
        return await sos_start(update, context)
    if action == "register":
        return await reg_start(update, context)
    context.user_data.pop("reg", None)
    context.user_data.pop("sos", None)
    await ack(update)
    handler = {"requests": requests_cmd, "me": me, "invite": invite, "rewards": rewards,
               "leaderboard": leaderboard, "achievements": achievements_cmd, "camps": camps_cmd, "teams": teams_cmd,
               "language": ask_language, "available": available, "busy": busy}.get(action)
    if handler:
        await handler(update, context)
    return END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("reg", None)
    context.user_data.pop("sos", None)
    await ack(update)
    if update.callback_query:
        try:
            await update.callback_query.edit_message_reply_markup(None)
        except BadRequest:
            pass
    await reply(update, t(L(context), "cancelled"), reply_markup=ReplyKeyboardRemove())
    await show_menu(update, context)
    return END


# ------------------------------------------------------------------ registration flow
async def reg_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    lang = await ensure_lang(update, context) or "en"
    user = await current_user(update)
    if user:
        await reply(update, t(lang, "already_registered") + "\n\n" + profile_text(lang, user),
                    reply_markup=menu_kb(lang, user))
        return END
    context.user_data["reg"] = {}
    name = (update.effective_user.full_name or "").strip()[:40]
    rows = [[btn(t(lang, "btn_use_name", name=name), "rn_tg")]] if name else []
    rows.append(cancel_row(lang))
    await reply(update, t(lang, "reg_name"), reply_markup=InlineKeyboardMarkup(rows))
    return REG_NAME


async def _reg_ask_group(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str):
    context.user_data.setdefault("reg", {})["name"] = name[:80]
    await show(update, f"👤 <b>{esc(name)}</b>\n\n" + t(L(context), "reg_group"), group_kb(L(context), "rg_"))
    return REG_GROUP


async def reg_name_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _reg_ask_group(update, context, update.message.text.strip())


async def reg_name_tg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    return await _reg_ask_group(update, context, update.effective_user.full_name or "Donor")


async def reg_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    bg = update.callback_query.data.removeprefix("rg_")
    context.user_data.setdefault("reg", {})["blood_group"] = bg
    await show(update, f"🩸 <b>{bg}</b>\n\n" + t(L(context), "choose_state"), state_kb(L(context), "r", await locations()))
    return REG_STATE


async def reg_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    lang, data = L(context), update.callback_query.data.removeprefix("rs_")
    if data == "other":
        await show(update, t(lang, "type_city"), InlineKeyboardMarkup([cancel_row(lang)]))
        return REG_CITY
    locs = await locations()
    i = int(data)
    context.user_data["reg"]["state_i"] = i
    await show(update, t(lang, "choose_district", state=esc(locs[i]["name"])), district_kb(lang, "r", locs[i]))
    return REG_DISTRICT


async def reg_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    lang, data = L(context), update.callback_query.data.removeprefix("rd_")
    locs = await locations()
    if data == "back":
        await show(update, t(lang, "choose_state"), state_kb(lang, "r", locs))
        return REG_STATE
    state = locs[context.user_data["reg"]["state_i"]]
    district = state["districts"][int(data)]["name"]
    context.user_data["reg"].update(state=state["name"], city=district)
    await show(update, f"📍 <b>{esc(district)}, {esc(state['name'])}</b>")
    await reply(update, t(lang, "reg_phone"), reply_markup=phone_kb(lang))
    return REG_PHONE


async def reg_city_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["reg"].update(city=update.message.text.strip()[:80], state=None)
    await reply(update, t(L(context), "reg_phone"), reply_markup=phone_kb(L(context)))
    return REG_PHONE


async def reg_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    reg = context.user_data.pop("reg", {})
    tg = update.effective_user
    payload = {"name": reg.get("name"), "blood_group": reg.get("blood_group"), "city": reg.get("city"),
               "state": reg.get("state"), "phone": extract_phone(update), "language": lang,
               "telegram_id": str(tg.id), "telegram_username": tg.username,
               "referred_by": context.user_data.pop("ref", None)}
    try:
        try:
            res = await api("POST", "/register", json=payload)
        except ApiError as e:
            if "Referral code" not in str(e):
                raise
            payload["referred_by"] = None  # stale/invalid invite code: register without it
            res = await api("POST", "/register", json=payload)
    except ApiError as e:
        await reply(update, err_text(lang, e), reply_markup=ReplyKeyboardRemove())
        return END
    u = res["user"]
    await reply(update, t(lang, "reg_done", name=esc(u["name"]), points=u["points"],
                          bonus=t(lang, "bonus") if u.get("referred_by") else "", district=esc(u["city"])),
                reply_markup=ReplyKeyboardRemove())
    await reply(update, t(lang, "invite", link=u["referral_link"]), reply_markup=menu_kb(lang, u))
    return END


# ------------------------------------------------------------------ SOS flow
async def sos_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    lang = await ensure_lang(update, context) or "en"
    user = await current_user(update)
    context.user_data.pop("reg", None)
    context.user_data["sos"] = {"saved": (user["state"], user["city"]) if user and user.get("state") else None}
    await reply(update, t(lang, "sos_group"), reply_markup=group_kb(lang, "sg_"))
    return SOS_GROUP


async def sos_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    sos = context.user_data.setdefault("sos", {})
    sos["blood_group"] = update.callback_query.data.removeprefix("sg_")
    locs = await locations()
    saved = sos.get("saved")
    saved = tuple(saved) if saved and find_location(locs, *saved) else None
    await show(update, f"🩸 <b>{sos['blood_group']}</b>\n\n" + t(L(context), "sos_state"),
               state_kb(L(context), "s", locs, saved))
    return SOS_STATE


async def _sos_ask_hospital(update: Update, context: ContextTypes.DEFAULT_TYPE, i: int, j: int):
    locs = await locations()
    state, district = locs[i], locs[i]["districts"][j]
    sos = context.user_data["sos"]
    sos.update(state_i=i, district_j=j, state=state["name"], city=district["name"])
    await show(update, t(L(context), "sos_hospital", district=esc(district["name"])),
               hospital_kb(L(context), district["hospitals"]))
    return SOS_HOSPITAL


async def sos_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    lang, data = L(context), update.callback_query.data.removeprefix("ss_")
    sos = context.user_data["sos"]
    locs = await locations()
    if data == "saved":
        return await _sos_ask_hospital(update, context, *find_location(locs, *sos["saved"]))
    if data == "other":
        await show(update, t(lang, "type_hospital_city"), InlineKeyboardMarkup([cancel_row(lang)]))
        return SOS_PLACE_TEXT
    i = int(data)
    sos["state_i"] = i
    await show(update, t(lang, "choose_district", state=esc(locs[i]["name"])), district_kb(lang, "s", locs[i]))
    return SOS_DISTRICT


async def sos_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    data = update.callback_query.data.removeprefix("sd_")
    sos = context.user_data["sos"]
    if data == "back":
        locs = await locations()
        saved = tuple(sos["saved"]) if sos.get("saved") and find_location(locs, *sos["saved"]) else None
        await show(update, t(L(context), "sos_state"), state_kb(L(context), "s", locs, saved))
        return SOS_STATE
    return await _sos_ask_hospital(update, context, sos["state_i"], int(data))


async def sos_hospital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    lang, data = L(context), update.callback_query.data.removeprefix("sh_")
    sos = context.user_data["sos"]
    locs = await locations()
    if data == "back":
        state = locs[sos["state_i"]]
        await show(update, t(lang, "choose_district", state=esc(state["name"])), district_kb(lang, "s", state))
        return SOS_DISTRICT
    if data == "other":
        await show(update, t(lang, "type_hospital"), InlineKeyboardMarkup([cancel_row(lang)]))
        return SOS_HOSP_TEXT
    sos["hospital"] = locs[sos["state_i"]]["districts"][sos["district_j"]]["hospitals"][int(data)]
    return await _sos_ask_units(update, context)


async def sos_hospital_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sos"]["hospital"] = update.message.text.strip()[:120]
    return await _sos_ask_units(update, context)


async def sos_place_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    hospital, _, city = text.rpartition(",")
    if not hospital.strip() or not city.strip():
        await reply(update, t(L(context), "need_comma"))
        return SOS_PLACE_TEXT
    context.user_data["sos"].update(hospital=hospital.strip()[:120], city=city.strip()[:80], state=None)
    return await _sos_ask_units(update, context)


async def _sos_ask_units(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sos = context.user_data["sos"]
    summary = f"🩸 <b>{sos['blood_group']}</b> · 🏥 {esc(sos['hospital'])}, {esc(sos['city'])}\n\n"
    kb = InlineKeyboardMarkup([*chunk([btn(str(n), f"su_{n}") for n in (1, 2, 3, 4, 5, 6)], 3), cancel_row(L(context))])
    await show(update, summary + t(L(context), "sos_units"), kb)
    return SOS_UNITS


async def sos_units(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    lang = L(context)
    sos = context.user_data["sos"]
    sos["units_needed"] = int(update.callback_query.data.removeprefix("su_"))
    kb = InlineKeyboardMarkup([*[[btn(t(lang, f"urg_{u}"), f"sx_{u}")] for u in URGENCIES], cancel_row(lang)])
    await show(update, f"🩸 {sos['units_needed']} × <b>{sos['blood_group']}</b> · 🏥 {esc(sos['hospital'])}\n\n"
               + t(lang, "sos_urgency"), kb)
    return SOS_URGENCY


async def sos_urgency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    lang = L(context)
    sos = context.user_data["sos"]
    sos["urgency"] = update.callback_query.data.removeprefix("sx_")
    await show(update, f"🩸 {sos['units_needed']} × <b>{sos['blood_group']}</b> · 🏥 {esc(sos['hospital'])}, "
               f"{esc(sos['city'])} · {t(lang, 'urg_' + sos['urgency'])}")
    await reply(update, t(lang, "sos_phone"), reply_markup=phone_kb(lang))
    return SOS_PHONE


async def sos_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    sos = context.user_data.pop("sos", {})
    tg = update.effective_user
    payload = {"blood_group": sos["blood_group"], "hospital": sos["hospital"], "city": sos["city"],
               "state": sos.get("state"), "units_needed": sos.get("units_needed", 1),
               "urgency": sos.get("urgency", "Critical"), "contact_phone": extract_phone(update),
               "requester_name": tg.full_name or tg.first_name or "Telegram user",
               "requester_telegram_id": str(tg.id), "requester_language": lang}
    msg = await reply(update, t(lang, "working"), reply_markup=ReplyKeyboardRemove())
    try:
        res = await api("POST", "/sos", json=payload)
    except ApiError as e:
        await msg.edit_text(t(lang, "sos_failed", error=err_text(lang, e)), parse_mode=ParseMode.HTML)
        return END
    await msg.edit_text(
        t(lang, "sos_done", units=payload["units_needed"], group=payload["blood_group"], hospital=esc(payload["hospital"]),
          district=esc(res["request"]["city"]), matched=res["matched_donors"], alerted=res["telegram_reachable"],
          id=res["request_id"]),
        parse_mode=ParseMode.HTML)
    await show_menu(update, context)
    return END


# ------------------------------------------------------------------ one-tap donate
async def donate_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """SOS alert button: ask the quick health check first (one tap if nothing applies)."""
    q = update.callback_query
    lang = await ensure_lang(update, context) or "en"
    request_id = int(q.data.removeprefix("donate_"))
    await ack(update)
    await context.bot.send_message(
        q.message.chat_id, t(lang, "elig_prompt"), parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[btn(t(lang, "elig_ok_btn"), f"dok_{request_id}")],
                                           [btn(t(lang, "elig_no_btn"), f"dno_{request_id}")]]))


async def reminder_later(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await ensure_lang(update, context) or "en"
    await ack(update, t(lang, "rem_later"))
    await update.callback_query.edit_message_reply_markup(None)


async def donate_declined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await ensure_lang(update, context) or "en"
    await ack(update)
    await update.callback_query.edit_message_text(t(lang, "elig_deferred", url=f"{WEB_URL}/profile"))


async def donate_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    lang = await ensure_lang(update, context) or "en"
    request_id = int(q.data.removeprefix("dok_"))
    screening = {"answers": {}, "basics_confirmed": True}  # the donor confirmed none of the listed conditions apply
    try:
        res = await api("POST", f"/donate/{request_id}",
                        json={"donor_telegram_id": str(update.effective_user.id), "confirmed": True, "screening": screening})
    except ApiError as e:
        elig = e.data.get("eligibility")
        if elig:
            wait = next((r for r in elig["reasons"] if r["code"] == "interval"), None)
            text = (t(lang, "elig_wait", date=wait["until"][:10]) if wait
                    else t(lang, "elig_not_now", url=f"{WEB_URL}/profile"))
            await ack(update)
            await q.edit_message_text(text)
            return
        await ack(update, (t(lang, "server_down") if str(e) == "server_down" else str(e))[:190], alert=True)
        return
    await ack(update, t(lang, "donate_thanks"))
    r, u = res["request"], res["donor"]
    lines = "\n".join(f"  +{b['points']} {t(lang, 'bd_' + b.get('code', 'donation'))}" for b in res["breakdown"])
    phone = t(lang, "contact", phone=esc(r["contact_phone"])) if r.get("contact_phone") else ""
    await q.edit_message_text(
        t(lang, "donated", id=r["id"], hospital=esc(r["hospital"]), city=esc(r["city"]), group=r["blood_group"],
          phone=phone, points=res["points_awarded"], lines=lines, balance=u["points"],
          badge=f"{BADGE_ICON.get(u['badge'], '')} {u['badge']}"),
        parse_mode=ParseMode.HTML)
    await context.bot.send_message(q.message.chat_id, t(lang, "invite", link=u["referral_link"]),
                                   parse_mode=ParseMode.HTML, disable_web_page_preview=True,
                                   reply_markup=InlineKeyboardMarkup([[btn(t(lang, "btn_menu"), "m_menu_show")]]))


# ------------------------------------------------------------------ info commands
async def not_registered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = L(context)
    await reply(update, t(lang, "not_registered"),
                reply_markup=InlineKeyboardMarkup([[btn(t(lang, "btn_register"), "m_register")]]))


async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ensure_lang(update, context)
    u = await current_user(update)
    if not u:
        return await not_registered(update, context)
    await reply(update, profile_text(L(context), u) + f"\n\n🌐 {WEB_URL}/profile", reply_markup=menu_kb(L(context), u))


async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ensure_lang(update, context)
    u = await current_user(update)
    if not u:
        return await not_registered(update, context)
    await reply(update, t(L(context), "invite", link=u["referral_link"]))


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ensure_lang(update, context)
    rows = await api("GET", "/leaderboard")
    lines = [f"#{i}  {BADGE_ICON.get(u['badge'], '')}  {esc(u['name'])} ({u['blood_group']}) — <b>{u['points']} BLP</b>"
             for i, u in enumerate(rows, 1)]
    await reply(update, t(L(context), "leaderboard") + "\n\n" + "\n".join(lines) + f"\n\n🌐 {WEB_URL}/leaderboard")


RARITY_DOT = {"Common": "⚪", "Uncommon": "🟢", "Rare": "🔵", "Epic": "🟣", "Legendary": "🟡", "Mythic": "🔴"}
TIER_ICON = {"Bronze": "🥉", "Silver": "🥈", "Gold": "🥇", "Platinum": "💎"}


async def achievements_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ensure_lang(update, context)
    lang = L(context)
    try:
        data = await api("GET", f"/users/by-telegram/{update.effective_user.id}/achievements")
    except ApiError:
        return await not_registered(update, context)
    s = data["summary"]
    lines = [t(lang, "ach_title"), t(lang, "ach_summary", unlocked=s["unlocked"], total=s["total"], points=s["points_earned"])]

    lines += ["", t(lang, "ach_tiers")]
    for f in data["families"]:
        tier = f"{TIER_ICON[f['tier']]} {f['tier']}" if f["tier"] else f"🔒 {t(lang, 'ach_locked')}"
        nxt = f" · {f['value']}/{f['next']['target']} → {f['next']['tier']}" if f["next"] else ""
        lines.append(f"{f['icon']} {esc(f['name'])}: <b>{tier}</b>{nxt}")

    got = sorted((a for a in data["singles"] if a["unlocked"]), key=lambda a: a["unlocked_at"], reverse=True)
    if got:
        lines += ["", t(lang, "ach_recent")]
        lines += [f"{a['icon']} <b>{esc(a['name'])}</b> {RARITY_DOT[a['rarity']]} {a['rarity']}" for a in got[:8]]
    else:
        lines += ["", t(lang, "ach_none")]

    locked = [a for a in data["singles"] if not a["unlocked"] and a["key"] != "admins_favorite"]
    locked.sort(key=lambda a: -a["progress"] / a["target"])
    lines += ["", t(lang, "ach_next")]
    lines += [f"🔒 {a['icon']} {esc(a['name'])}: {esc(a['requirement'])} ({a['progress']}/{a['target']})" for a in locked[:3]]
    lines += ["", f"🌐 {WEB_URL}/achievements"]
    await reply(update, "\n".join(lines))


def _camp_keyboard(lang: str, camps: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for c in camps:
        going = c.get("my_status") == "Registered"
        label = f"{t(lang, 'btn_unrsvp') if going else t(lang, 'btn_rsvp')} · {c['title'][:28]}"
        rows.append([btn(label, f"crsvp_{c['id']}")])
    return InlineKeyboardMarkup(rows)


async def camps_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ensure_lang(update, context)
    lang = L(context)
    u = await current_user(update)
    camps = await api("GET", "/camps", params={"user_id": u["id"]} if u else {})
    if u and u.get("state"):
        local = [c for c in camps if c.get("state") == u["state"]]
        camps = local or camps
    camps = camps[:6]
    if not camps:
        return await reply(update, t(lang, "camps_none", url=f"{WEB_URL}/camps"))
    lines = [t(lang, "camps_title"), ""]
    for c in camps:
        when = c["starts_at"][:10]
        going = f"  {t(lang, 'camp_going')}" if c.get("my_status") == "Registered" else ""
        lines.append(f"🗓 <b>{esc(c['title'])}</b> · {when}{going}\n📍 {esc(c['venue'])}, {esc(c['city'])} · 👥 {c['registered']}/{c['expected_donors']}")
    lines += ["", f"🌐 {WEB_URL}/camps"]
    await reply(update, "\n".join(lines), reply_markup=_camp_keyboard(lang, camps) if u else None)


async def camp_rsvp_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await ensure_lang(update, context) or "en"
    u = await current_user(update)
    if not u:
        await ack(update)
        return await not_registered(update, context)
    camp_id = int(update.callback_query.data.removeprefix("crsvp_"))
    try:
        res = await api("POST", f"/camps/{camp_id}/rsvp", json={"user_id": u["id"]})
    except ApiError as e:
        elig = e.data.get("eligibility")
        wait = next((r for r in elig["reasons"] if r["code"] == "interval"), None) if elig else None
        msg = t(lang, "elig_wait", date=wait["until"][:10]) if wait else (t(lang, "server_down") if str(e) == "server_down" else str(e))
        return await ack(update, msg[:190], alert=True)
    await ack(update, t(lang, "rsvp_ok") if res["status"] == "registered" else t(lang, "rsvp_cancel"))


async def teams_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ensure_lang(update, context)
    lang = L(context)
    u = await current_user(update)
    if not u:
        return await not_registered(update, context)
    teams = await api("GET", f"/users/{u['id']}/teams")
    if not teams:
        return await reply(update, t(lang, "teams_none", url=f"{WEB_URL}/teams"))
    lines = [t(lang, "teams_title"), ""]
    lines += [t(lang, "team_line", rank=x["rank"], name=esc(x["name"]), points=x["points"], donations=x["donations"],
                members=x["members"]) for x in teams]
    lines += ["", f"🌐 {WEB_URL}/teams"]
    await reply(update, "\n".join(lines))


async def requests_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ensure_lang(update, context)
    lang = L(context)
    u = await current_user(update)
    reqs = await api("GET", "/requests")
    if u:
        reqs = [r for r in reqs if u["blood_group"] in r["compatible_donor_groups"]]
    if not reqs:
        await reply(update, t(lang, "no_requests_match" if u else "no_requests"))
        return
    for r in reqs[:5]:
        text = t(lang, "req_item", group=r["blood_group"], urgency=t(lang, f"urg_{r['urgency']}"),
                 hospital=esc(r["hospital"]), city=esc(r["city"]), done=r["units_fulfilled"],
                 units=r["units_needed"], id=r["id"])
        kb = InlineKeyboardMarkup([[btn(t(lang, "btn_donate"), f"donate_{r['id']}")]]) if u else None
        await reply(update, text, reply_markup=kb)
    if not u:
        await not_registered(update, context)


async def set_available(update: Update, context: ContextTypes.DEFAULT_TYPE, value: bool):
    await ensure_lang(update, context)
    lang = L(context)
    try:
        u = await api("PATCH", f"/users/by-telegram/{update.effective_user.id}/availability",
                      json={"is_available": value})
    except ApiError:
        return await not_registered(update, context)
    await reply(update, t(lang, "avail_on" if value else "avail_off"), reply_markup=menu_kb(lang, u))


async def available(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_available(update, context, True)


async def busy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_available(update, context, False)


async def rewards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ensure_lang(update, context)
    lang = L(context)
    u = await current_user(update)
    items = await api("GET", "/rewards")
    lines = [f"• {esc(r['name'])} — {r['cost']} BLP" for r in items]
    header = t(lang, "balance", points=u["points"]) if u else t(lang, "register_to_redeem")
    kb = InlineKeyboardMarkup([[btn(f"🎁 {r['name']} ({r['cost']})", f"redeem_{r['id']}")] for r in items]) if u else None
    await reply(update, t(lang, "rewards") + "\n\n" + header + "\n\n" + "\n".join(lines), reply_markup=kb)


async def redeem_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await ensure_lang(update, context) or "en"
    try:
        # the backend sends the voucher code to this chat in the user's language
        await api("POST", f"/redeem/{update.callback_query.data.removeprefix('redeem_')}",
                  json={"telegram_id": str(update.effective_user.id)})
    except ApiError as e:
        await ack(update, (t(lang, "server_down") if str(e) == "server_down" else str(e))[:190], alert=True)
        return
    await ack(update, t(lang, "redeemed_popup"), alert=True)


async def menu_show_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    await ensure_lang(update, context)
    await show_menu(update, context)


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await ensure_lang(update, context):
        context.user_data["pending_start"] = None
        return await ask_language(update, context)
    await show_menu(update, context, t(L(context), "unknown"))


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    log.exception("Handler error", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        lang = context.user_data.get("lang", "en") if context.user_data is not None else "en"
        key = "server_down" if isinstance(context.error, ApiError) and str(context.error) == "server_down" else "error"
        try:
            await update.effective_message.reply_text(t(lang, key), reply_markup=ReplyKeyboardRemove())
        except Exception:  # noqa: BLE001
            pass


async def post_init(app: Application):
    for code, cmds in COMMANDS.items():
        await app.bot.set_my_commands([BotCommand(c, d) for c, d in cmds], language_code=None if code == "en" else code)
    log.info("Bot @%s running. API: %s", app.bot.username, API_URL)


# ------------------------------------------------------------------ wiring
def build_app() -> Application:
    persistence = PicklePersistence(filepath=Path(__file__).resolve().parent / "bot_state.pickle")
    app = Application.builder().token(TOKEN).persistence(persistence).post_init(post_init).build()
    text = filters.TEXT & ~filters.COMMAND
    cb = CallbackQueryHandler

    flows = ConversationHandler(
        entry_points=[CommandHandler("register", reg_start), CommandHandler("sos", sos_start),
                      cb(menu_router, pattern=r"^m_(sos|register)$")],
        states={
            REG_NAME: [MessageHandler(text, reg_name_text), cb(reg_name_tg, pattern=r"^rn_tg$")],
            REG_GROUP: [cb(reg_group, pattern=r"^rg_")],
            REG_STATE: [cb(reg_state, pattern=r"^rs_")],
            REG_DISTRICT: [cb(reg_district, pattern=r"^rd_")],
            REG_CITY: [MessageHandler(text, reg_city_text)],
            REG_PHONE: [MessageHandler(filters.CONTACT | text, reg_phone)],
            SOS_GROUP: [cb(sos_group, pattern=r"^sg_")],
            SOS_STATE: [cb(sos_state, pattern=r"^ss_")],
            SOS_DISTRICT: [cb(sos_district, pattern=r"^sd_")],
            SOS_HOSPITAL: [cb(sos_hospital, pattern=r"^sh_")],
            SOS_HOSP_TEXT: [MessageHandler(text, sos_hospital_text)],
            SOS_PLACE_TEXT: [MessageHandler(text, sos_place_text)],
            SOS_UNITS: [cb(sos_units, pattern=r"^su_\d+$")],
            SOS_URGENCY: [cb(sos_urgency, pattern=r"^sx_")],
            SOS_PHONE: [MessageHandler(filters.CONTACT | text, sos_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel), cb(cancel, pattern=r"^x_cancel$"),
                   CommandHandler("menu", menu_cmd), CommandHandler("start", start_over),
                   CommandHandler("register", reg_start), CommandHandler("sos", sos_start),
                   cb(menu_router, pattern=r"^m_(?!menu_show)")],
        allow_reentry=True,
        name="flows",
        persistent=True,
    )
    app.add_handler(flows)
    for name, fn in [("start", start), ("menu", menu_cmd), ("help", menu_cmd), ("language", ask_language),
                     ("me", me), ("invite", invite), ("leaderboard", leaderboard), ("achievements", achievements_cmd), ("camps", camps_cmd), ("teams", teams_cmd), ("requests", requests_cmd),
                     ("available", available), ("busy", busy), ("rewards", rewards), ("cancel", cancel)]:
        app.add_handler(CommandHandler(name, fn))
    app.add_handler(cb(menu_router, pattern=r"^m_(?!menu_show)"))
    app.add_handler(cb(menu_show_click, pattern=r"^m_menu_show$"))
    app.add_handler(cb(language_chosen, pattern=r"^lang_"))
    app.add_handler(cb(donate_click, pattern=r"^donate_\d+$"))
    app.add_handler(cb(donate_confirmed, pattern=r"^dok_\d+$"))
    app.add_handler(cb(donate_declined, pattern=r"^dno_\d+$"))
    app.add_handler(cb(reminder_later, pattern=r"^rem_later$"))
    app.add_handler(cb(camp_rsvp_click, pattern=r"^crsvp_\d+$"))
    app.add_handler(cb(redeem_click, pattern=r"^redeem_\d+$"))
    app.add_handler(cb(cancel, pattern=r"^x_cancel$"))
    app.add_handler(MessageHandler(text, unknown_text))
    app.add_error_handler(on_error)
    return app


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if not TOKEN:
        sys.exit("TELEGRAM_BOT_TOKEN is not set. Create a bot with @BotFather and put the token in .env")
    build_app().run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
