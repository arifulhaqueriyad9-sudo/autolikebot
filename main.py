#!/usr/bin/env python3
"""FX FF LIKE BD — Free Fire likes bot."""

# Bootstrap required packages and write requirements.txt automatically.
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REQUIREMENTS = "python-telegram-bot>=21.0,<23.0\naiohttp>=3.9,<4.0\n"
REQ_PATH = BASE_DIR / "requirements.txt"
try:
    REQ_PATH.write_text(REQUIREMENTS, encoding="utf-8")
except OSError:
    REQ_PATH = Path.cwd() / "requirements.txt"
    REQ_PATH.write_text(REQUIREMENTS, encoding="utf-8")

missing = []
if importlib.util.find_spec("telegram") is None:
    missing.append("python-telegram-bot>=21.0,<23.0")
if importlib.util.find_spec("aiohttp") is None:
    missing.append("aiohttp>=3.9,<4.0")
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

import asyncio
import html
import json
import logging
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import aiohttp
from aiohttp import web
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "8823280270:AAF-auB09iS2j4mBRFOfQhN2cXYAdNLiL80").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", "6417430059"))
API_URL = "https://autolike-api-frexy.vercel.app/like?"
OWNER_URL = "https://t.me/Frexy1only"
WEBSITE_URL = "https://fx-like-bd.vercel.app"
LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", "-1003765179070"))
AUTHORIZED_GROUP_ID = int(os.getenv("AUTHORIZED_GROUP_ID", str(LOG_CHAT_ID)))
TZ = ZoneInfo("Asia/Dhaka")
DATA_DIR = BASE_DIR / "bot_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
ORDERS_FILE = DATA_DIR / "orders.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
USED_LIKES_FILE = DATA_DIR / "used_likes.json"
ORDER_LOCK = asyncio.Lock()

