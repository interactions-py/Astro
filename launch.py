import dotenv

dotenv.load_dotenv()

from src.bot import bot

bot.start()