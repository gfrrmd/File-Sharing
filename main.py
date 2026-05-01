import os
import random
import string
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID"))
DB_CHANNEL = int(os.getenv("DB_CHANNEL"))
CHANNEL_URL = os.getenv("CHANNEL_URL")

app = Client(
    "file-share-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

db = {}

def generate_code(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def check_force_sub(client, user_id):
    try:
        await client.get_chat_member(CHANNEL_URL, user_id)
        return True
    except UserNotParticipant:
        return False
    except:
        return False

@app.on_message(filters.command("start"))
async def start_command(client, message):
    args = message.text.split()

    if len(args) <= 1:
        await message.reply_text(
            "Upload file ke bot buat generate link.",
            protect_content=True
        )
        return

    code = args[1]

    if code not in db:
        await message.reply_text(
            "Link invalid jir.",
            protect_content=True
        )
        return

    joined = await check_force_sub(client, message.from_user.id)

    if not joined:
        btn = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "Join Channel",
                    url=CHANNEL_URL
                )
            ]
        ])

        await message.reply_text(
            "Join channel dulu baru sok akses file.",
            reply_markup=btn,
            protect_content=True
        )
        return

    msg_id = db[code]

    await client.copy_message(
        chat_id=message.chat.id,
        from_chat_id=DB_CHANNEL,
        message_id=msg_id,
        protect_content=True
    )

@app.on_message(
    filters.private &
    (filters.document | filters.video | filters.photo)
)
async def upload_handler(client, message):

    if message.from_user.id != ADMIN_ID:
        return

    copied = await message.copy(
        DB_CHANNEL
    )

    code = generate_code()

    db[code] = copied.id

    me = await client.get_me()

    link = f"https://t.me/{me.username}?start={code}"

    await message.reply_text(
        f"Link generated:\n\n{link}",
        protect_content=True,
        disable_web_page_preview=True
    )

print("BOT RUNNING...")
app.run()
