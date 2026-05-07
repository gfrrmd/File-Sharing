# 📁 File Sharing Telegram Bot

Bot Telegram berbasis [Pyrogram](https://docs.pyrogram.org/) untuk menyimpan file (foto, video, dokumen) ke channel Telegram sebagai database cloud, lalu membagikannya lewat link unik yang **diproteksi anti-forward & anti-screenshot**.

---

## ✨ Fitur

- 🔐 **Link Unik per File** — setiap file mendapat kode acak 10 karakter (huruf + angka)
- 🛡️ **Proteksi Konten** — file dikirim dengan `protect_content=True`, mencegah forward & screenshot
- ☁️ **Cloud Storage via Channel** — file disimpan di channel Telegram sebagai database
- 👮 **Akses Admin Only** — hanya admin yang bisa upload; user lain hanya bisa akses via link
- ⚡ **Siap Deploy ke Railway** — sudah dilengkapi `Procfile` dan konfigurasi env variable

---

## 🚀 Deploy ke Railway

### Cara Cepat (Satu Klik)

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/WwYXmR?referralCode=_9ag2F&utm_medium=integration&utm_source=template&utm_campaign=file-sharing)

### Cara Manual

1. **Fork** repo ini ke akun GitHub kamu
2. Buka [railway.app](https://railway.app) dan login
3. Klik **New Project** → **Deploy from GitHub Repo** → pilih repo ini
4. Buka tab **Variables**, lalu isi semua environment variable berikut:

| Variable | Keterangan |
|---|---|
| `API_ID` | Telegram API ID dari [my.telegram.org](https://my.telegram.org/auth) |
| `API_HASH` | Telegram API Hash dari [my.telegram.org](https://my.telegram.org/auth) |
| `BOT_TOKEN` | Token bot dari [@BotFather](https://t.me/BotFather) |
| `ADMIN_ID` | User ID Telegram kamu (owner/admin bot) |
| `DB_CHANNEL` | ID channel Telegram database (format: `-100xxxxxxxxxx`) |

5. Railway akan otomatis menjalankan perintah dari `Procfile`:
   ```
   worker: python main.py
   ```
6. Tunggu deploy selesai — bot langsung aktif!

---

## ⚙️ Persyaratan Sebelum Deploy

### 1. API_ID & API_HASH
- Buka [my.telegram.org/auth](https://my.telegram.org/auth)
- Login → **API Development Tools** → buat aplikasi baru
- Salin `API ID` dan `API Hash`

### 2. BOT_TOKEN
- Buka [@BotFather](https://t.me/BotFather) di Telegram
- Kirim `/newbot` → ikuti instruksi → salin token

### 3. ADMIN_ID
- Buka [@userinfobot](https://t.me/userinfobot) → kirim `/start`
- Salin **User ID** kamu

### 4. DB_CHANNEL
- Buat channel Telegram baru (bisa private)
- Tambahkan bot ke channel tersebut
- **Jadikan bot sebagai Admin** dengan semua permission (terutama *Post Messages*)
- Ambil ID channel dari [@userinfobot](https://t.me/userinfobot) atau forward pesan dari channel ke bot tersebut
- ID channel biasanya berawalan `-100...`

---

## 📖 Cara Penggunaan

### Sebagai Admin
1. Buka chat pribadi dengan bot
2. Kirim file apa saja (foto, video, dokumen)
3. Bot akan membalas dengan **link sharing** unik, contoh:
   ```
   https://t.me/namabot?start=aB3dEf7gHi
   ```
4. Bagikan link tersebut ke siapa saja

### Sebagai User
1. Klik link yang dibagikan admin
2. Bot akan langsung mengirimkan file — **tanpa bisa di-forward atau di-screenshot**

---

## 🧱 Struktur Project

```
File-Sharing-Telegram-Bot/
├── main.py           # Logika utama bot (Pyrogram)
├── requirements.txt  # Dependensi: pyrogram, tgcrypto
├── Procfile          # Entry point untuk Railway
└── README.md
```

---

## ⚠️ Catatan Penting

- Jika setelah deploy bot **gagal menyimpan file**, pastikan bot sudah dijadikan **Admin di DB_CHANNEL** dengan izin penuh.
- Link sharing bersifat **in-memory** (tidak persisten). Jika bot di-restart, semua link lama akan hilang. Untuk produksi, pertimbangkan menambahkan database seperti MongoDB atau Redis.
- `tgcrypto` diperlukan untuk enkripsi — **jangan dihapus** dari `requirements.txt`.
