import os
import base64
import logging
import secrets
import string
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

# Setup Logging
logging.basicConfig(level=logging.INFO)

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))
DB_CHANNEL = int(os.environ.get("DB_CHANNEL"))
CHANNEL_URL = os.environ.get("CHANNEL_URL")

bot = TelegramClient('sharebot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Fungsi untuk membuat link unik (mengacak ID agar tidak bisa ditebak)
def encode_id(msg_id):
    # Menambahkan angka acak di depan ID untuk membuatnya unik seperti captcha
    random_salt = "".join(secrets.choice(string.ascii_letters) for _ in range(5))
    combined = f"{random_salt}:{msg_id}"
    return base64.urlsafe_b64encode(combined.encode()).decode().strip("=")

def decode_id(coded_str):
    try:
        # Menambah padding jika hilang saat proses pengiriman link
        decoded = base64.urlsafe_b64decode(coded_str + "==").decode()
        # Mengambil ID asli setelah tanda titik dua (:)
        return int(decoded.split(":")[1])
    except:
        return None

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    # 1. Proteksi Force Subscribe
    try:
        await bot(GetParticipantRequest(DB_CHANNEL, event.sender_id))
    except UserNotParticipantError:
        join_button = [
            [Button.url("Join Channel (Private)", CHANNEL_URL)],
            [Button.url("Coba Lagi", f"https://t.me/{(await bot.get_me()).username}?start={event.text.split(' ')[1] if len(event.text) > 7 else ''}")]
        ]
        return await event.respond("⚠️ **AKSES DIBATASI**\nSilakan bergabung ke channel private kami untuk mengambil file.", buttons=join_button)
    except Exception as e:
        logging.error(f"Fsub Error: {e}")
        return await event.respond("Terjadi masalah saat verifikasi keanggotaan.")

    # 2. Logika Mengambil File
    if len(event.text) > 7:
        coded_id = event.text.split(" ")[1]
        real_id = decode_id(coded_id)
        
        if not real_id:
            return await event.respond("Link tidak valid atau kadaluarsa.")

        try:
            # Ambil pesan langsung dari ID channel
            msg = await bot.get_messages(DB_CHANNEL, ids=real_id)
            
            if msg and msg.media:
                await bot.send_message(
                    event.chat_id,
                    file=msg.media,
                    message=msg.text or "",
                    protect_content=True # ANTI-SCREENSHOT & ANTI-FORWARD
                )
            else:
                await event.respond("Maaf, file tidak ditemukan di database.")
        except Exception as e:
            logging.error(f"Fetch Error: {e}")
            await event.respond("Gagal mengambil file. Pastikan Bot adalah Admin di channel database.")
    else:
        await event.respond("Bot Aktif. Kirim file (Admin Only) untuk mendapatkan link unik.")

@bot.on(events.NewMessage)
async def upload_handler(event):
    # Proteksi Admin
    if event.sender_id != ADMIN_ID:
        return

    if event.media and not event.text.startswith('/'):
        # Kirim ke channel database
        sent_msg = await bot.send_message(DB_CHANNEL, file=event.media, message=event.text or "")
        
        # Buat link unik dengan salt
        unique_code = encode_id(sent_msg.id)
        bot_username = (await bot.get_me()).username
        share_link = f"https://t.me/{bot_username}?start={unique_code}"
        
        await event.respond(
            f"✅ **Berhasil Diupload!**\n\nLink Unik:\n`{share_link}`\n\n*Catatan: Link ini diproteksi (Restricted Content)*",
            link_preview=False
        )

print("Bot berjalan dengan Link Unik & Proteksi Konten...")
bot.run_until_disconnected()
        
