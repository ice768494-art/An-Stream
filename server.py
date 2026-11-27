import re
from urllib.parse import quote_plus

from aiohttp import web

from info import CHANNEL_LINK, CHANNEL_NAME, LOG_CHANNEL, URL
from player import build_page
from util.file_properties import get_hash, get_media_file_size, get_mime, get_name
from util.human_readable import humanbytes

routes = web.RouteTableDef()
CHUNK = 1024 * 1024  # Pyrogram streams in 1 MiB chunks


async def fetch_message(request, msg_id: int):
    client = request.app["client"]
    try:
        msg = await client.get_messages(LOG_CHANNEL, msg_id)
    except Exception:
        raise web.HTTPNotFound(text="File not found")
    if not msg or msg.empty or not get_media_file_size(msg):
        raise web.HTTPNotFound(text="File not found")
    if get_hash(msg) != request.query.get("hash", ""):
        raise web.HTTPForbidden(text="Invalid hash")
    return msg


@routes.get("/")
async def index(request):
    return web.Response(text=f"{CHANNEL_NAME} File to Link is running.")


@routes.get(r"/watch/{id:\d+}/{name}")
async def watch(request):
    msg_id = int(request.match_info["id"])
    msg = await fetch_message(request, msg_id)
    name = get_name(msg)
    # Absolute URL (built from the configured public URL) so external players can open it
    stream_url = f"{URL}{msg_id}/{quote_plus(name)}?hash={get_hash(msg)}"
    username = request.app.get("bot_username", "")
    tg_link = f"https://t.me/{username}?start=file_{msg_id}_{get_hash(msg)}" if username else ""
    page = build_page(
        name=name,
        size=humanbytes(get_media_file_size(msg)),
        mime=get_mime(msg),
        stream_url=stream_url,
        brand=CHANNEL_NAME,
        channel_link=CHANNEL_LINK,
        tg_link=tg_link,
    )
    return web.Response(text=page, content_type="text/html")


@routes.get(r"/{id:\d+}/{name}")
async def stream(request):
    msg_id = int(request.match_info["id"])
    msg = await fetch_message(request, msg_id)
    client = request.app["client"]

    size = get_media_file_size(msg)
    start, end = 0, size - 1
    range_header = request.headers.get("Range")
    if range_header:
        m = re.match(r"bytes=(\d*)-(\d*)", range_header)
        if m:
            s, e = m.groups()
            if s == "" and e:
                start = max(size - int(e), 0)
            else:
                if s:
                    start = int(s)
                if e:
                    end = min(int(e), size - 1)
    if start > end or start >= size:
        return web.Response(status=416, headers={"Content-Range": f"bytes */{size}"})

    disposition = "attachment" if request.query.get("dl") else "inline"
    headers = {
        "Content-Type": get_mime(msg),
        "Content-Length": str(end - start + 1),
        "Accept-Ranges": "bytes",
        "Content-Disposition": f'{disposition}; filename="{quote_plus(get_name(msg))}"',
    }
    status = 200
    if range_header:
        status = 206
        headers["Content-Range"] = f"bytes {start}-{end}/{size}"

    resp = web.StreamResponse(status=status, headers=headers)
    await resp.prepare(request)

    first_chunk = start // CHUNK
    skip = start % CHUNK
    remaining = end - start + 1
    chunks_needed = end // CHUNK - first_chunk + 1
    try:
        async for chunk in client.stream_media(msg, limit=chunks_needed, offset=first_chunk):
            if skip:
                chunk = chunk[skip:]
                skip = 0
            if len(chunk) > remaining:
                chunk = chunk[:remaining]
            await resp.write(chunk)
            remaining -= len(chunk)
            if remaining <= 0:
                break
    except (ConnectionResetError, ConnectionError):
        pass
    return resp
