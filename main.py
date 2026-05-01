import os
from pyrogram import Client, filters

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID"))
DB_CHANNEL = int(os.getenv("DB_CHANNEL"))

app = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# database sementara
db = {}

# upload media admin
@app.on_message(filters.private & filters.media)
async def upload(client, message):

    # admin only
    if message.from_user.id != ADMIN_ID:
        return

    try:

        # KUNCI PALING PENTING:
        # pake copy()
        # jangan copy_message()
        # jangan forward_messages()

        cloud = await message.copy(
            chat_id=DB_CHANNEL
        )

        # save message id
        code = str(cloud.id)

        db[code] = cloud.id

        me = await client.get_me()

        link = f"https://t.me/{me.username}?start={code}"

        await message.reply_text(
            f"SUCCESS\n\n{link}"
        )

    except Exception as e:

        await message.reply_text(
            f"ERROR\n\n{e}"
        )

# get file
@app.on_message(filters.command("start"))
async def start(client, message):

    args = message.text.split()

    # start biasa
    if len(args) == 1:

        await message.reply_text(
            "Bot aktif."
        )

        return

    code = args[1]

    # invalid
    if code not in db:

        await message.reply_text(
            "Invalid."
        )

        return

    # send media
    await client.copy_message(
        chat_id=message.chat.id,
        from_chat_id=DB_CHANNEL,
        message_id=db[code],
        protect_content=True
    )

print("BOT RUNNING")
app.run()
