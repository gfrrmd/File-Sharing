import os
import random
import string

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from pyrogram.errors import UserNotParticipant

# ===================================
# ENV
# ===================================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID"))

DB_CHANNEL = int(os.getenv("DB_CHANNEL"))

# PRIVATE FSUB CHANNEL ID
FSUB_CHANNEL = int(os.getenv("FSUB_CHANNEL"))

# PRIVATE INVITE LINK
CHANNEL_URL = os.getenv("CHANNEL_URL")

# ===================================
# CLIENT
# ===================================

app = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ===================================
# TEMP DATABASE
# ===================================

db = {}

# ===================================
# RANDOM CODE
# ===================================

def generate_code(length=10):

    return ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=length
        )
    )

# ===================================
# FORCE SUB CHECK
# ===================================

async def check_force_sub(client, user_id):

    try:

        member = await client.get_chat_member(
            FSUB_CHANNEL,
            user_id
        )

        # member valid
        if member:
            return True

        return False

    except UserNotParticipant:

        return False

    except:

        return False

# ===================================
# START
# ===================================

@app.on_message(filters.command("start"))
async def start(client, message):

    args = message.text.split()

    # ===============================
    # START BIASA
    # ===============================

    if len(args) == 1:

        if message.from_user.id == ADMIN_ID:

            await message.reply_text(
                "Admin aktif.\n\nUpload media sekarang."
            )

        else:

            await message.reply_text(
                "Bot file sharing aktif."
            )

        return

    # ===============================
    # GET CODE
    # ===============================

    code = args[1]

    # invalid
    if code not in db:

        await message.reply_text(
            "Link invalid."
        )

        return

    # cek force sub
    joined = await check_force_sub(
        client,
        message.from_user.id
    )

    # belum join
    if not joined:

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "Join Channel",
                    url=CHANNEL_URL
                )
            ]
        ])

        await message.reply_text(
            "Join channel dulu jir.",
            reply_markup=buttons
        )

        return

    # ambil message id
    msg_id = db[code]

    # kirim media private
    await client.copy_message(
        chat_id=message.chat.id,
        from_chat_id=DB_CHANNEL,
        message_id=msg_id,
        protect_content=True
    )

# ===================================
# HANDLE PRIVATE MESSAGE
# ===================================

@app.on_message(filters.private)
async def private_handler(client, message):

    # admin only
    if message.from_user.id != ADMIN_ID:
        return

    # wajib media
    if not message.media:
        return

    try:

        # copy ke cloud
        copied = await message.copy(
            DB_CHANNEL
        )

        # message id cloud
        msg_id = copied.id

        # random code
        code = generate_code()

        # save
        db[code] = msg_id

        # username bot
        me = await client.get_me()

        # generate link
        link = f"https://t.me/{me.username}?start={code}"

        # kirim hasil
        await message.reply_text(
            f"Link generated:\n\n{link}",
            disable_web_page_preview=True
        )

    except Exception as e:

        await message.reply_text(
            f"Error:\n{e}"
        )

print("BOT RUNNING...")
app.run()
