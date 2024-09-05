# handlers/admin.py
from aiogram import types
from aiogram.dispatcher import Dispatcher
from config import SUDO_USERS
from utils import get_stats

async def handle_stats(message: types.Message):
    # Only allow sudo users to access stats
    if message.from_user.id not in SUDO_USERS:
        return
    
    total_groups, total_users = get_stats()
    await message.reply(f"Total Groups: {total_groups}\nTotal Users: {total_users}")

async def handle_adves(message: types.Message):
    # Only allow sudo users to send ads
    if message.from_user.id not in SUDO_USERS:
        return
    
    ad_text = message.get_args()
    # Logic to send ads to all groups and users in the database
    # Placeholder for ad-sending logic

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_stats, commands="stats")
    dp.register_message_handler(handle_adves, commands="adves")
