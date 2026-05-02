# File Sharing Telegram Bot

Bot Telegram untuk menyimpan file ke channel database dan membagikannya kembali melalui bot dengan lebih mudah.

## Penjelasan

Project ini digunakan untuk:
- Menyimpan file ke channel Telegram sebagai database
- Mengelola file melalui bot Telegram
- Membagikan file dengan lebih praktis
- Menjalankan bot secara online menggunakan Railway

## Deploy on Railway

Klik tombol di bawah untuk deploy bot ini ke Railway.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/WwYXmR?referralCode=_9ag2F&utm_medium=integration&utm_source=template&utm_campaign=file-sharing)

## Required Variables

Saat deploy ke Railway, isi variabel berikut:

| Variable | Keterangan |
|---|---|
| `API_ID` | Telegram API ID |
| `API_HASH` | Telegram API Hash |
| `BOT_TOKEN` | Token bot dari BotFather |
| `ADMIN_ID` | User ID Telegram admin/owner bot |
| `DB_CHANNEL` | ID channel Telegram yang dipakai sebagai database file |

## Yang Dibutuhkan

### 1. API_ID dan API_HASH
Ambil dari akun Telegram Developer.

### 2. BOT_TOKEN
Buat bot melalui [@BotFather](https://t.me/BotFather), lalu salin token bot.

### 3. ADMIN_ID
Isi dengan user ID Telegram admin utama bot.

### 4. DB_CHANNEL
Buat channel Telegram untuk database file, lalu:
- Tambahkan bot ke channel
- Jadikan bot sebagai admin
- Ambil ID channel
- Masukkan ke `DB_CHANNEL`

## Cara Menjalankan Secara Lokal

```bash
git clone https://github.com/gfrrmd/File-Sharing.git
cd File-Sharing
pip install -r requirements.txt
python bot.py
