import os, subprocess, sys, asyncio, threading, re
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# --- RAILWAY 24/7 ---
app = Flask(__name__)
@app.route('/')
def h(): return "Active"
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

# --- THE STREAMING ENGINE (FIXED FOR RAILWAY) ---
def get_audio_stream(q):
    opts = {
        # 'worst' is the secret. YouTube rarely blocks low-quality video streams.
        # Telegram will still play it as audio.
        'format': 'bestaudio/worstvideo/best', 
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1',
        'nocheckcertificate': True,
        'geo_bypass': True,
        'skip_download': True,
        'cookiefile': COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        # We search specifically for official audio to keep it clean
        info = ydl.extract_info(f"ytsearch1:{q} official audio", download=False)
        if 'entries' in info:
            info = info['entries'][0]
        return info.get('url'), info.get('title'), info.get('uploader')

# --- HANDLERS ---
async def start_cmd(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text(WELCOME, parse_mode='Markdown')

async def handle_everything(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    text = u.message.text.strip()
    if text.lower().startswith("/start"): return

    # Clean query for all prefixes
    query = re.sub(r'^[!/#]|^get\s+|^lr\s+', '', text, flags=re.IGNORECASE).strip()
    if not query: return
    
    try:
        # Fetching direct link
        stream_url, title, artist = await asyncio.to_thread(get_audio_stream, query)
        
        if stream_url:
            # We use reply_audio so Telegram hides the video and shows the music player
            await u.message.reply_audio(
                audio=stream_url, 
                title=title, 
                performer=artist, 
                caption=CREDIT, 
                parse_mode='Markdown'
            )
    except Exception as e:
        print(f"Railway Block Error: {e}")

# --- EXECUTION ---
async def main():
    threading.Thread(target=run, daemon=True).start()
    bot = Application.builder().token(TOKEN).build()
    
    bot.add_handler(CommandHandler("start", start_cmd))
    # Combined filter to handle everything: text, commands, and prefixes
    bot.add_handler(MessageHandler(filters.TEXT, handle_everything))
    
    print("RAILWAY-OPTIMIZED MODE ACTIVE ----")
    print("Dev -> @FUCXD")

    await bot.initialize()
    await bot.start()
    await bot.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
    
