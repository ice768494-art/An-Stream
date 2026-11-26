# Based on the TechVJ File-Stream-Bot plugin. Original credit: @VJ_Bots / @Tech_VJ
from urllib.parse import quote_plus

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from info import ALLOWED_USERS, LOG_CHANNEL, STREAM_MODE, URL
from util.file_properties import get_hash, get_media_file_size, get_name
from util.human_readable import humanbytes

media_filter = filters.video | filters.document | filters.audio


def allowed(user_id: int) -> bool:
    return not ALLOWED_USERS or user_id in ALLOWED_USERS


@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    await message.reply_text("Send me a file or video and I'll give you stream and download links.")


@Client.on_message(filters.private & media_filter)
async def handle_media(client, message):
    if not STREAM_MODE or not allowed(message.from_user.id):
        return
    log_msg = await message.copy(LOG_CHANNEL)
    name = quote_plus(get_name(log_msg))
    h = get_hash(log_msg)
    stream = f"{URL}watch/{log_msg.id}/{name}?hash={h}"
    download = f"{URL}{log_msg.id}/{name}?hash={h}&dl=1"

    await log_msg.reply_text(
        f"Link generated for #{message.from_user.id}\nUser: {message.from_user.mention}\nFile: {get_name(log_msg)}",
        quote=True,
        disable_web_page_preview=True,
    )
    await message.reply_text(
        f"<b>Your link is ready!</b>\n\n<b>File:</b> {get_name(log_msg)}\n"
        f"<b>Size:</b> {humanbytes(get_media_file_size(log_msg))}\n\n"
        f"<b>Download:</b> {download}\n<b>Watch:</b> {stream}",
        quote=True,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Stream", url=stream),
            InlineKeyboardButton("Download", url=download),
        ]]),
    )
