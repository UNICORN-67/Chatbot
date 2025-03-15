from pyrogram import Client, filters

app = Client("my_bot", bot_token="YOUR_BOT_API_TOKEN")

# Updated start command handler
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Hello! I am your updated group chatbot.")

# New feature: Echo all text messages in the group
@app.on_message(filters.text & filters.group)
async def echo(client, message):
    await message.reply(message.text)

# Additional handler for help command
@app.on_message(filters.command("help"))
async def help(client, message):
    await message.reply("This is the help message. Here you can describe how to use the bot.")

if __name__ == "__main__":
    app.run()
