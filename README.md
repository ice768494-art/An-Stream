# File to Link Bot (Render)

1. Create a bot with @BotFather; get API_ID / API_HASH from my.telegram.org.
2. Create a private channel, add the bot as admin, copy its ID (-100...) -> LOG_CHANNEL.
3. Push this folder to GitHub, create a Render Web Service (or use render.yaml).
4. Set env vars: API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, URL (https://yourapp.onrender.com/), STREAM_MODE=True.
   Optional: ALLOWED_USERS=123,456 to restrict who can generate links.
5. Send the bot a file; it replies with Watch and Download links.

Links stop working if the bot is banned, the log channel is deleted, or the logged message is removed.
Free Render instances sleep after ~15 min idle.
Credit: plugin based on TechVJ File-Stream-Bot (@VJ_Bots).
