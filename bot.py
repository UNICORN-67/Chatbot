# vcbot.py — Ultra Stable VC Music Bot (Single File)

import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream.quality import HighQualityAudio
from pytgcalls.types.stream import StreamAudioEnded
from yt_dlp import YoutubeDL
import ffmpeg

# ================= CONFIG =================
API_ID = int(os.getenv("API_ID", "16841147"))
API_HASH = os.getenv("API_HASH", "724367ca3534a7e37594fcf3512dc8ad")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7493470667:AAEEgyqY3CKwKFeoct6uhJTUaW1djW1GTr0")
# ==========================================

# Create folders
os.makedirs("downloads", exist_ok=True)

app = Client("vc_music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
vc = PyTgCalls(app)

queue = {}   # {chat_id: [{"file": path, "title": title}]}

# ============ YouTube Downloader ============
def download(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "nocheckcertificate": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            return path, info.get("title", "Unknown")
    except:
        return None, None


# ============ Play System ==============
async def play_stream(chat_id):
    if chat_id not in queue or not queue[chat_id]:
        return

    data = queue[chat_id][0]
    file_path = data["file"]

    try:
        # convert audio to raw 48k for 0-lag streaming
        process = (
            ffmpeg
            .input(file_path)
            .output("pipe:", format="s16le", acodec="pcm_s16le", ac=2, ar=48000)
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )

        await vc.join_group_call(
            chat_id,
            InputStream(
                process.stdout,
                HighQualityAudio(),
            ),
        )
    except Exception as e:
        print("Error:", e)


# ============ On Song End =============
@vc.on_stream_end()
async def stream_end_handler(_, update: StreamAudioEnded):
    chat_id = update.chat_id

    if queue.get(chat_id):
        queue[chat_id].pop(0)

    if queue.get(chat_id):
        await play_stream(chat_id)
    else:
        await vc.leave_group_call(chat_id)


# ============ Commands ================

@app.on_message(filters.command("start"))
async def start(_, m: Message):
    await m.reply("🎵 Stable VC Music Bot\nUse /play <song link>")


@app.on_message(filters.command("play"))
async def play(_, m: Message):
    if len(m.command) < 2:
        return await m.reply("❗ Usage: /play <youtube link>")

    link = m.text.split(maxsplit=1)[1]

    msg = await m.reply("⏳ Downloading...")

    file, title = download(link)
    if not file:
        return await msg.edit("❌ Failed to download!")

    chat_id = m.chat.id

    if chat_id not in queue:
        queue[chat_id] = []

    queue[chat_id].append({"file": file, "title": title})

    if len(queue[chat_id]) == 1:
        await msg.edit(f"🎧 Playing: **{title}**")
        await play_stream(chat_id)
    else:
        await msg.edit(f"➕ Added to queue: **{title}**")


@app.on_message(filters.command("pause"))
async def pause(_, m: Message):
    try:
        await vc.pause_stream(m.chat.id)
        await m.reply("⏸ Paused")
    except:
        await m.reply("❗ Nothing is playing")


@app.on_message(filters.command("resume"))
async def resume(_, m: Message):
    try:
        await vc.resume_stream(m.chat.id)
        await m.reply("▶️ Resumed")
    except:
        await m.reply("❗ Nothing is paused")


@app.on_message(filters.command("skip"))
async def skip(_, m: Message):
    chat_id = m.chat.id
    if chat_id in queue and len(queue[chat_id]) > 1:
        queue[chat_id].pop(0)
        await play_stream(chat_id)
        return await m.reply("⏭ Skipped!")
    await m.reply("❗ No next track")


@app.on_message(filters.command("stop"))
async def stop(_, m: Message):
    chat_id = m.chat.id
    try:
        queue[chat_id] = []
        await vc.leave_group_call(chat_id)
        await m.reply("⏹ Stopped")
    except:
        await m.reply("❗ Bot not in VC")


# ============ Start Bot =============
async def main():
    await app.start()
    await vc.start()
    print("Bot is running without lag 🚀")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
