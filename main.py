import os
import json
import string
import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

# ─── ENV VARIABLES ───────────────────────────────────────────────
API_ID    = int(os.environ.get("API_ID"))
API_HASH  = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID  = int(os.environ.get("ADMIN_ID"))
DB_CHANNEL = int(os.environ.get("DB_CHANNEL"))
WEBAPP_URL = os.environ.get("WEBAPP_URL", "")
PORT       = int(os.environ.get("PORT", 8080))

# ─── PERSISTENT STORAGE (JSON file) ──────────────────────────────
DB_FILE = "db_links.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

db_links = load_db()

# ─── BOT CLIENT ──────────────────────────────────────────────────
app = Client("file_sharing_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def generate_code(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

# ─── /start HANDLER ──────────────────────────────────────────────
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    if len(message.command) > 1:
        code = message.command[1]
        msg_id = db_links.get(code)
        if msg_id:
            try:
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=DB_CHANNEL,
                    message_id=msg_id,
                    protect_content=True
                )
            except Exception as e:
                await message.reply_text("\u274c Gagal mengambil file.")
        else:
            await message.reply_text("\u274c Link kadaluwarsa atau salah.")
    else:
        if message.from_user.id == ADMIN_ID:
            buttons = []
            if WEBAPP_URL:
                buttons.append([InlineKeyboardButton("\U0001f4c1 Buka Mini App", web_app=WebAppInfo(url=WEBAPP_URL))])
            await message.reply_text(
                "\U0001f44b **Halo Admin!**\n\nAnda bisa mengirim foto, video, atau dokumen ke sini "
                "untuk diubah menjadi link sharing otomatis."
                + ("\n\nAtau gunakan tombol di bawah untuk membuka Mini App." if WEBAPP_URL else ""),
                reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
            )
        else:
            await message.reply_text(
                "\U0001f64f **Selamat Datang!**\n\nBot ini hanya bisa digunakan jika Anda memiliki "
                "link file yang sah dari Admin."
            )

# ─── ADMIN UPLOAD VIA CHAT ────────────────────────────────────────
@app.on_message(filters.private & filters.user(ADMIN_ID) & ~filters.command(["start", "help"]))
async def admin_upload_handler(client, message):
    try:
        stored_msg = await message.copy(DB_CHANNEL)
        code = generate_code()
        db_links[code] = stored_msg.id
        save_db(db_links)

        bot = await client.get_me()
        link = f"https://t.me/{bot.username}?start={code}"

        await message.reply_text(
            f"\u2705 **Berhasil Disimpan!**\n\n"
            f"\U0001f517 **Link Sharing:**\n`{link}`\n\n"
            f"\u26a0\ufe0f *File diproteksi (Anti-Forward/Anti-Screenshot)*",
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply_text(f"\u274c Gagal upload: {str(e)}")

# ─── REJECT NON-ADMIN UPLOAD ─────────────────────────────────────
@app.on_message(filters.private & ~filters.user(ADMIN_ID) & (filters.document | filters.video | filters.photo))
async def non_admin_reject(client, message):
    await message.reply_text("\U0001f6ab Anda tidak memiliki izin untuk upload.")

# ─── HTTP SERVER ─────────────────────────────────────────────────
routes = web.RouteTableDef()

@routes.get("/")
async def index(request):
    with open("webapp/index.html", "r") as f:
        return web.Response(text=f.read(), content_type="text/html")

@routes.post("/api/upload")
async def api_upload(request):
    try:
        reader = await request.multipart()
        field = await reader.next()
        if field is None:
            return web.json_response({"ok": False, "error": "No file"}, status=400)
        filename = field.filename or "file"
        file_bytes = await field.read()
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix="_" + filename) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        sent = await app.send_document(DB_CHANNEL, tmp_path, file_name=filename)
        os.unlink(tmp_path)
        code = generate_code()
        db_links[code] = sent.id
        save_db(db_links)
        bot_info = await app.get_me()
        link = f"https://t.me/{bot_info.username}?start={code}"
        return web.json_response({"ok": True, "link": link, "filename": filename})
    except Exception as e:
        return web.json_response({"ok": False, "error": str(e)}, status=500)

@routes.get("/api/links")
async def api_links(request):
    bot_info = await app.get_me()
    result = []
    for code, msg_id in db_links.items():
        result.append({
            "code": code,
            "link": f"https://t.me/{bot_info.username}?start={code}",
            "msg_id": msg_id
        })
    return web.json_response({"ok": True, "links": result})

async def run_web():
    web_app = web.Application()
    web_app.add_routes(routes)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Web server running on port {PORT}")

# ─── MAIN ─────────────────────────────────────────────────────────
async def main():
    await run_web()
    await app.start()
    print("Bot started!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
