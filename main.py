import os
import base64
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

# Ambil variabel dari Environment (Railway)
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))
DB_CHANNEL = int(os.environ.get("DB_CHANNEL"))
CHANNEL_URL = os.environ.get("CHANNEL_URL") # Link join channel

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def encode(text):
    return base64.b64encode(text.encode("ascii")).decode("ascii")

def decode(text):
    return base64.b64decode(text.encode("ascii")).decode("ascii")

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    # Cek Force Subscribe
    try:
        await bot(GetParticipantRequest(DB_CHANNEL, event.sender_id))
    except UserNotParticipantError:
        return await event.respond(
            f"Silakan bergabung ke channel kami terlebih dahulu untuk menggunakan bot ini.",
            buttons=[Button.url("Join Channel", CHANNEL_URL)]
        )

    # Logika Deep Linking (Jika user klik link t.me/bot?start=xxx)
    if len(event.text) > 7:
        coded_id = event.text.split(" ")[1]
        msg_id = int(decode(coded_id))
        try:
            await bot.forward_messages(event.chat_id, msg_id, DB_CHANNEL)
        except Exception:
            await event.respond("File tidak ditemukan atau telah dihapus.")
    else:
        await event.respond("Kirim file ke saya (Hanya Admin) untuk mendapatkan link sharing.")

@bot.on(events.NewMessage)
async def handle_upload(event):
    # Proteksi: Hanya Admin yang bisa upload
    if event.sender_id != ADMIN_ID:
        return

    if event.media and not event.text.startswith('/'):
        # Kirim file ke channel database
        sent_msg = await bot.send_message(DB_CHANNEL, file=event.media, caption=event.text or "")
        
        # Buat link berdasarkan ID pesan di channel
        coded_id = encode(str(sent_msg.id))
        bot_username = (await bot.get_me()).username
        share_link = f"https://t.me/{bot_username}?start={coded_id}"
        
        await event.respond(f"**File Berhasil Disimpan!**\n\nLink: `{share_link}`", link_preview=False)

print("Bot sedang berjalan...")
bot.run_until_disconnected()
      
