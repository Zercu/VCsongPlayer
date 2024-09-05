# handlers/music.py
from pyrogram import Client
from aiogram import types
from aiogram.dispatcher import Dispatcher
import os
import asyncio
import subprocess
from youtube_search_python import VideosSearch
import yt_dlp

# Bot's Pyrogram client
app = Client("music_bot", api_id="YOUR_API_ID", api_hash="YOUR_API_HASH")

async def join_vc(chat_id):
    # Join the voice chat
    async with app:
        await app.join_chat(chat_id)
        await app.send_message(chat_id, "Bot has joined the Voice Chat!")

async def play_song(chat_id, song_name):
    # Search for the song on YouTube
    videos_search = VideosSearch(song_name, limit=1)
    video = videos_search.result()["result"][0]
    video_url = video["link"]
    
    # Download the audio using yt-dlp
    ydl_opts = {
        'format': 'bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info)
        audio_file = filename.replace(".webm", ".mp3")

    # Play the downloaded song in the voice chat
    await play_in_voice_chat(chat_id, audio_file)

async def play_in_voice_chat(chat_id, audio_file):
    process = subprocess.Popen(
        ['ffmpeg', '-re', '-i', audio_file, '-f', 's16le', '-ac', '2', '-ar', '48000', '-'],
        stdout=subprocess.PIPE
    )

    async with app:
        # Ensure the bot is in the voice chat
        await app.join_chat(chat_id)

        while True:
            output = process.stdout.read(1024)
            if not output:
                break
            # Send the audio stream to the voice chat here
            # Placeholder: Pyrogram's voice chat functionality integration.
    
    # Cleanup the audio file after playing
    os.remove(audio_file)

async def handle_join(message: types.Message):
    # Command to make bot join VC
    chat_id = message.chat.id
    await join_vc(chat_id)

async def handle_play(message: types.Message):
    # Command to play music
    chat_id = message.chat.id
    song_name = message.get_args()
    await play_song(chat_id, song_name)

def register_music_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_join, commands="join")
    dp.register_message_handler(handle_play, commands="play")
