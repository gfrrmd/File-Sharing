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

# ==========================================
# ENV
# ==========================================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID"))

# CHANNEL CLOUD / DATABASE
DB_CHANNEL = int(os.getenv("DB_CHANNEL"))

# FORCE SUB CHANNEL URL
# contoh:
# https://t.me/channelku
CHANNEL_URL = os.getenv("CHANNEL_URL")

# ambil username channel
CHANNEL_USERNAME = CHANNEL_URL.replace(
    "https://t.me/",
    ""
)

# ==========================================
# CLIENT
# ==========================================

app = Client(
    "file-share-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==========================================
# TEMP DATABASE
# WARNING:
# restart railway = hilang
# nanti upgrade pake mongodb
# ==========================================

db = {}

# ==========================================
# RANDOM CODE
# ==========================================

def generate_code(length=12):

    return ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=length
        )
    )

# ==========================================
# FORCE SUB CHECK
# ==========================================

async def check_force_sub(client, user_id):

    try:

        await client.get_chat_member(
            CHANNEL_USERNAME,
            user_id
        )

        return True

    except UserNotParticipant:

        return False

    except:

        return False

# ==========================================
# START COMMAND
# ==========================================

@app.on_message(filters.command("start"))
async def start_command(client, message):

    try:

        args = message.text.split()

        # ==================================
        # ADMIN START
        # ==================================

        if len(args) == 1 and message.from_user.id == ADMIN_ID:

            await message.reply_text(
                text=(
                    "Admin mode aktif.\n\n"
                    "Upload media buat generate link."
                )
            )

            return

        # ==================================
        # USER START
        # ==================================

        if len(args) == 1:

            await message.reply_text(
                text=(
                    "Bot file sharing aktif.\n\n"
                    "Klik link dari admin buat ambil file."
                )
            )

            return

        # ==================================
        # GET FILE
        # ==================================

        code = args[1]

        # code invalid
        if code not in db:

            await message.reply_text(
                "Link invalid jir."
            )

            return

        # cek join channel
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
                text=(
                    "Join channel dulu baru akses file."
                ),
                reply_markup=buttons
            )

            return

        # ambil message id dari db
        msg_id = db[code]

        # kirim media
        # protect_content=True
        # supaya gabisa forward/screenshot
        await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=DB_CHANNEL,
            message_id=msg_id,
            protect_content=True
        )

    except Exception as e:

        print("START ERROR")
        print(str(e))
        print(traceback.format_exc())

# ==========================================
# UPLOAD MEDIA
# ==========================================

@app.on_message(filters.private & filters.media)
async def upload_handler(client, message):

    try:

        user_id = message.from_user.id

        # ==================================
        # NON ADMIN BLOCK
        # ==================================

        if user_id != ADMIN_ID:

            await message.reply_text(
                "Lu bukan admin jir."
            )

            return

        # ==================================
        # FORWARD KE CLOUD
        # lebih cepat dibanding copy
        # ==================================

        forwarded = await client.forward_messages(
            chat_id=DB_CHANNEL,
            from_chat_id=message.chat.id,
            message_ids=message.id
        )

        # ambil message id cloud
        msg_id = forwarded.id

        # generate random code
        code = generate_code()

        # simpan ke database sementara
        db[code] = msg_id

        # ambil username bot
        me = await client.get_me()

        # generate link
        link = f"https://t.me/{me.username}?start={code}"

        # kirim link ke admin
        await message.reply_text(
            text=(
                "Link generated:\n\n"
                f"{link}"
            ),
            disable_web_page_preview=True
        )

    except Exception as e:

        print("UPLOAD ERROR")
        print(str(e))
        print(traceback.format_exc())

# ==========================================
# RUN BOT
# ==========================================

print("BOT RUNNING...")
app.run()
