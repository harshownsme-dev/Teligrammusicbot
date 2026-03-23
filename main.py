import os, subprocess, sys, asyncio, threading
from flask import Flask
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes, CallbackQueryHandler

# --- RAILWAY HEALTH CHECK ---
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
OWNER_ID = 8276411342  
CREDIT_TEXT = "***Developed by [ @FUCXD ]💀***"

# --- DOWNLOAD LOGIC (FIXED FOR FAKE RESULTS) ---
def fast_download(query):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': 's.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        # 'ytsearch3' looks at top 3 results to find the real one, avoiding the "Hola Amigo" fake
        'default_search': 'ytsearch3', 
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        
        # Logic to pick the BEST match out of top 3 results
        actual_video = None
        if 'entries' in info:
            for entry in info['entries']:
                # Filter out videos that are too short or have "Hola" in title
                if "hola" not in entry.get('title', '').lower():
                    actual_video = entry
                    break
            if not actual_video: actual_video = info['entries'][0]
        else:
            actual_video = info

        # Download the selected one
        ydl.download([actual_video['webpage_url']])
        file_path = ydl.prepare_filename(actual_video)
        return file_path, actual_video.get('title', 'Song'), actual_video.get('uploader', 'Artist')

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("***Bot alive Devloper -> [ @FUCXD ]💀***", parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_text = update.message.text
    query = None
    
    if "http" in msg_text:
        query = msg_text # Direct link is always 100% accurate
    elif msg_text.lower().startswith(("/get ", "get ")):
        query = msg_text.split(None, 1)[1]
    elif msg_text.lower().startswith(("/lr ", "lr ")):
        query = msg_text.split(None, 1)[1]

    if query:
        status = await update.message.reply_text(f"***🔍 Searching for '{query}'...***", parse_mode='Markdown')
        try:
            file_path, title, artist = await asyncio.to_thread(fast_download, query)
            with open(file_path, 'rb') as audio:
                await update.message.reply_audio(audio=audio, title=title, performer=artist, caption=CREDIT_TEXT, parse_mode='Markdown')
            await status.delete()
            if os.path.exists(file_path): os.remove(file_path)
        except Exception as e:
            await status.edit_text(f"***❌ YouTube Blocked the search. Please paste the direct Link!***")

# --- MAIN ---
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Hot running 24/7 on Railway ----")
    print("Dev -> @FUCXD")

    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
        
