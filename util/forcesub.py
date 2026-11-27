from pyrogram import enums
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from info import FORCE_SUB

_chats = {}
_links = {}


def _ref(value):
    v = value.strip()
    return int(v) if v.lstrip("-").isdigit() else v


async def _get_chat(client, ref):
    if ref not in _chats:
        _chats[ref] = await client.get_chat(ref)
    return _chats[ref]


async def _invite_link(client, chat):
    if chat.id not in _links:
        if chat.username:
            _links[chat.id] = f"https://t.me/{chat.username}"
        else:
            _links[chat.id] = chat.invite_link or await client.export_chat_invite_link(chat.id)
    return _links[chat.id]


async def missing_channels(client, user_id):
    """Return [(title, link)] for force-sub channels the user has not joined.
    If a channel cannot be checked (bot not admin, bad ID) it is skipped so nobody gets locked out."""
    missing = []
    for raw in FORCE_SUB:
        try:
            chat = await _get_chat(client, _ref(raw))
            try:
                member = await client.get_chat_member(chat.id, user_id)
                if member.status in (enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED):
                    missing.append((chat.title, await _invite_link(client, chat)))
            except UserNotParticipant:
                missing.append((chat.title, await _invite_link(client, chat)))
        except Exception as e:
            print(f"[force-sub] cannot check {raw}: {e}")
    return missing


def join_markup(missing, retry_url=None):
    rows = [[InlineKeyboardButton(f"Join {title}", url=link)] for title, link in missing]
    if retry_url:
        rows.append([InlineKeyboardButton("I've joined - Try again", url=retry_url)])
    return InlineKeyboardMarkup(rows)
