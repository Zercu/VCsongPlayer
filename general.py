# handlers/general.py
from aiogram import types
from aiogram.dispatcher import Dispatcher

async def handle_help(message: types.Message):
    help_text = """
    Available Commands:
    /join - Make the bot join voice chat
    /play <song_name> - Play a song by name or YouTube URL
    /skip - Skip the current song
    /stop - Stop playing music
    /stats - Show bot stats (admin only)
    /adves <message> - Send an ad to all users and groups (admin only)
    """
    await message.reply(help_text)

def register_general_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_help, commands="help")
