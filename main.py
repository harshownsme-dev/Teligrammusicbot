import os, subprocess, sys, asyncio, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes, CallbackQueryHandler

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

# --- THE "PRO" DOWNLOADER (SPEED & ACCURACY) ---
def fast_download(query):
    # This configuration mimics high-speed bots by forcing specific extractors
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 's.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1',
        'nocheckcertificate': True,
        'geo_bypass': True,
        # 'extract_flat' makes it fetch metadata in milliseconds
        'extract_flat': False, 
        'skip_download': False,
        'source_address': '0.0.0.0', # Helps with Railway network routing
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Connection': 'keep-alive',
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Step 1: Rapid metadata fetch
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)
        if 'entries' in info:
            info = info['entries'][0]
        
        file_path = ydl.prepare_filename(info)
        return file_path, info.get('title', 'Song'), info.get('uploader', 'Artist')

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("***Bot alive Devloper -> [ @FUCXD ]💀***", parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_text = update.message.text
    # Speed optimization: Ignore short spam texts
    if len(msg_text) < 3: return

    # Extract clean query
    query = msg_text
    if msg_text.lower().startswith(("/get ", "get ")): query = msg_text[4:].strip()
    elif msg_text.lower().startswith(("/lr ", "lr ")): query = msg_text[3:].strip()

    status = await update.message.reply_text("🚀 **Processing...**", parse_mode='Markdown')
    
    try:
        # Use asyncio thread to keep the bot responsive while downloading
        file_path, title, artist = await asyncio.to_thread(fast_download, query)
        
        with open(file_path, 'rb') as audio:
            await update.message.reply_audio(
                audio=audio, 
                title=title, 
                performer=artist, 
                caption=CREDIT_TEXT, 
                parse_mode='Markdown',
                connect_timeout=10 # High-speed upload
            )
        await status.delete()
        if os.path.exists(file_path): os.remove(file_path)
        
    except Exception as e:
        print(f"Error: {e}")
        await status.edit_text("❌ **Error fetching song. Try a direct YouTube Link!**", parse_mode='Markdown')

# --- MAIN ---
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Force Railway to recognize the active bot immediately
    print("Hot running 24/7 on Railway ----")
    print("Dev -> @FUCXD")

    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
    
