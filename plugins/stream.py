# Based on the TechVJ File-Stream-Bot plugin. Original credit: @VJ_Bots / @Tech_VJ
from urllib.parse import quote_plus

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from info import ALLOWED_USERS, CHANNEL_NAME, LOG_CHANNEL, STREAM_MODE, URL
from util.file_properties import get_hash, get_media_file_size, get_name
from util.human_readable import humanbytes

media_filter = filters.video | filters.document | filters.audio


def allowed(user_id: int) -> bool:
    return not ALLOWED_USERS or user_id in ALLOWED_USERS


@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    if len(message.command) > 1 and message.command[1].startswith("file_"):
        try:
            _, msg_id, h = message.command[1].split("_", 2)
            log_msg = await client.get_messages(LOG_CHANNEL, int(msg_id))
            if not log_msg or log_msg.empty or get_hash(log_msg) != h:
                return await message.reply_text("File not found or link is invalid.")
            await log_msg.copy(message.chat.id)
        except Exception as e:
            await message.reply_text(f"Could not send the file: {e}")
        return
    await message.reply_text(
        f"Welcome to <b>{CHANNEL_NAME}</b>!\n\nSend me a file or video and I'll give you stream and download links."
    )


@Client.on_message(filters.private & media_filter)
async def handle_media(client, message):
    if not STREAM_MODE:
        return await message.reply_text("STREAM_MODE is off.")
    if not allowed(message.from_user.id):
        return await message.reply_text("You are not allowed to use this bot.")

    try:
        log_msg = await message.copy(LOG_CHANNEL)
        name = quote_plus(get_name(log_msg))
        h = get_hash(log_msg)
        stream = f"{URL}watch/{log_msg.id}/{name}?hash={h}"
        download = f"{URL}{log_msg.id}/{name}?hash={h}&dl=1"
    except Exception as e:
        return await message.reply_text(f"Could not save file to log channel: {e}")

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
