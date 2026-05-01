import os
import string
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Ambil variabel dari Railway
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))
DB_CHANNEL = int(os.environ.get("DB_CHANNEL"))

app = Client("file_sharing_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Database sederhana dalam memori
db_links = {}

def generate_captcha_style_code(length=10):
    # Menggunakan kombinasi huruf besar, kecil, dan angka agar mirip captcha
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

# ================= USER INTERFACE (NON-ADMIN) =================

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    # Jika user klik link (ada argumen start)
    if len(message.command) > 1:
        code = message.command[1]
        msg_id = db_links.get(code)
        
        if msg_id:
            try:
                # Mengirim media dari cloud ke user
                # protect_content=True: Mencegah screenshot, save, dan forward
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=DB_CHANNEL,
                    message_id=msg_id,
                    protect_content=True 
                )
            except Exception as e:
                await message.reply_text("❌ Gagal mengambil file. Pastikan bot adalah Admin di Channel Database.")
        else:
            await message.reply_text("❌ Link kadaluwarsa atau salah.")
    
    # Jika user hanya klik start biasa
    else:
        if message.from_user.id == ADMIN_ID:
            await message.reply_text(
                "👋 **Halo Admin!**\n\nAnda bisa mengirim foto, video, atau dokumen ke sini "
                "untuk diubah menjadi link sharing otomatis."
            )
        else:
            await message.reply_text(
                "🙏 **Selamat Datang!**\n\nBot ini hanya bisa digunakan jika Anda memiliki "
                "link file yang sah dari Admin."
            )

# ================= ADMIN INTERFACE (UPLOAD) =================

# Filter hanya untuk ADMIN_ID dan tipe pesan media
@app.on_message(filters.private & filters.user(ADMIN_ID) & (filters.document | filters.video | filters.photo | filters.audio))
async def admin_upload_handler(client, message):
    try:
        # 1. Simpan ke Channel Database (Menghapus pengirim asli)
        stored_msg = await message.copy(DB_CHANNEL)
        
        # 2. Generate kode captcha
        code = generate_captcha_style_code()
        db_links[code] = stored_msg.id
        
        # 3. Berikan link ke admin
        bot = await client.get_me()
        link = f"https://t.me/{bot.username}?start={code}"
        
        await message.reply_text(
            f"✅ **Berhasil Disimpan di Cloud!**\n\n"
            f"🔗 **Link Sharing:**\n`{link}`\n\n"
            f"⚠️ *File ini diproteksi (Anti-Forward/Anti-Screenshot)*",
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply_text(f"❌ Gagal upload: {str(e)}")

# Tolak upload jika bukan admin
@app.on_message(filters.private & ~filters.user(ADMIN_ID) & (filters.document | filters.video | filters.photo))
async def non_admin_reject(client, message):
    await message.reply_text("🚫 **Akses Ditolak.** Anda tidak memiliki izin untuk mengupload file ke bot ini.")

app.run()
        
