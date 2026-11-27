import asyncio

from pyrogram.errors import FloodWait, InputUserDeactivated, PeerIdInvalid, UserIsBlocked

# Shared state so both the bot command and the web dashboard can show progress
progress = {"running": False, "finished": False, "total": 0, "done": 0, "success": 0, "blocked": 0, "failed": 0}


async def _send(client, uid, text, source, parse_mode):
    if source is not None:
        return await source.copy(uid)
    kwargs = {"parse_mode": parse_mode} if parse_mode is not None else {}
    return await client.send_message(uid, text, **kwargs)


async def broadcast(client, db, *, text=None, source=None, parse_mode=None):
    progress.update(running=True, finished=False, total=0, done=0, success=0, blocked=0, failed=0)
    try:
        ids = await db.all_user_ids()
        progress["total"] = len(ids)
        for uid in ids:
            for _ in range(2):
                try:
                    await _send(client, uid, text, source, parse_mode)
                    progress["success"] += 1
                except FloodWait as e:
                    await asyncio.sleep(e.value + 1)
                    continue
                except (UserIsBlocked, InputUserDeactivated, PeerIdInvalid):
                    progress["blocked"] += 1
                    await db.remove_user(uid)
                except Exception:
                    progress["failed"] += 1
                break
            else:
                progress["failed"] += 1
            progress["done"] += 1
            await asyncio.sleep(0.05)
    finally:
        progress.update(running=False, finished=True)
    return dict(progress)