CUSTOM_EMOJI_POOL = [
    ("🔍", "5231012545799666522"), ("🛡", "5251203410396458957"), ("🔗", "5271604874419647061"),
    ("🖥", "5282843764451195532"), ("©", "5323442290708985472"), ("ℹ️", "5334544901428229844"),
    ("👍", "5337080053119336309"), ("▶️", "5348125953090403204"), ("⏸", "5359543311897998264"),
    ("💯", "5341498088408234504"), ("🔄", "5375338737028841420"), ("🔝", "5415655814079723871"),
    ("🆕", "5382357040008021292"), ("🔜", "5440621591387980068"), ("📍", "5391032818111363540"),
    ("➕", "5397916757333654639"), ("💎", "5427168083074628963"), ("⭐️", "5438496463044752972"),
    ("✨", "5325547803936572038"), ("👑", "5217822164362739968"), ("🗑", "5445267414562389170"),
    ("🔖", "5222444124698853913"), ("✉️", "5253742260054409879"), ("🔒", "5296369303661067030"),
    ("😮", "5303479226882603449"), ("📎", "5305265301917549162"), ("⚙️", "5341715473882955310"),
    ("🎮", "5361741454685256344"), ("🔈", "5388632425314140043"), ("⌛", "5386367538735104399"),
    ("⬇️", "5406745015365943482"), ("☀️", "5402477260982731644"), ("🌧", "5399913388845322366"),
    ("🌛", "5449569374065152798"), ("❄️", "5449449325434266744"), ("🌈", "5409109841538994759"),
    ("💧", "5393512611968995988"), ("🗓", "5413879192267805083"), ("💡", "5422439311196834318"),
    ("🥇", "5440539497383087970"), ("🥈", "5447203607294265305"), ("🥉", "5453902265922376865"),
    ("🎵", "5463107823946717464"), ("🆓", "5406756500108501710"), ("✏️", "5395444784611480792"),
    ("🚨", "5395695537687123235"), ("🛍", "5406683434124859552"), ("🏠", "5416041192905265756"),
    ("🚩", "5460755126761312667"), ("🎉", "5461151367559141950"), ("✅", "6147565374289220368"),
    ("😎", "6147464060305676048"), ("🌟", "6147629438021408084"), ("😁", "6147868521670907133"),
    ("❤️‍🔥", "6147617184479711380"), ("💀", "6147902731085420231"), ("💎", "6147524086768604985"),
    ("👍", "6147698410901214769"), ("😬", "6147815573314082674"), ("✔️", "6147460667281511517"),
    ("👇", "6147439566107186310"), ("🔥", "6235628846855492222"), ("⭐", "6235403472741603087"),
    ("👑", "6235252066554484059"), ("💥", "6235646232883107337"), ("🤑", "6237742262822901946"),
    ("🦁", "6237585380552480043"), ("💸", "6235445786759402354"), ("💰", "6235459831302460476"),
    ("🎁", "6242498410822244114"), ("📈", "6244492465353529537"), ("🍽", "6244501154072368012"),
    ("📣", "6242353099193718277"), ("⚠️", "6242010768825391425"), ("1️⃣", "6244317784738632020"),
    ("2️⃣", "6242147417504879292"), ("3️⃣", "6242172637552842445"), ("⚡", "6244678063775289843"),
    ("🚀", "6235302918967269680"), ("👻", "6237941218592960218"), ("🎉", "6242319667168287353"),
    ("🗿", "6235353887344170203"), ("🌹", "6235350382650859086"), ("🙏", "6237491767445296588"),
    ("🥳", "6237769162203076727"), ("🤖", "6129873536413605540"), ("💳", "6129926111108275647"),
    ("📱", "6125425225900237494"), ("🌐", "6125138773056430039"), ("🎥", "6123204598959189818"),
    ("✨", "6122884580945960571"), ("🛒", "6123015074937315826"), ("💬", "6172321806301538099"),
    ("👤", "6172309033068799949"), ("🎮", "6172195774781203007"), ("💙", "6172275927460881862"),
    ("🔛", "6174920038177317740"), ("💘", "6172512880806601884"), ("💰", "6172584215918421678"),
    ("🪶", "6244779107175895852"), ("🫧", "5796567714713572605"), ("🍊", "5796633857209931262"),
    ("🍇", "5794045349140108622"), ("🚀", "5796688063992172876"), ("💡", "5796431697394275354"),
    ("🌹", "5796409337794532823"), ("🎁", "5796463239634096295"), ("💳", "5798689673370931928"),
    ("💎", "5798757220321595976"), ("💊", "5798553402648565182"), ("🔬", "5796444659605574073"),
    ("⭐", "6122647168038740825"), ("⚡", "6122719177460426327"), ("📱", "6125297141385535507"),
    ("🔥", "6122786324979130530"), ("👑", "6125060175154914096"), ("🌎", "6122854679383647899"),
]

_EMOJI_DECK = []
_LAST_EMOJI_ID = None

def next_custom_emoji(exclude_ids=None):
    """Return a rotating premium emoji tag."""
    global _EMOJI_DECK, _LAST_EMOJI_ID
    exclude_ids = set(exclude_ids or ())
    if not _EMOJI_DECK:
        unique = {}
        for symbol, emoji_id in CUSTOM_EMOJI_POOL:
            unique[emoji_id] = (symbol, emoji_id)
        _EMOJI_DECK = list(unique.values())
        random.shuffle(_EMOJI_DECK)
    for index in range(len(_EMOJI_DECK) - 1, -1, -1):
        symbol, emoji_id = _EMOJI_DECK[index]
        if emoji_id not in exclude_ids and (emoji_id != _LAST_EMOJI_ID or len(_EMOJI_DECK) == 1):
            _EMOJI_DECK.pop(index)
            _LAST_EMOJI_ID = emoji_id
            return f'<tg-emoji emoji-id="{emoji_id}">{html.escape(symbol)}</tg-emoji>'
    _EMOJI_DECK = list({emoji_id: (symbol, emoji_id) for symbol, emoji_id in CUSTOM_EMOJI_POOL}.values())
    random.shuffle(_EMOJI_DECK)
    for index in range(len(_EMOJI_DECK) - 1, -1, -1):
        symbol, emoji_id = _EMOJI_DECK[index]
        if emoji_id not in exclude_ids:
            _EMOJI_DECK.pop(index)
            _LAST_EMOJI_ID = emoji_id
            return f'<tg-emoji emoji-id="{emoji_id}">{html.escape(symbol)}</tg-emoji>'
    return '⭐'

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("as-ff-like-bd")

