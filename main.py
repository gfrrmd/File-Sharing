import os
import base64
import logging
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

# Setup Logging agar kita bisa lihat error di log Railway
logging.basicConfig(level=logging.INFO)

# --- KONFIGURASI DARI RAILWAY ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))
DB_CHANNEL = int(os.environ.get("DB_CHANNEL"))  # Contoh: -100123456789
CHANNEL_URL = os.environ.get("CHANNEL_URL")    # Link Join (https://t.me/+)

bot = TelegramClient('sharebot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Fungsi untuk mengubah ID angka menjadi kode teks (agar link terlihat rapi)
def encode(text):
    return base64.b64encode(text.encode("ascii")).decode("ascii")

def decode(text):
    return base64.b64decode(text.encode("ascii")).decode("ascii")

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    # 1. Cek apakah user sudah join channel fsub (private)
    try:
        await bot(GetParticipantRequest(DB_CHANNEL, event.sender_id))
    except UserNotParticipantError:
        # Jika belum join, kirim pesan peringatan
        join_button = [
            [Button.url("Join Channel Dulu", CHANNEL_URL)],
            [Button.url("Coba Lagi", f"https://t.me/{(await bot.get_me()).username}?start={event.text.split(' ')[1] if len(event.text) > 7 else ''}")]
        ]
        return await event.respond("❌ **Akses Ditolak!**\nSilakan bergabung ke channel kami terlebih dahulu.", buttons=join_button)

    # 2. Jika user klik link file (Contoh: /start base64code)
    if len(event.text) > 7:
        coded_id = event.text.split(" ")[1]
        try:
            msg_id = int(decode(coded_id))
            # Mengambil file dari channel database dan mengirim ke user
            await bot.forward_messages(event.chat_id, msg_id, DB_CHANNEL)
        except Exception as e:
            logging.error(f"Error saat ambil file: {e}")
            await event.respond("Maaf, file tersebut tidak lagi tersedia.")
    else:
        # Pesan start biasa jika tidak ada kode file
        await event.respond("Halo! Kirimkan saya file (hanya Admin) atau klik link file yang tersedia.")

@bot.on(events.NewMessage)
async def upload_handler(event):
    # 3. Proteksi Admin: Hanya kamu yang bisa upload file
    if event.sender_id != ADMIN_ID:
        return

    # Jika admin mengirim media (foto/video/dokumen) dan bukan perintah /start
    if event.media and not event.text.startswith('/start'):
        status = await event.respond("Sedang memproses file...")
        
        # Kirim file ke channel database
        sent_msg = await bot.send_message(DB_CHANNEL, file=event.media, caption=event.text or "")
        
        # Buat link unik
        coded_id = encode(str(sent_msg.id))
        bot_username = (await bot.get_me()).username
        share_link = f"https://t.me/{bot_username}?start={coded_id}"
        
        await status.edit(f"✅ **Berhasil Diupload!**\n\nLink kamu:\n`{share_link}`", link_preview=False)

print("Bot aktif...")
bot.run_until_disconnected()
                                                                                           
