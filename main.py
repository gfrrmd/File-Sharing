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

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Database sementara untuk menyimpan kode captcha (dalam produksi disarankan pakai Redis/MongoDB)
# Format: { "kode_captcha": message_id_di_channel }
db_links = {}

def generate_captcha_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Handler untuk Admin (Upload Media)
@app.on_message(filters.private & filters.user(ADMIN_ID) & (filters.document | filters.video | filters.photo))
async def handle_admin_upload(client, message):
    # 1. Forward media ke channel database secara diam-diam
    pushed = await message.copy(DB_CHANNEL)
    
    # 2. Buat kode unik ala captcha
    captcha_code = generate_captcha_code()
    db_links[captcha_code] = pushed.id
    
    # 3. Berikan link kepada Admin
    bot_user = await client.get_me()
    share_link = f"https://t.me/{bot_user.username}?start={captcha_code}"
    
    await message.reply_text(
        f"✅ **File Berhasil Disimpan!**\n\nLink: `{share_link}`",
        disable_web_page_preview=True
    )

# Handler untuk User Klik /start [kode]
@app.on_message(filters.command("start") & filters.private)
async def handle_start(client, message):
    if len(message.command) > 1:
        code = message.command[1]
        msg_id = db_links.get(code)
        
        if msg_id:
            try:
                # Mengirim ulang file dari channel ke user tanpa header forward
                # protect_content=True mengunci fitur screenshot/forward
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=DB_CHANNEL,
                    message_id=msg_id,
                    protect_content=True 
                )
            except Exception as e:
                await message.reply_text("Terjadi kesalahan saat mengambil file.")
        else:
            await message.reply_text("❌ Link tidak valid atau sudah kadaluwarsa.")
    else:
        # Interaksi Non-Admin (Welcome Message)
        await message.reply_text("Halo! Kirimkan link bot yang valid untuk mendapatkan file.")

app.run()