def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return default

def write_json(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)

def public_enabled():
    return bool(read_json(SETTINGS_FILE, {}).get("public_mode", False))

def set_public(enabled):
    settings = read_json(SETTINGS_FILE, {})
    settings["public_mode"] = bool(enabled)
    write_json(SETTINGS_FILE, settings)

def is_owner(update):
    return bool(update.effective_user and update.effective_user.id == ADMIN_ID)

def estimate_days(likes):
    return max(1, (max(0, int(likes)) + 199) // 200)

def format_message(text):
    """Format messages line by line with premium emojis."""
    raw_lines = [line.rstrip() for line in str(text).splitlines()]
    while raw_lines and not raw_lines[0].strip():
        raw_lines.pop(0)
    if not raw_lines:
        return "<blockquote> </blockquote>"
    used_ids = set()
    heading_emoji = next_custom_emoji(used_ids)
    import re
    match = re.search(r'emoji-id="(\d+)"', heading_emoji)
    if match:
        used_ids.add(match.group(1))
    heading = html.escape(raw_lines[0].strip(), quote=False)
    details_lines = []
    for line in raw_lines[1:]:
        if not line.strip():
            details_lines.append("")
            continue
        emoji = next_custom_emoji(used_ids)
        match = re.search(r'emoji-id="(\d+)"', emoji)
        if match:
            used_ids.add(match.group(1))
        details_lines.append(f"{emoji} {html.escape(line, quote=False)}")
    details = "\n".join(details_lines)
    if details.strip():
        return f"<blockquote>{heading_emoji} <b>{heading}</b>\n\n{details}</blockquote>"
    return f"<blockquote>{heading_emoji} <b>{heading}</b></blockquote>"

async def reply(update, text):
    """Reply strictly to ADMIN only."""
    if not update or not update.message:
        return
    if not is_owner(update):
        return
    try:
        await update.message.reply_text(
            format_message(text),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception as exc:
        logger.warning("Formatted reply failed (%s); retrying as plain text", type(exc).__name__)
        try:
            await update.message.reply_text(str(text), disable_web_page_preview=True)
        except Exception:
            logger.exception("Plain-text reply also failed")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Unhandled Telegram update error", exc_info=context.error)

def player_fields(data):
    name = data.get("PlayerNickname") or data.get("player_name") or data.get("nickname") or "Unknown"
    before = data.get("LikesbeforeCommand", data.get("likes_before", "N/A"))
    after = data.get("LikesafterCommand", data.get("likes_after", "N/A"))
    try:
        given = max(0, int(data.get("LikesGivenByAPI", data.get("likes_given", 0)) or 0))
    except (ValueError, TypeError):
        given = 0
    return str(name), before, after, given

async def send_like_api(uid):
    params = {"uid": str(uid), "server_name": "BD"}
    last_error = "API unavailable"
    timeout = aiohttp.ClientTimeout(total=30, connect=10)
    for attempt in range(2):
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(API_URL, params=params) as response:
                    if response.status != 200:
                        last_error = f"API HTTP {response.status}"
                    else:
                        try:
                            data = await response.json(content_type=None)
                        except Exception:
                            last_error = "Invalid API response"
                        else:
                            if isinstance(data, dict):
                                return data
                            last_error = "Unexpected API response"
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            logger.warning("API attempt %s failed: %s", attempt + 1, type(exc).__name__)
            last_error = "API connection failed"
        if attempt == 0:
            await asyncio.sleep(1)
    return {"error": last_error}

def api_succeeded(data):
    if data.get("error"):
        return False
    status = data.get("status")
    return status in (1, 2, "1", "2") or data.get("success") is True

def next_day_start():
    now = datetime.now(TZ)
    target = (now + timedelta(days=1)).replace(hour=4, minute=0, second=0, microsecond=0)
    return target.isoformat()

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update) or not update.message:
        return
    await reply(update,
        "FX FF LIKE BD — OWNER START\n\n"
        "/like UID — manual like\n"
        "/order UID LIKE_AMOUNT — schedule auto-like (Up to 20k)\n"
        "/orderlist — view all orders\n"
        "/admin — admin commands\n/help — all commands"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update) or not update.message:
        return
    await reply(update,
        "FX FF LIKE BD — HELP\n\n"
        "/like UID — send likes once\n"
        "/order UID LIKE_AMOUNT — queue scheduled likes (1 - 20000)\n"
        "/orderlist — view all orders\n"
        "/admin — owner admin panel\n\n"
        f"Website: {WEBSITE_URL}\nAdmin: {OWNER_URL}"
    )

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update) or not update.message:
        return
    await reply(update,
        "FX FF LIKE BD — ADMIN PANEL\n\n"
        "/public — enable public commands in authorized group\n"
        "/offpublic — disable public commands\n"
        "/orderremove UID — remove pending orders for UID\n"
        "/orderlist — show all orders\n"
        "/resetlike USER_ID — allow a user to use /like again\n"
        f"Authorized group ID: {AUTHORIZED_GROUP_ID}"
    )

