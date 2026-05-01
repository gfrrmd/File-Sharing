import os
import base64
import logging
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

logging.basicConfig(level=logging.INFO)

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))
DB_CHANNEL = int(os.environ.get("DB_CHANNEL"))
CHANNEL_URL = os.environ.get("CHANNEL_URL")

bot = TelegramClient('sharebot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def encode(text):
    return base64.b64encode(text.encode("ascii")).decode("ascii")

def decode(text):
    return base64.b64decode(text.encode("ascii")).decode("ascii")

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    # 1. Cek Force Subscribe
    try:
        await bot(GetParticipantRequest(DB_CHANNEL, event.sender_id))
    except UserNotParticipantError:
        join_button = [
            [Button.url("Join Channel", CHANNEL_URL)],
            [Button.url("Coba Lagi", f"https://t.me/{(await bot.get_me()).username}?start={event.text.split(' ')[1] if len(event.text) > 7 else ''}")]
        ]
        return await event.respond("❌ **Akses Ditolak!**\nJoin channel dulu ya.", buttons=join_button)

    # 2. Logika Mengambil File
    if len(event.text) > 7:
        coded_id = event.text.split(" ")[1]
        try:
            msg_id = int(decode(coded_id))
            
            # Ambil pesan dari channel database
            msgs = await bot.get_messages(DB_CHANNEL, ids=msg_id)
            
            if msgs and msgs.media:
                # Mengirim ulang media tanpa label forward + proteksi konten
                await bot.send_message(
                    event.chat_id, 
                    file=msgs.media, 
                    message=msgs.text, # Mengambil caption asli
                    protect_content=True # ANTI-FORWARD & ANTI-SCREENSHOT
                )
            else:
                await event.respond("File tidak ditemukan.")
        except Exception as e:
            logging.error(f"Error: {e}")
            await event.respond("Terjadi kesalahan saat mengambil file.")
    else:
        await event.respond("Bot Aktif! Kirim file untuk upload (Khusus Admin).")

@bot.on(events.NewMessage)
async def upload_handler(event):
    # Proteksi Admin
    if event.sender_id != ADMIN_ID:
        return

    if event.media and not event.text.startswith('/'):
        # Admin upload file ke channel database (agar tersimpan)
        sent_msg = await bot.send_message(DB_CHANNEL, file=event.media, message=event.text or "")
        
        coded_id = encode(str(sent_msg.id))
        bot_username = (await bot.get_me()).username
        share_link = f"https://t.me/{bot_username}?start={coded_id}"
        
        await event.respond(f"✅ **File Berhasil Disimpan!**\n\nLink (Protected): `{share_link}`", link_preview=False)

print("Bot aktif dengan fitur Restricted Content...")
bot.run_until_disconnected()
        
