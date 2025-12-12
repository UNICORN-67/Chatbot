from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import youtube_dl
from pytube import YouTube
import os
import asyncio
import random

# Config
api_id = 16841147
api_hash = "724367ca3534a7e37594fcf3512dc8ad"
bot_token = "7493470667:AAEEgyqY3CKwKFeoct6uhJTUaW1djW1GTr0"

# Group VC variables
group_id = -1002301496075  # Replace with your group ID
vc_id = None

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3111.101 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
]

def get_user_agent():
    return random.choice(user_agents)

ydl_opts = {
    'outtmpl': '%(title)s.%(ext)s',
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'user_agent': get_user_agent(),
}

app = Client("music_bot", api_id, api_hash, bot_token=bot_token)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Send me a song name or link to download")

@app.on_message(filters.command("join"))
async def join_vc(client, message):
    global vc_id
    try:
        vc_id = await client.join_group_call(group_id)
        await message.reply_text("Joined VC!")
    except Exception as e:
        await message.reply_text(str(e))

@app.on_message(filters.command("leave"))
async def leave_vc(client, message):
    global vc_id
    try:
        await client.leave_group_call(group_id)
        vc_id = None
        await message.reply_text("Left VC!")
    except Exception as e:
        await message.reply_text(str(e))

@app.on_message(filters.command("play"))
async def play(client, message):
    global vc_id
    try:
        query = message.text.replace("/play ", "")
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            url = info['entries'][0]['webpage_url']
            title = info['entries'][0]['title']
            await message.reply_text(f"Playing {title}...")
            if vc_id is None:
                await join_vc(client, message)
            await client.send_audio(group_id, f"{title}.mp3")
            os.remove(f"{title}.mp3")
    except Exception as e:
        await message.reply_text(str(e))

app.run()
