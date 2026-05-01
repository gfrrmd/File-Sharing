import os
import base64
import logging
import secrets
import string
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from telethon.tl.types import InputPeerChannel

# Setup Logging agar muncul di Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))
DB_CHANNEL = int(os.environ.get("DB_CHANNEL"))
CHANNEL_URL = os.environ.get("CHANNEL_URL")

bot = TelegramClient('sharebot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def encode_id(msg_id):
    random_salt = "".join(secrets.choice(string.ascii_letters) for _ in range(5))
    combined = f"{random_salt}:{msg_id}"
    return base64.urlsafe_b64encode(combined.encode()).decode().strip("=")

def decode_id(coded_str):
    try:
        decoded = base64.urlsafe_b64decode(coded_str + "==").decode()
        return int(decoded.split(":")[1])
    except Exception as e:
        logger.error(f"Decode Error: {e}")
        return None

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    # 1. Force Subscribe Check
    try:
        await bot(GetParticipantRequest(DB_CHANNEL, event.sender_id))
    except UserNotParticipantError:
        join_button = [
            [Button.url("Join Channel", CHANNEL_URL)],
            [Button.url("Coba Lagi", f"https://t.me/{(await bot.get_me()).username}?start={event.text.split(' ')[1] if len(event.text) > 7 else ''}")]
        ]
        return await event.respond("⚠️ **AKSES DITOLAK**\nSilakan bergabung ke channel untuk mengambil file.", buttons=join_button)
    except Exception as e:
        logger.error(f"Fsub Error: {e}")
        return await event.respond("Verifikasi member gagal. Pastikan bot adalah admin di channel.")

    # 2. Ambil File
    if len(event.text) > 7:
        coded_id = event.text.split(" ")[1]
        real_id = decode_id(coded_id)
        
        if not real_id:
            return await event.respond("Link tidak valid.")

        try:
            # --- PERBAIKAN UTAMA DI SINI ---
            # Dapatkan entitas channel secara eksplisit agar bot "mengenal" channelnya
            entity = await bot.get_input_entity(DB_CHANNEL)
            
            # Ambil pesan menggunakan entitas yang sudah divalidasi
            msgs = await bot.get_messages(entity, ids=real_id)
            
            if msgs and msgs.media:
                await bot.send_message(
                    event.chat_id,
                    file=msgs.media,
                    message=msgs.text or "",
                    protect_content=True # ANTI-SCREENSHOT & ANTI-FORWARD
                )
            else:
                await event.respond("Maaf, file tidak ditemukan di database channel.")
        except Exception as e:
            logger.error(f"Gagal mengambil pesan ID {real_id}: {e}")
            await event.respond(f"Kesalahan sistem saat mengambil file. (ID: {real_id})")
    else:
        await event.respond("Bot Aktif! Kirim file ke sini (Admin) untuk buat link unik.")

@bot.on(events.NewMessage)
async def upload_handler(event):
    if event.sender_id != ADMIN_ID:
        return

    if event.media and not event.text.startswith('/'):
        try:
            # Upload ke channel
            sent_msg = await bot.send_message(DB_CHANNEL, file=event.media, message=event.text or "")
            
            # Buat link unik
            unique_code = encode_id(sent_msg.id)
            bot_username = (await bot.get_me()).username
            share_link = f"https://t.me/{bot_username}?start={unique_code}"
            
            await event.respond(f"✅ **Berhasil!**\n\nLink Unik (Anti-Screenshot):\n`{share_link}`", link_preview=False)
        except Exception as e:
            logger.error(f"Upload Error: {e}")
            await event.respond("Gagal upload ke channel cloud.")

print("Bot berjalan...")
bot.run_until_disconnected()
