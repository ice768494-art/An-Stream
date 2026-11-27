import os

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))  # e.g. -1001234567890
STREAM_MODE = os.environ.get("STREAM_MODE", "True").lower() == "true"
PORT = int(os.environ.get("PORT", "8080"))
# Must end with a slash, e.g. https://yourapp.vercel.app/
URL = os.environ.get("URL", "http://localhost:8080/")
if not URL.endswith("/"):
    URL += "/"
# Optional: comma-separated Telegram user IDs allowed to use the bot. Empty = everyone.
ALLOWED_USERS = [int(x) for x in os.environ.get("ALLOWED_USERS", "").split(",") if x.strip()]
# Branding shown on the player page
CHANNEL_NAME = os.environ.get("CHANNEL_NAME", "CodeRips")
CHANNEL_LINK = os.environ.get("CHANNEL_LINK", "")  # e.g. https://t.me/yourchannel (optional)

# ---- Admin / database / force-sub ----
# Telegram user IDs of bot admins, comma-separated
ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split(",") if x.strip()]
# MongoDB connection string (recommended; without it data is kept in a local JSON file that Render wipes on redeploy)
DATABASE_URI = os.environ.get("DATABASE_URI", "")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "filebot")
# Force-subscribe channels, comma-separated: IDs (-100...) or @usernames. Bot must be admin there.
FORCE_SUB = [x.strip() for x in os.environ.get("FORCE_SUB", "").split(",") if x.strip()]
# Web dashboard login (dashboard is disabled if ADMIN_PASSWORD is empty)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
