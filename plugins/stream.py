# Based on the TechVJ File-Stream-Bot plugin. Original credit: @VJ_Bots / @Tech_VJ
import time
from urllib.parse import quote_plus

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db import db
from info import ALLOWED_USERS, CHANNEL_NAME, LOG_CHANNEL, STREAM_MODE, URL
from util.file_properties import get_hash, get_media_file_size, get_name
from util.forcesub import join_markup, missing_channels
from util.human_readable import humanbytes

media_filter = filters.video | filters.document | filters.audio


def allowed(user_id: int) -> bool:
    return not ALLOWED_USERS or user_id in ALLOWED_USERS


@Client.on_message(filters.private & media_filter)
async def handle_media(client, message):
    user = message.from_user
    if await db.is_banned(user.id):
        return await message.reply_text("You are banned from using this bot.")
    if not STREAM_MODE:
        return await message.reply_text("Link generation is currently turned off.")
    if not allowed(user.id):
        return await message.reply_text("You are not allowed to use this bot.")

    await db.add_user(user.id, user.first_name or "")
    missing = await missing_channels(client, user.id)
    if missing:
        return await message.reply_text(
            f"<b>Access required</b>\n\nPlease join the channel(s) below, then send your file again.",
            reply_markup=join_markup(missing),
        )

    try:
        log_msg = await message.copy(LOG_CHANNEL)
        name = quote_plus(get_name(log_msg))
        h = get_hash(log_msg)
        stream = f"{URL}watch/{log_msg.id}/{name}?hash={h}"
        download = f"{URL}{log_msg.id}/{name}?hash={h}&dl=1"
    except Exception as e:
        return await message.reply_text(f"Could not save file to log channel: {e}")

    try:
        await db.add_file({
            "msg_id": log_msg.id, "name": get_name(log_msg),
            "size": get_media_file_size(log_msg), "user": user.id, "time": time.time(),
        })
    except Exception:
        pass

    text = (
        f"<b>Your link is ready!</b>\n\n<b>File:</b> {get_name(log_msg)}\n"
        f"<b>Size:</b> {humanbytes(get_media_file_size(log_msg))}\n\n"
        f"<b>Download:</b> {download}\n<b>Watch:</b> {stream}\n\n<i>Powered by {CHANNEL_NAME}</i>"
    )
    try:
        await message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Stream", url=stream),
                InlineKeyboardButton("Download", url=download),
            ]]),
        )
    except Exception as e:
        await message.reply_text(text + f"\n\n(Buttons failed: {e})")
