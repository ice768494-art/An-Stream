import asyncio

from pyrogram import Client, filters

from broadcast import broadcast, progress
from db import db
from info import ADMIN_PASSWORD, ADMINS, FORCE_SUB, URL

admin_only = filters.private & filters.user(ADMINS)
_tasks = set()


@Client.on_message(filters.command("admin") & admin_only)
async def admin_help(client, message):
    dash = f"{URL}admin" if ADMIN_PASSWORD else "disabled (set ADMIN_PASSWORD)"
    await message.reply_text(
        "<b>Admin panel</b>\n\n"
        "/stats - bot statistics\n"
        "/broadcast - reply to a message to send it to all users\n"
        "/ban <code>user_id</code> - ban a user\n"
        "/unban <code>user_id</code> - unban a user\n\n"
        f"Web dashboard: {dash}"
    )


@Client.on_message(filters.command("stats") & admin_only)
async def stats(client, message):
    await message.reply_text(
        "<b>Bot statistics</b>\n\n"
        f"Users: <b>{await db.total_users()}</b>\n"
        f"Files linked: <b>{await db.total_files()}</b>\n"
        f"Banned: <b>{await db.banned_count()}</b>\n"
        f"Force-sub channels: <b>{len(FORCE_SUB)}</b>"
    )


@Client.on_message(filters.command("broadcast") & admin_only)
async def bcast(client, message):
    source = message.reply_to_message
    if not source:
        return await message.reply_text("Reply to the message you want to broadcast with /broadcast.")
    if progress["running"]:
        return await message.reply_text("A broadcast is already running.")
    status = await message.reply_text("Broadcast started...")

    async def job():
        res = await broadcast(client, db, source=source)
        await status.edit_text(
            "<b>Broadcast finished</b>\n\n"
            f"Total: {res['total']}\nDelivered: {res['success']}\n"
            f"Blocked/removed: {res['blocked']}\nFailed: {res['failed']}"
        )

    task = asyncio.create_task(job())
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)


async def _moderate(message, ban):
    if len(message.command) < 2 or not message.command[1].lstrip("-").isdigit():
        return await message.reply_text(f"Usage: /{'ban' if ban else 'unban'} user_id")
    uid = int(message.command[1])
    await (db.ban(uid) if ban else db.unban(uid))
    await message.reply_text(f"User <code>{uid}</code> {'banned' if ban else 'unbanned'}.")


@Client.on_message(filters.command("ban") & admin_only)
async def ban(client, message):
    await _moderate(message, True)


@Client.on_message(filters.command("unban") & admin_only)
async def unban(client, message):
    await _moderate(message, False)
