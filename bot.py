import asyncio

from aiohttp import web
from pyrogram import Client, idle

from info import API_HASH, API_ID, BOT_TOKEN, LOG_CHANNEL, PORT
from server import routes


async def main():
    client = Client(
        "filebot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="plugins"),
        in_memory=True,
    )
    await client.start()
    await client.get_chat(LOG_CHANNEL)  # cache the log channel peer (bot must be admin there)

    app = web.Application()
    app["client"] = client
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    print(f"Bot and web server running on port {PORT}")

    await idle()
    await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
