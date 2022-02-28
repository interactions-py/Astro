import interactions
import dotenv
import logging

logging.basicConfig(level=logging.DEBUG)

TOKEN = dotenv.get_key(".env", "token")
EXTENSIONS = ["info", "tag", "user"]

bot = interactions.Client(TOKEN, disable_sync=True)
[bot.load(f"exts.{ext}") for ext in EXTENSIONS]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.me.name}.")

bot.start()
