import os
import string
import random
import json
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

# Variabel Railway
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))
DB_CHANNEL = int(os.environ.get("DB_CHANNEL"))
CHANNEL_URL = os.environ.get("CHANNEL_URL")

bot = Client("FileSharingBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DB_FILE = "links.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

db_map = load_db()

def generate_captcha_code(length=12):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# --- INTERAKSI USER (NON-ADMIN) ---
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    
    # 1. Cek Force Subscribe
    try:
        await client.get_chat_member(DB_CHANNEL, user_id)
    except UserNotParticipant:
        return await message.reply(
            "👋 **Halo!**\n\nUntuk mengakses file di bot ini, kamu harus bergabung ke channel kami terlebih dahulu.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📢 Gabung Channel", url=CHANNEL_URL),
                InlineKeyboardButton("🔄 Coba Lagi", url=f"https://t.me/{(await client.get_me()).username}?start={message.command[1] if len(message.command) > 1 else ''}")
            ]])
        )
    except Exception: pass

    # 2. Ambil File jika ada kode
    if len(message.command) > 1:
        code = message.command[1]
        msg_id = db_map.get(code)
        
        if msg_id:
            await message.reply("🚀 **Mengambil file dari cloud...**")
            # Metode COPY: Instan, tanpa upload ulang, menghapus info forwarder
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=DB_CHANNEL,
                message_id=int(msg_id),
                protect_content=True # Mencegah simpan/forward/screenshot
            )
        else:
            await message.reply("❌ **Link Kadaluarsa atau Salah.**")
    else:
        # Tampilan khusus Admin vs User di Start
        if user_id == ADMIN_ID:
            await message.reply(f"👋 **Halo Bos Admin!**\n\nKirimkan file apa saja ke sini, nanti saya buatkan link captchanya.")
        else:
            await message.reply("👋 **Halo!**\n\nSilakan masukkan link file sharing yang kamu miliki untuk mendownload.")

# --- INTERAKSI KHUSUS ADMIN (UPLOAD) ---
@bot.on_message(filters.private & (filters.document | filters.video | filters.photo | filters.audio | filters.animation))
async def handle_upload(client, message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ **Akses Ditolak.** Hanya Admin yang bisa upload file ke cloud.")

    status = await message.reply("⌛ **Memproses ke Cloud...**")
    
    # Forward ke channel (sebagai database cloud)
    sent_msg = await message.forward(DB_CHANNEL)
    
    # Buat kode captcha
    code = generate_captcha_code()
    db_map[code] = sent_msg.id
    save_db(db_map)
    
    bot_info = await client.get_me()
    share_link = f"https://t.me/{bot_info.username}?start={code}"
    
    await status.edit(
        f"✅ **File Berhasil Disimpan!**\n\n"
        f"🔗 **Link:** `{share_link}`\n\n"
        f"🛡️ **Proteksi:** Anti-Screenshot & Anti-Forward Aktif.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Bagikan Link", url=f"https://t.me/share/url?url={share_link}")
        ]])
    )

print("Bot Berjalan...")
bot.run()
        
