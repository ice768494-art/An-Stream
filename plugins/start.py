from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton as Btn
from pyrogram.types import InlineKeyboardMarkup as Markup

from db import db
from info import CHANNEL_LINK, CHANNEL_NAME, LOG_CHANNEL
from util.file_properties import get_hash
from util.forcesub import join_markup, missing_channels


def home_text(user):
    return (
        f"<b>Welcome to {CHANNEL_NAME}</b>\n\n"
        f"Hello {user.mention}, send me any video, document or audio file and I will instantly "
        "create a <b>stream link</b> and a <b>download link</b> for it.\n\n"
        "Use the buttons below to learn more."
    )


HELP_TEXT = (
    "<b>How to use</b>\n\n"
    "1. Send me a video, document or audio file.\n"
    "2. I reply with a <b>Watch</b> link and a <b>Download</b> link.\n"
    "3. Open the Watch link for the web player, or use the buttons on that page to open the "
    "file in VLC, MX Player and other apps.\n"
    "4. On the player page, tap <b>Get file on Telegram</b> to receive the file in this chat."
)

ABOUT_TEXT = (
    f"<b>About {CHANNEL_NAME}</b>\n\n"
    "- Instant stream and download links\n"
    "- Web player with seeking\n"
    "- Open in external players\n"
    "- Secure hash-protected links\n\n"
    f"<i>Powered by {CHANNEL_NAME}</i>"
)


def home_markup():
    rows = [[Btn("Help", callback_data="help"), Btn("About", callback_data="about")]]
    if CHANNEL_LINK:
        rows.append([Btn(f"{CHANNEL_NAME} Channel", url=CHANNEL_LINK)])
    rows.append([Btn("Close", callback_data="close")])
    return Markup(rows)


def back_markup():
    return Markup([[Btn("Back", callback_data="home"), Btn("Close", callback_data="close")]])


@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    if await db.is_banned(user.id):
        return await message.reply_text("You are banned from using this bot.")

    is_new = await db.add_user(user.id, user.first_name or "")
    if is_new and LOG_CHANNEL:
        try:
            await client.send_message(LOG_CHANNEL, f"New user: {user.mention} (<code>{user.id}</code>)")
        except Exception:
            pass

    payload = message.command[1] if len(message.command) > 1 else ""
    missing = await missing_channels(client, user.id)
    if missing:
        me = client.me or await client.get_me()
        retry = f"https://t.me/{me.username}" + (f"?start={payload}" if payload else "")
        return await message.reply_text(
            f"<b>Access required</b>\n\nPlease join the channel(s) below to use {CHANNEL_NAME}, then tap Try again.",
            reply_markup=join_markup(missing, retry),
        )

    if payload.startswith("file_"):
        try:
            _, msg_id, h = payload.split("_", 2)
            log_msg = await client.get_messages(LOG_CHANNEL, int(msg_id))
            if not log_msg or log_msg.empty or get_hash(log_msg) != h:
                return await message.reply_text("File not found or link is invalid.")
            await log_msg.copy(message.chat.id)
        except Exception as e:
            await message.reply_text(f"Could not send the file: {e}")
        return

    await message.reply_text(home_text(user), reply_markup=home_markup())


@Client.on_callback_query(filters.regex("^(home|help|about|close)$"))
async def menu(client, query):
    action = query.data
    if action == "close":
        await query.answer()
        return await query.message.delete()
    if action == "home":
        text, markup = home_text(query.from_user), home_markup()
    elif action == "help":
        text, markup = HELP_TEXT, back_markup()
    else:
        text, markup = ABOUT_TEXT, back_markup()
    try:
        await query.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass
    await query.answer()
