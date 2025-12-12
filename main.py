from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import youtube_dl

api_id = 16841147
api_hash = "724367ca3534a7e37594fcf3512dc8ad"
bot_token = "7493470667:AAEEgyqY3CKwKFeoct6uhJTUaW1djW1GTr0"

app = Client("music_bot", api_id, api_hash, bot_token=bot_token)

ydl_opts = {
    'outtmpl': '%(title)s.%(ext)s',
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Send me a song name or link to download")

@app.on_message(filters.text)
async def music(client, message):
    try:
        query = message.text
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            url = info['entries'][0]['webpage_url']
            title = info['entries'][0]['title']
            await message.reply_text(f"Downloading {title}...")
            ydl.download([url])
            await message.reply_audio(f"{title}.mp3")
    except Exception as e:
        await message.reply_text(str(e))

app.run()
