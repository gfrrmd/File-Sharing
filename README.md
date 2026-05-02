# File Sharing Bot

Bot Telegram untuk menyimpan file ke channel database dan membagikannya kembali lewat link khusus.

## Penjelasan

Project ini digunakan untuk:
- Menyimpan file ke channel Telegram sebagai database
- Mengelola akses file lewat bot
- Membagikan file dengan link yang lebih praktis
- Menjalankan bot secara online di Railway

## Environment Variables

Sebelum menjalankan bot, kamu harus menyiapkan variabel berikut:

| Variable | Wajib | Keterangan |
|---|---|---|
| `API_ID` | Ya | API ID Telegram |
| `API_HASH` | Ya | API Hash Telegram |
| `BOT_TOKEN` | Ya | Token bot dari BotFather |
| `ADMIN_ID` | Ya | User ID Telegram admin utama |
| `DB_CHANNEL` | Ya | ID channel Telegram untuk menyimpan file |

## Yang Dibutuhkan

### 1. API_ID dan API_HASH
Ambil dari akun Telegram developer kamu.

### 2. BOT_TOKEN
Buat bot lewat [@BotFather](https://t.me/BotFather), lalu ambil token bot.

### 3. ADMIN_ID
Masukkan user ID Telegram kamu sebagai admin/owner bot.

### 4. DB_CHANNEL
Buat channel Telegram untuk penyimpanan file, lalu:
- Tambahkan bot ke channel
- Jadikan bot sebagai admin
- Gunakan ID channel tersebut sebagai `DB_CHANNEL`

## Cara Menjalankan Secara Lokal

```bash
git clone https://github.com/gfrrmd/File-Sharing.git
cd File-Sharing
pip install -r requirements.txt
python bot.py
