from pyrogram import Client, filters

# Initialize the bot with API ID, API Hash, and Bot Token
app = Client(
    "my_bot",
    api_id="",
    api_hash="",
    bot_token=""
)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Hello! I am your group chatbot.")

@app.on_message(filters.text & filters.group)
async def echo(client, message):
    await message.reply(message.text)

@app.on_message(filters.command("help"))
async def help(client, message):
    await message.reply("This is the help message. Here you can describe how to use the bot.")

if __name__ == "__main__":
    app.run()
