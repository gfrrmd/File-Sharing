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
    # Cek Force Subscribe
    try:
        await bot(GetParticipantRequest(DB_CHANNEL, event.sender_id))
    except UserNotParticipantError:
        join_button = [
            [Button.url("Join Channel", CHANNEL_URL)],
            [Button.url("Coba Lagi", f"https://t.me/{(await bot.get_me()).username}?start={event.text.split(' ')[1] if len(event.text) > 7 else ''}")]
        ]
        return await event.respond("❌ **Akses Ditolak!**\nJoin channel dulu ya.", buttons=join_button)
    except Exception as e:
        return await event.respond(f"Error: {e}")

    # Ambil File
    if len(event.text) > 7:
        coded_id = event.text.split(" ")[1]
        try:
            msg_id = int(decode(coded_id))
            # Mengirim balik file dari channel ke user
            await bot.forward_messages(event.chat_id, msg_id, DB_CHANNEL)
        except:
            await event.respond("File tidak ditemukan.")
    else:
        await event.respond("Kirim file ke saya (Admin Only) untuk dapat link.")

@bot.on(events.NewMessage)
async def fast_upload_handler(event):
    # Proteksi Admin
    if event.sender_id != ADMIN_ID:
        return

    # Logika Forward Instan
    if event.media and not event.text.startswith('/'):
        # Gunakan forward_messages agar instan (server-side telegram)
        sent_msgs = await bot.forward_messages(DB_CHANNEL, event.message)
        
        # Ambil ID dari pesan yang baru saja di-forward ke channel
        sent_msg = sent_msgs[0] if isinstance(sent_msgs, list) else sent_msgs
        
        coded_id = encode(str(sent_msg.id))
        bot_username = (await bot.get_me()).username
        share_link = f"https://t.me/{bot_username}?start={coded_id}"
        
        await event.respond(f"✅ **Instan Upload Berhasil!**\n\nLink: `{share_link}`", link_preview=False)

print("Bot aktif dengan mode Fast Forward...")
bot.run_until_disconnected()
            
