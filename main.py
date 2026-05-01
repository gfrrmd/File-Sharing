import os
import random
import string
import traceback

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
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

# temporary db
db = {}

def generate_code(length=12):
    return ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=length
        )
    )

async def check_force_sub(client, user_id):

    try:
        await client.get_chat_member(
            CHANNEL_URL,
            user_id
        )
        return True

    except UserNotParticipant:
        return False

    except:
        return False


# START COMMAND
@app.on_message(filters.command("start"))
async def start_command(client, message):

    user_id = message.from_user.id
    args = message.text.split()

    # =========================
    # ADMIN START
    # =========================
    if user_id == ADMIN_ID and len(args) == 1:

        await message.reply_text(
            text=(
                "Admin mode aktif.\n\n"
                "Upload media buat generate link."
            ),
            protect_content=True
        )
        return

    # =========================
    # USER START NO PARAM
    # =========================
    if len(args) == 1:

        await message.reply_text(
            text=(
                "Bot file sharing.\n\n"
                "Klik link file yang dikasih admin "
                "buat ambil media."
            ),
            protect_content=True
        )
        return

    # =========================
    # GET FILE
    # =========================
    code = args[1]

    if code not in db:

        await message.reply_text(
            "Link invalid atau file udah mampus.",
            protect_content=True
        )
        return

    joined = await check_force_sub(
        client,
        user_id
    )

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
            text="Join channel dulu baru sok download.",
            reply_markup=btn,
            protect_content=True
        )
        return

    msg_id = db[code]

    # COPY biar no forward tag
    await client.copy_message(
        chat_id=message.chat.id,
        from_chat_id=DB_CHANNEL,
        message_id=msg_id,
        protect_content=True
    )


# ADMIN MEDIA UPLOAD
@app.on_message(filters.private & filters.media)
async def upload_handler(client, message):

    try:

        user_id = message.from_user.id

        # =========================
        # NON ADMIN BLOCK
        # =========================
        if user_id != ADMIN_ID:

            await message.reply_text(
                text=(
                    "Lu siapa upload-upload.\n"
                    "Bot ini khusus admin doang."
                ),
                protect_content=True
            )

            return

        # =========================
        # FORWARD TO CLOUD
        # =========================
        forwarded = await client.forward_messages(
            chat_id=DB_CHANNEL,
            from_chat_id=message.chat.id,
            message_ids=message.id
        )

        msg_id = forwarded.id

        code = generate_code()

        db[code] = msg_id

        me = await client.get_me()

        link = f"https://t.me/{me.username}?start={code}"

        await message.reply_text(
            text=(
                "Link berhasil dibuat.\n\n"
                f"{link}"
            ),
            protect_content=True,
            disable_web_page_preview=True
        )

    except Exception:
        print(traceback.format_exc())


print("BOT RUNNING...")
app.run()