async def resetlike_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update) or not update.message:
        return
    if len(context.args) != 1 or not context.args[0].isdigit():
        await reply(update, "Correct format: /resetlike USER_ID")
        return
    user_id = str(context.args[0])
    used = read_json(USED_LIKES_FILE, {})
    existed = user_id in used
    used.pop(user_id, None)
    write_json(USED_LIKES_FILE, used)
    await reply(update, "User /like permission reset." if existed else "This user has no recorded /like usage.")

async def public_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update) or not update.message:
        return
    set_public(True)
    await reply(update, f"PUBLIC MODE ON\nAuthorized group ID: {AUTHORIZED_GROUP_ID}")

async def offpublic_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update) or not update.message:
        return
    set_public(False)
    await reply(update, "PUBLIC MODE OFF\nOnly owner commands enabled.")

async def like_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update) or not update.message:
        return
    if len(context.args) != 1 or not context.args[0].isdigit():
        await reply(update, "Incorrect command format.\nCorrect: /like UID\nExample: /like 123456789")
        return
    uid = context.args[0]
    data = await send_like_api(uid)
    if not api_succeeded(data):
        await reply(update, "Like request failed. Check the UID or try again later.")
        return
    name, before, after, given = player_fields(data)
    report = (
        "LIKE SUCCESSFULLY SENT\n\n"
        f"Player Name: {name}\n"
        f"UID: {uid}\n"
        f"Likes Sent: {given}\n"
        f"Likes Before: {before}\n"
        f"Likes After: {after}"
    )
    await reply(update, report)

