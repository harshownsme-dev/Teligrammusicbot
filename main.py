import os, subprocess, sys, asyncio, threading, re
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# --- RAILWAY 24/7 ---
app = Flask(__name__)
@app.route('/')
def h(): return "Bot Active"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- AUTO-INSTALLER ---
def init():
    for lib in ['python-telegram-bot', 'yt-dlp', 'flask']:
        try: __import__(lib.replace('-', '_'))
        except: subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])

init()
import yt_dlp

# --- CONFIG ---
TOKEN = os.environ.get('BOT_TOKEN') or '8595967891:AAHS1PE2om3824-l1ualhUNSQhe7MyNavVw'
CREDIT = "***Developed by [ @FUCXD ]💀***"
WELCOME = "***Bot alive Devloper -> [ @FUCXD ]💀***"

# --- COOKIE HANDLER ---
COOKIE_FILE = "cookies.txt"
cookie_data = os.environ.get("COOKIES_CONTENT")
if cookie_data:
    with open(COOKIE_FILE, "w") as f:
        f.write(cookie_data)

# --- THE STREAMING ENGINE ---
def get_audio_stream(q):
    opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1',
        'nocheckcertificate': True,
        'geo_bypass': True,
        'skip_download': True,
        'cookiefile': COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'}
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(q, download=False)
        if 'entries' in info: info = info['entries'][0]
        return info['url'], info.get('title'), info.get('uploader')

# --- HANDLERS ---
async def start_cmd(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text(WELCOME, parse_mode='Markdown')

async def handle_request(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    raw_text = u.message.text.strip()
    
    # Ignore /start command here
    if raw_text.lower().startswith("/start"): return

    # Clean the query (handles !, /, get, etc.)
    query = re.sub(r'^[!/#]|^get\s+|^lr\s+', '', raw_text, flags=re.IGNORECASE).strip()
    if not query: return
    
    try:
        # Direct stream fetch
        stream_url, title, art = await asyncio.to_thread(get_audio_stream, query)
        
        # Send audio directly
        await u.message.reply_audio(
            audio=stream_url, 
            title=title, 
            performer=art, 
            caption=CREDIT, 
            parse_mode='Markdown'
        )
    except:
        pass

# --- EXECUTION ---
async def main():
    threading.Thread(target=run, daemon=True).start()
    bot = Application.builder().token(TOKEN).build()
    
    bot.add_handler(CommandHandler("start", start_cmd))
    bot.add_handler(MessageHandler(filters.TEXT, handle_request))
    
    print("Zero-Fluff + Cookies Active ----")
    print("Dev -> @FUCXD")

    await bot.initialize()
    await bot.start()
    await bot.updater.start_polling(drop_pending_updates=True) # Kills session conflicts
    while True: await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
    
