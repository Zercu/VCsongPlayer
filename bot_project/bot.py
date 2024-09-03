
import os
import zipfile
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import Update
from pytgcalls.types.stream import StreamType
from yt_dlp import YoutubeDL
import ffmpeg
from pyrogram.types import Message

# Configuration
API_ID = 'YOUR_API_ID'
API_HASH = 'YOUR_API_HASH'
BOT_TOKEN = 'YOUR_BOT_TOKEN'

# Initialize the bot and call handler
app = Client('bot', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# Set up yt-dlp options
ytdl_format_options = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ytdl = YoutubeDL(ytdl_format_options)

# Function to download and prepare audio/video
async def download_media(url, video_quality='720p'):
    loop = asyncio.get_event_loop()
    ytdl_format_options['format'] = f'bestvideo[height<={video_quality[:-1]}]+bestaudio/best'
    ytdl = YoutubeDL(ytdl_format_options)
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
    if 'entries' in data:
        data = data['entries'][0]
    return data['url'], data['title']

# Command to join voice chat
@app.on_message(filters.command('join'))
async def join_vc(client, message):
    if message.chat.type in ['group', 'supergroup']:
        await call_py.join_group_call(
            message.chat.id,
            'input.raw',
            stream_type=StreamType().local_stream
        )
        await message.reply("Joined the voice chat.")

# Command to play YouTube video/audio in voice chat
@app.on_message(filters.command('play'))
async def play_media(client, message):
    if len(message.command) < 2:
        await message.reply("Please provide a YouTube URL or video tag.")
        return

    if message.command[1].startswith("http"):
        url = message.command[1]
        video_quality = '720p'  # You can customize this
        media_url, title = await download_media(url, video_quality)
    else:
        tag = message.command[1]
        if tag in message.chat.get_media_messages():
            video_file = f"{tag}.mp4"
            media_url = video_file
            title = f"Playing tagged video: {tag}"
        else:
            await message.reply("Tag not found in the group.")
            return

    # Play the media
    process = (
        ffmpeg
        .input(media_url)
        .output('pipe:', format='s16le', acodec='pcm_s16le', ac=2, ar='48k')
        .run_async(pipe_stdout=True)
    )

    await call_py.change_stream(
        message.chat.id,
        process.stdout
    )

    await message.reply(f"Now playing: {title} in {video_quality} quality.")

# Command to handle video files sent to the group
@app.on_message(filters.video)
async def handle_video(client, message: Message):
    if len(message.caption) > 0 and "OmFo" in message.caption:
        file_path = await message.download(file_name=f"{message.caption.split()[0]}.mp4")
        await play_media(client, message)
    else:
        await message.reply("No tag 'OmFo' found in the caption. Video added to storage.")

# Command to send the zipped video files to the user
@app.on_message(filters.command('sendzip'))
async def send_zip(client, message):
    zip_filename = f"{message.chat.id}_videos.zip"
    
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for video in os.listdir():
            if video.endswith('.mp4'):
                zipf.write(video)
    
    if os.path.exists(zip_filename):
        await message.reply_document(zip_filename)
    else:
        await message.reply("No videos have been zipped yet.")

# Command to leave the voice chat
@app.on_message(filters.command('leave'))
async def leave_vc(client, message):
    await call_py.leave_group_call(message.chat.id)
    await message.reply("Left the voice chat.")

# Start the bot
@app.on_message(filters.command('start'))
async def start(client, message):
    await message.reply("Bot is running. Use /join to join the VC, /play to play media, and /leave to leave the VC.")

@app.on_raw_update()
async def raw_handler(client, update, users, chats):
    if isinstance(update, Update):
        print(f"Received update: {update}")

async def main():
    await call_py.start()
    await idle()

# Run the bot
app.start()
asyncio.run(main())
