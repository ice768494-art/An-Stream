import html
import re
from urllib.parse import quote_plus

from aiohttp import web

from info import LOG_CHANNEL
from util.file_properties import get_hash, get_media_file_size, get_mime, get_name

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
    return web.Response(text="File to Link bot is running.")


@routes.get(r"/watch/{id:\d+}/{name}")
async def watch(request):
    msg_id = int(request.match_info["id"])
    msg = await fetch_message(request, msg_id)
    name = get_name(msg)
    src = f"/{msg_id}/{quote_plus(name)}?hash={get_hash(msg)}"
    mime = get_mime(msg)
    tag = "audio" if mime.startswith("audio") else "video"
    page = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(name)}</title>
<style>body{{margin:0;background:#111;color:#eee;font-family:sans-serif;text-align:center}}
{tag}{{width:100%;max-height:85vh;background:#000}}a{{color:#6cf}}</style></head>
<body><h3>{html.escape(name)}</h3>
<{tag} controls autoplay preload="metadata"><source src="{src}" type="{html.escape(mime)}"></{tag}>
<p><a href="{src}&dl=1">Download</a></p></body></html>"""
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