async def order_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update) or not update.message:
        return
    if len(context.args) != 2 or not all(arg.isdigit() for arg in context.args):
        await reply(update, "Incorrect format.\nCorrect: /order UID LIKE_AMOUNT\nExample: /order 123456789 5000")
        return
    uid, amount = context.args[0], int(context.args[1])
    if amount < 1 or amount > 20000:
        await reply(update, "LIKE_AMOUNT must be between 1 and 20000.")
        return
    async with ORDER_LOCK:
        orders = read_json(ORDERS_FILE, [])
        order_id = max([int(o.get("id", 0)) for o in orders] or [0]) + 1
        order = {
            "id": order_id,
            "uid": uid,
            "requested": amount,
            "delivered": 0,
            "created_by": update.effective_user.id,
            "created_at": datetime.now(TZ).isoformat(),
            "start_at": next_day_start(),
            "status": "queued",
            "last_before": "N/A",
            "last_after": "N/A",
            "player_name": "Pending",
        }
        orders.append(order)
        write_json(ORDERS_FILE, orders)
    
    days_needed = estimate_days(amount)
    await reply(
        update,
        "ORDER QUEUED SUCCESSFULLY\n\n"
        f"Order ID: #{order_id}\n"
        f"UID: {uid}\n"
        f"Total Likes Requested: {amount}\n"
        f"Estimated Duration: {days_needed} day(s) (about 200 likes/day)\n"
        "Processing Start: Next 4:00 AM"
    )

async def orderremove_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update) or not update.message:
        return
    if len(context.args) != 1 or not context.args[0].isdigit():
        return
    uid = context.args[0]
    async with ORDER_LOCK:
        orders = read_json(ORDERS_FILE, [])
        kept = []
        removed = 0
        for order in orders:
            if str(order.get("uid", "")) == uid and order.get("status") == "queued":
                removed += 1
            else:
                kept.append(order)
        if removed:
            write_json(ORDERS_FILE, kept)
    if removed:
        await reply(update, f"ORDER REMOVED\n\nUID: {uid}\nRemoved Pending Orders: {removed}")
    else:
        await reply(update, f"NO PENDING ORDER FOUND\n\nUID: {uid}")

async def orderlist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update) or not update.message:
        return
    orders = read_json(ORDERS_FILE, [])
    if not orders:
        await reply(update, "ORDER LIST\n\nNo orders found.")
        return
    lines = [f"FX FF LIKE BD — ALL ORDERS ({len(orders)})\n"]
    for order in sorted(orders, key=lambda item: int(item.get("id", 0))):
        requested = int(order.get("requested", 0) or 0)
        delivered = int(order.get("delivered", 0) or 0)
        remaining = max(0, requested - delivered)
        days_left = estimate_days(remaining)
        lines.append(
            f"Order #{order.get('id', '?')} | {str(order.get('status', 'unknown')).upper()}\n"
            f"UID: {order.get('uid', 'N/A')}\n"
            f"Player: {order.get('player_name', 'Pending')}\n"
            f"Likes: {delivered}/{requested}\n"
            f"Remaining: {remaining}\n"
            f"Days Left: {days_left} day(s)\n"
        )
    chunk = ""
    for entry in lines:
        candidate = (chunk + "\n" + entry).strip()
        if len(candidate) > 3500 and chunk:
            await reply(update, chunk)
            chunk = entry
        else:
            chunk = candidate
    if chunk:
        await reply(update, chunk)

