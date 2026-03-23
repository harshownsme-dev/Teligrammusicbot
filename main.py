import os, subprocess, sys, asyncio, threading, re
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# --- RAILWAY 24/7 ---
app = Flask(__name__)
@app.route('/')
def h(): return "Bot Active"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- FAST-INSTALLER ---
def init():
    for lib in ['python-telegram-bot', 'yt-dlp', 'flask']:
        try: __import__(lib.replace('-', '_'))
        except: subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])

init()
import yt_dlp

# --- CONFIG ---
TOKEN = os.environ.get('BOT_TOKEN') or '8595967891:AAHS1PE2om3824-l1ualhUNSQhe7MyNavVw'
CREDIT = "***Developed by [ @FUCXD ]💀***"

# --- THE STREAMING ENGINE (FASTEST METHOD) ---
def get_audio_stream(q):
    opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1',
        'nocheckcertificate': True,
        'geo_bypass': True,
        # skip_download: True sends the URL directly to Telegram
        'skip_download': True, 
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'}
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(q, download=False)
        if 'entries' in info: info = info['entries'][0]
        # Return the stream URL instead of a file path
        return info['url'], info.get('title'), info.get('uploader')

# --- UNIFIED HANDLER (OLD + NEW COMMANDS) ---
async def handle_request(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    raw_text = u.message.text.strip()

    # 1. Clean the query: removes !, /, #, get, lr from the start
    query = re.sub(r'^[!/#]|^get\s+|^lr\s+', '', raw_text, flags=re.IGNORECASE).strip()
    
    if not query or query.lower() == "start": return

    status = await u.message.reply_text("⚡")
    
    try:
        # Fetch stream URL (No disk download = High Speed)
        stream_url, title, art = await asyncio.to_thread(get_audio_stream, query)
        
        await u.message.reply_audio(
            audio=stream_url, 
            title=title, 
            performer=art, 
            caption=CREDIT, 
            parse_mode='Markdown'
        )
        await status.delete()
    except:
        await status.edit_text("❌")

# --- EXECUTION ---
async def main():
    threading.Thread(target=run, daemon=True).start()
    
    # drop_pending_updates=True prevents Conflict crashes
    bot = Application.builder().token(TOKEN).build()
    
    # This handler covers ALL text (Direct names, !commands, /commands)
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_request))
    
    # Handlers for specific slash commands to ensure old commands work
    bot.add_handler(CommandHandler(["get", "lr", "start"], handle_request))
    
    print("Hybrid Ultra-Speed Active ----")
    print("Dev -> @FUCXD")

    await bot.initialize()
    await bot.start()
    await bot.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
