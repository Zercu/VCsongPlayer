import logging
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN
from handlers.music import register_music_handlers
from handlers.admin import register_admin_handlers
from handlers.general import register_general_handlers
from utils import create_db

# Logging and Bot initialization
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Initialize Database
create_db()

# Register command handlers
register_music_handlers(dp)
register_admin_handlers(dp)
register_general_handlers(dp)

# Start the bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
