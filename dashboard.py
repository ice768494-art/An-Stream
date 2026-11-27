import asyncio
import base64
import hashlib
import hmac
import html
import os
import time
from urllib.parse import quote_plus

from aiohttp import web
from pyrogram import enums

from broadcast import broadcast, progress
from db import db
from info import ADMIN_PASSWORD, ADMIN_USERNAME, CHANNEL_NAME, FORCE_SUB
from theme import page
from util.human_readable import humanbytes
from util.premium import fmt_date, grant

dash_routes = web.RouteTableDef()
_SECRET = os.urandom(32)
_tasks = set()


def _token():
    return hmac.new(_SECRET, b"admin-csrf", hashlib.sha256).hexdigest()


def _auth(request):
    if not ADMIN_PASSWORD:
        raise web.HTTPNotFound()
    header = request.headers.get("Authorization", "")
    if header.startswith("Basic "):
        try:
            user, _, pw = base64.b64decode(header[6:]).decode().partition(":")
            if hmac.compare_digest(user.encode(), ADMIN_USERNAME.encode()) and hmac.compare_digest(
                pw.encode(), ADMIN_PASSWORD.encode()
            ):
                return
        except Exception:
            pass
    raise web.HTTPUnauthorized(headers={"WWW-Authenticate": 'Basic realm="Admin"'})


def _csrf(data):
    if not hmac.compare_digest(str(data.get("t", "")).encode(), _token().encode()):
        raise web.HTTPForbidden(text="Bad token")


def _when(ts):
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(ts or 0)) + " UTC"


def _back(msg):
    raise web.HTTPSeeOther(f"/admin?msg={quote_plus(msg)}")


@dash_routes.get("/admin")
async def dashboard(request):
    _auth(request)
    users, files, banned = await db.total_users(), await db.total_files(), await db.banned_count()
    premium = await db.premium_count()
    rfiles, rusers = await db.recent_files(10), await db.recent_users(10)
    t = _token()

    if progress["running"]:
        status = f'Broadcast running: {progress["done"]} / {progress["total"]} sent'
    elif progress["finished"]:
        status = (
            f'Last broadcast: {progress["success"]} delivered, {progress["blocked"]} blocked/removed, '
            f'{progress["failed"]} failed (of {progress["total"]})'
        )
    else:
        status = "No broadcast has been sent since the last restart."

    notice = request.query.get("msg", "")
    notice_html = f'<div class="notice">{html.escape(notice)}</div>' if notice else ""

    frows = "".join(
        f"<tr><td>{html.escape(str(f.get('name') or ''))}</td><td>{humanbytes(f.get('size') or 0)}</td>"
        f"<td>{f.get('user')}</td><td>{_when(f.get('time'))}</td></tr>"
        for f in rfiles
    ) or '<tr><td colspan="4">No files yet</td></tr>'
    urows = "".join(
        f"<tr><td>{u['id']}</td><td>{html.escape(u.get('name') or '')}</td><td>{_when(u.get('joined'))}</td></tr>"
        for u in rusers
    ) or '<tr><td colspan="3">No users yet</td></tr>'

    body = f"""<main><div class="wrap">
<h1 style="margin:28px 0 0;font-size:24px">Admin Dashboard</h1>{notice_html}
<div class="stats">
  <div class="card stat"><div class="n">{users}</div><div class="l">Total users</div></div>
  <div class="card stat"><div class="n">{files}</div><div class="l">Files linked</div></div>
  <div class="card stat"><div class="n">{banned}</div><div class="l">Banned users</div></div>
  <div class="card stat"><div class="n">{premium}</div><div class="l">Premium users</div></div>
  <div class="card stat"><div class="n">{len(FORCE_SUB)}</div><div class="l">Force-sub channels</div></div>
</div>
<div class="two">
  <div class="card"><h2 class="s">Broadcast</h2><p style="color:var(--muted);font-size:13px;margin-top:0">{html.escape(status)}</p>
    <form method="post" action="/admin/broadcast"><input type="hidden" name="t" value="{t}">
    <textarea name="text" placeholder="Message to send to every user (HTML like &lt;b&gt;bold&lt;/b&gt; is supported)"></textarea>
    <div class="row"><button class="btn primary" type="submit">Send broadcast</button></div></form></div>
  <div class="card"><h2 class="s">Moderation</h2>
    <form method="post"><input type="hidden" name="t" value="{t}">
    <input type="text" name="user_id" placeholder="Telegram user ID">
    <div class="row"><button class="btn danger" formaction="/admin/ban" type="submit">Ban user</button>
    <button class="btn" formaction="/admin/unban" type="submit">Unban user</button></div></form></div>
  <div class="card"><h2 class="s">Premium</h2>
    <form method="post"><input type="hidden" name="t" value="{t}">
    <input type="text" name="user_id" placeholder="Telegram user ID">
    <input type="text" name="days" placeholder="Days (default 30)" style="margin-top:8px">
    <div class="row"><button class="btn primary" formaction="/admin/premium/add" type="submit">Grant premium</button>
    <button class="btn" formaction="/admin/premium/remove" type="submit">Revoke</button></div></form></div>
</div>
<div class="card" style="margin-bottom:14px"><h2 class="s">Recent files</h2><div class="tbl"><table>
<tr><th>Name</th><th>Size</th><th>User</th><th>Time</th></tr>{frows}</table></div></div>
<div class="card"><h2 class="s">Recent users</h2><div class="tbl"><table>
<tr><th>ID</th><th>Name</th><th>Joined</th></tr>{urows}</table></div></div>
</div></main>"""
    extra = '<meta http-equiv="refresh" content="4">' if progress["running"] else ""
    return web.Response(text=page(f"Admin | {CHANNEL_NAME}", body, CHANNEL_NAME, extra_head=extra), content_type="text/html")