async def process_queued_orders(application):
    """Process queued auto-like orders once daily at 04:00 Asia/Dhaka and send clean report to Admin inbox."""
    while True:
        now = datetime.now(TZ)
        target = now.replace(hour=4, minute=0, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)

        await asyncio.sleep(max(0, (target - now).total_seconds()))

        admin_reports = []

        async with ORDER_LOCK:
            orders = read_json(ORDERS_FILE, [])
            for order in orders:
                if order.get("status") != "queued":
                    continue

                try:
                    start_at = datetime.fromisoformat(order["start_at"])
                    if start_at.tzinfo is None:
                        start_at = start_at.replace(tzinfo=TZ)
                    if datetime.now(TZ) < start_at:
                        continue

                    uid = str(order["uid"])
                    data = await send_like_api(uid)

                    if not api_succeeded(data):
                        admin_reports.append(
                            f"❌ Auto-Like Failed\n"
                            f"UID: {uid}\n"
                            f"Player: {order.get('player_name', 'Pending')}\n"
                            f"Reason: API temporarily unavailable (will retry next 4:00 AM)"
                        )
                        continue

                    name, before, after, given = player_fields(data)
                    order["player_name"] = name
                    order["last_before"] = before
                    order["last_after"] = after
                    order["delivered"] = int(order.get("delivered", 0)) + given

                    requested = int(order.get("requested", 0))
                    remaining = max(0, requested - int(order["delivered"]))
                    if remaining == 0:
                        order["status"] = "completed"

                    write_json(ORDERS_FILE, orders)

                    days_left = estimate_days(remaining)
                    # Line-by-line detailed report for Admin inbox
                    single_report = (
                        f"👤 Player Name: {name}\n"
                        f"🆔 UID: {uid}\n"
                        f"👍 Likes Sent Today: {given}\n"
                        f"📊 Likes Before: {before}\n"
                        f"📈 Likes After: {after}\n"
                        f"🎯 Total Delivered: {order['delivered']} / {requested}\n"
                        f"⏳ Remaining Likes: {remaining}\n"
                        f"🗓 Days Left: {days_left} day(s)\n"
                        f"📌 Status: {order['status'].upper()}"
                    )
                    admin_reports.append(single_report)
                    await asyncio.sleep(1.5)

                except asyncio.CancelledError:
                    raise
                except Exception:
                    logger.exception("Failed processing a queued auto-like order")
                    try:
                        write_json(ORDERS_FILE, orders)
                    except Exception:
                        pass

        # Send daily logs directly to ADMIN inbox
        if admin_reports:
            full_header = f"📅 DAILY AUTO-LIKE REPORT (04:00 AM)\nTotal Processed: {len(admin_reports)}\n\n"
            chunk = full_header
            for report_text in admin_reports:
                candidate = chunk + report_text + "\n\n────────────────\n\n"
                if len(candidate) > 3500 and chunk:
                    try:
                        await application.bot.send_message(
                            chat_id=ADMIN_ID,
                            text=format_message(chunk.strip()),
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True
                        )
                    except Exception:
                        await application.bot.send_message(chat_id=ADMIN_ID, text=chunk.strip())
                    chunk = report_text + "\n\n────────────────\n\n"
                else:
                    chunk = candidate
            if chunk.strip():
                try:
                    await application.bot.send_message(
                        chat_id=ADMIN_ID,
                        text=format_message(chunk.strip()),
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                except Exception:
                    await application.bot.send_message(chat_id=ADMIN_ID, text=chunk.strip())

async def main_async():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing!")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("resetlike", resetlike_cmd))
    app.add_handler(CommandHandler("like", like_cmd))
    app.add_handler(CommandHandler("order", order_cmd))
    app.add_handler(CommandHandler("orderremove", orderremove_cmd))
    app.add_handler(CommandHandler("orderlist", orderlist_cmd))
    app.add_handler(CommandHandler("public", public_cmd))
    app.add_handler(CommandHandler("offpublic", offpublic_cmd))
    app.add_error_handler(error_handler)
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    asyncio.create_task(process_queued_orders(app))
    server = web.Application()
    async def health(_request):
        return web.Response(text="FX FF LIKE BD is running")
    server.router.add_get("/", health)
    runner = web.AppRunner(server)
    health_server_started = False
    try:
        await runner.setup()
        port = int(os.getenv("PORT", "8080"))
        site = web.TCPSite(runner, "0.0.0.0", port)
        try:
            await site.start()
            health_server_started = True
            logger.info("Health server listening on port %s", port)
        except OSError as exc:
            logger.warning("Health server could not bind port %s (%s). Continuing...", port, exc)
    except Exception:
        logger.exception("Could not initialize optional health server.")

    logger.info("FX FF LIKE BD started for ADMIN: %s", ADMIN_ID)
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        if health_server_started:
            await runner.cleanup()
        else:
            try:
                await runner.cleanup()
            except Exception:
                pass

def main():
    print("FX FF LIKE BD")
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
