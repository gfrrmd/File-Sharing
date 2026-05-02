# File Sharing Bot

Bot Telegram untuk menyimpan file ke channel database dan membagikannya kembali melalui bot.

## Penjelasan

Project ini dipakai untuk:
- Menyimpan file ke channel Telegram sebagai database
- Mengelola file melalui bot Telegram
- Membagikan file dengan lebih praktis
- Menjalankan bot secara online menggunakan Railway

## Required Variables

Saat deploy ke Railway, isi variable berikut:

| Variable | Keterangan |
|---|---|
| `API_ID` | Telegram API ID |
| `API_HASH` | Telegram API Hash |
| `BOT_TOKEN` | Token bot dari BotFather |
| `ADMIN_ID` | User ID Telegram admin/owner bot |
| `DB_CHANNEL` | ID channel Telegram untuk database file |

## Yang Dibutuhkan

### 1. API_ID dan API_HASH
Ambil dari Telegram Developer.

### 2. BOT_TOKEN
Buat bot lewat [@BotFather](https://t.me/BotFather), lalu salin token bot.

### 3. ADMIN_ID
Isi dengan user ID Telegram milik admin utama bot.

### 4. DB_CHANNEL
Buat channel Telegram untuk database file, lalu:
- Tambahkan bot ke channel
- Jadikan bot sebagai admin
- Ambil ID channel tersebut
- Masukkan ke `DB_CHANNEL`

## Cara Menjalankan Secara Lokal

```bash
git clone https://github.com/gfrrmd/File-Sharing.git
cd File-Sharing
pip install -r requirements.txt
python bot.py