@dash_routes.post("/admin/broadcast")
async def do_broadcast(request):
    _auth(request)
    data = await request.post()
    _csrf(data)
    text = (data.get("text") or "").strip()
    if not text:
        _back("Message is empty.")
    if progress["running"]:
        _back("A broadcast is already running.")
    progress["running"] = True
    task = asyncio.create_task(broadcast(request.app["client"], db, text=text, parse_mode=enums.ParseMode.HTML))
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
    _back("Broadcast started.")


async def _moderate(request, ban):
    _auth(request)
    data = await request.post()
    _csrf(data)
    try:
        uid = int(str(data.get("user_id", "")).strip())
    except ValueError:
        _back("Enter a valid numeric user ID.")
    await (db.ban(uid) if ban else db.unban(uid))
    _back(f"User {uid} {'banned' if ban else 'unbanned'}.")


@dash_routes.post("/admin/ban")
async def ban_user(request):
    await _moderate(request, True)


@dash_routes.post("/admin/unban")
async def unban_user(request):
    await _moderate(request, False)


@dash_routes.post("/admin/premium/add")
async def premium_add(request):
    _auth(request)
    data = await request.post()
    _csrf(data)
    try:
        uid = int(str(data.get("user_id", "")).strip())
        days = int(str(data.get("days", "") or 30).strip())
    except ValueError:
        _back("Enter valid numbers for user ID and days.")
    if not 1 <= days <= 3650:
        _back("Days must be between 1 and 3650.")
    expires = await grant(db, uid, days)
    try:
        await request.app["client"].send_message(uid, f"Your Premium is active until <b>{fmt_date(expires)}</b>. Thank you!")
    except Exception:
        pass
    _back(f"Premium granted to {uid} until {fmt_date(expires)}.")


@dash_routes.post("/admin/premium/remove")
async def premium_remove(request):
    _auth(request)
    data = await request.post()
    _csrf(data)
    try:
        uid = int(str(data.get("user_id", "")).strip())
    except ValueError:
        _back("Enter a valid numeric user ID.")
    await db.remove_premium(uid)
    _back(f"Premium removed from {uid}.")
