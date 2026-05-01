import os
import random
import string
import traceback

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from pyrogram.errors import (
    UserNotParticipant,
    PeerIdInvalid
)

# =========================================
# ENV
# =========================================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID"))

# CLOUD CHANNEL
DB_CHANNEL = int(os.getenv("DB_CHANNEL"))

# FORCE SUB PRIVATE CHANNEL
FSUB_CHANNEL = int(os.getenv("FSUB_CHANNEL"))

# INVITE LINK PRIVATE CHANNEL
CHANNEL_URL = os.getenv("CHANNEL_URL")

# =========================================
# CLIENT
# =========================================

app = Client(
    "file-share-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================================
# TEMP DATABASE
# =========================================

db = {}

# =========================================
# RANDOM CODE
# =========================================

def generate_code(length=12):

    return ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=length
        )
    )

# =========================================
# FORCE SUB CHECK
# =========================================

async def check_force_sub(client, user_id):

    try:

        member = await client.get_chat_member(
            FSUB_CHANNEL,
            user_id
        )

        if member:
            return True

        return False

    except UserNotParticipant:

        return False

    except:

        return False

# =========================================
# START
# =========================================

@app.on_message(filters.command("start"))
async def start_command(client, message):

    try:

        args = message.text.split()

        # =================================
        # START TANPA PARAM
        # =================================

        if len(args) == 1:

            if message.from_user.id == ADMIN_ID:

                await message.reply_text(
                    "Admin mode aktif.\n\nUpload media sekarang."
                )

            else:

                await message.reply_text(
                    "Bot file sharing aktif."
                )

            return

        # =================================
        # GET FILE
        # =================================

        code = args[1]

        # invalid code
        if code not in db:

            await message.reply_text(
                "Link invalid jir."
            )

            return

        # force sub check
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
                "Join channel dulu baru akses file.",
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

    except Exception as e:

        print("START ERROR")
        print(str(e))
        print(traceback.format_exc())

# =========================================
# HANDLE PRIVATE MESSAGE
# =========================================

@app.on_message(filters.private)
async def private_handler(client, message):

    try:

        # =================================
        # ADMIN ONLY
        # =================================

        if message.from_user.id != ADMIN_ID:
            return

        # =================================
        # MEDIA ONLY
        # =================================

        if not message.media:
            return

        print("MEDIA DETECTED")

        # =================================
        # INIT CHANNEL
        # FIX PEER INVALID
        # =================================

        chat = await client.get_chat(DB_CHANNEL)

        print(f"CLOUD: {chat.title}")

        # =================================
        # COPY TO CLOUD
        # =================================

        copied = await client.copy_message(
            chat_id=DB_CHANNEL,
            from_chat_id=message.chat.id,
            message_id=message.id
        )

        print("UPLOAD SUCCESS")

        # =================================
        # SAVE DATA
        # =================================

        msg_id = copied.id

        code = generate_code()

        db[code] = msg_id

        # =================================
        # GENERATE LINK
        # =================================

        me = await client.get_me()

        link = f"https://t.me/{me.username}?start={code}"

        # =================================
        # SEND RESULT
        # =================================

        await message.reply_text(
            text=(
                "Link generated:\n\n"
                f"{link}"
            ),
            disable_web_page_preview=True
        )

    except PeerIdInvalid:

        await message.reply_text(
            "Peer invalid.\n\n"
            "Fix:\n"
            "- pastikan channel private\n"
            "- bot admin\n"
            "- ID channel benar\n"
            "- jangan pake group/forum"
        )

    except Exception as e:

        print("UPLOAD ERROR")
        print(str(e))
        print(traceback.format_exc())

        await message.reply_text(
            f"Error:\n{e}"
        )

# =========================================
# RUN
# =========================================

print("BOT RUNNING...")
app.run()
