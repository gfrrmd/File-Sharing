import os
import string
import random
import json
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

# Konfigurasi
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))
DB_CHANNEL = int(os.environ.get("DB_CHANNEL"))
CHANNEL_URL = os.environ.get("CHANNEL_URL")

bot = Client("FileSharingBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Database Sederhana menggunakan JSON
DB_FILE = "database.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

db_map = load_db()

def generate_code(length=10):
    # Kode unik campuran huruf besar dan angka (seperti captcha)
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    
    # Force Subscribe Check
    try:
        await client.get_chat_member(DB_CHANNEL, user_id)
    except UserNotParticipant:
        return await message.reply(
            "⚠️ **Akses Ditolak**\n\nSilakan bergabung ke channel kami terlebih dahulu untuk mengambil file.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Gabung Channel", url=CHANNEL_URL)
            ]])
        )
    except Exception:
        pass

    if len(message.command) > 1:
        code = message.command[1]
        msg_id = db_map.get(code)
        
        if msg_id:
            # copy_message menghapus nama pengirim & protect_content melarang screenshot/forward
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=DB_CHANNEL,
                message_id=int(msg_id),
                protect_content=True
            )
        else:
            await message.reply("❌ Link salah atau file sudah dihapus.")
    else:
        await message.reply("Selamat datang! Bot ini siap digunakan.")

@bot.on_message(filters.private & (filters.document | filters.video | filters.photo | filters.audio))
async def handle_admin_upload(client, message):
    if message.from_user.id != ADMIN_ID:
        return

    # Forward ke channel (database cloud)
    sent_msg = await message.forward(DB_CHANNEL)
    
    # Buat kode unik
    code = generate_code()
    db_map[code] = sent_msg.id
    save_db(db_map)
    
    bot_info = await client.get_me()
    share_link = f"https://t.me/{bot_info.username}?start={code}"
    
    await message.reply(
        f"✅ **Berhasil di-generate!**\n\n"
        f"Link: `{share_link}`\n\n"
        f"**Fitur:** Anti-Forward & Anti-Screenshot Aktif.",
        disable_web_page_preview=True
    )

print("Bot sedang berjalan...")
bot.run()
    
