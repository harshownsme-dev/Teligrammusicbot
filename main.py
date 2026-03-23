import os, subprocess, sys, asyncio, threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# --- RAILWAY 24/7 HEALTH CHECK ---
app_railway = Flask(__name__)
@app_railway.route('/')
def home(): return "Bot is Running"
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_railway.run(host='0.0.0.0', port=port)

# --- AUTO INSTALLER ---
def install_libs():
    libs = {'python-telegram-bot': 'telegram', 'yt-dlp': 'yt_dlp', 'flask': 'flask'}
    for lib_name, import_name in libs.items():
        try: __import__(import_name)
        except ImportError: subprocess.check_call([sys.executable, "-m", "pip", "install", lib_name, "--quiet"])

install_libs()
import yt_dlp

# --- CONFIG (WITH FALLBACK) ---
TOKEN = os.environ.get('BOT_TOKEN') or '8595967891:AAHS1PE2om3824-l1ualhUNSQhe7MyNavVw'
CREDIT_TEXT = "***Developed by [ @FUCXD ]💀***"

# --- HIGH-SPEED DOWNLOAD ENGINE ---
def fast_download(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 's.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1',
        'nocheckcertificate': True,
        'geo_bypass': True,
        'extract_flat': False,
        # Forced headers to bypass "Sign in" and "Hola Amigo" traps
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Direct metadata extraction
        info = ydl.extract_info(query, download=True)
        if 'entries' in info:
            info = info['entries'][0]
        return ydl.prepare_filename(info), info.get('title', 'Song'), info.get('uploader', 'Artist')

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("***Bot alive Devloper -> [ @FUCXD ]💀***", parse_mode='Markdown')

async def get_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This ensures the bot ONLY works when you type /get [song]
    if not context.args:
        return # Ignore empty /get commands
    
    query = " ".join(context.args)
    status = await update.message.reply_text("⚡ **Fetching...**", parse_mode='Markdown')
    
    try:
        # Offload download to thread to prevent bot freezing
        file_path, title, artist = await asyncio.to_thread(fast_download, query)
        
        with open(file_path, 'rb') as audio:
            await update.message.reply_audio(
                audio=audio, title=title, performer=artist, 
                caption=CREDIT_TEXT, parse_mode='Markdown'
            )
        await status.delete()
        if os.path.exists(file_path): os.remove(file_path)
    except Exception:
        await status.edit_text("❌ **Failed. Use a direct link!**")

# --- MAIN ---
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    
    # drop_pending_updates=True kills the Conflict error on start
    app = Application.builder().token(TOKEN).build()
    
    # Strictly only respond to /get or /start
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("get", get_music))
    
    print("Hot running 24/7 on Railway ----")
    print("Dev -> @FUCXD")

    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
    
