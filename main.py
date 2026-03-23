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

# --- THE STREAMING ENGINE (MOBILE CLIENT HACK) ---
def get_audio_stream(q):
    opts = {
        # 'best' is safer than 'bestaudio' on blocked IPs
        'format': 'best', 
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1',
        'nocheckcertificate': True,
        'geo_bypass': True,
        'skip_download': True,
        # THE NUCLEAR OPTION: Forces yt-dlp to pretend it's an Android Phone
        'extractor_args': {
            'youtube': {
                'player_client': ['android'],
                'skip': ['webpage', 'player_js']
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.android.youtube/19.05.36 (Linux; U; Android 11; en_US; Pixel 4) gzip',
            'Accept': '*/*',
            'Connection': 'keep-alive',
        }
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
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

    query = re.sub(r'^[!/#]|^get\s+|^lr\s+', '', text, flags=re.IGNORECASE).strip()
    if not query: return
    
    try:
        stream_url, title, artist = await asyncio.to_thread(get_audio_stream, query)
        
        if stream_url:
            await u.message.reply_audio(
                audio=stream_url, 
                title=title, 
                performer=artist, 
                caption=CREDIT, 
                parse_mode='Markdown'
            )
    except Exception as e:
        # If it still fails, the IP is hard-blocked. 
        print(f"CRITICAL BLOCK: {e}")

# --- EXECUTION ---
async def main():
    threading.Thread(target=run, daemon=True).start()
    bot = Application.builder().token(TOKEN).build()
    bot.add_handler(CommandHandler("start", start_cmd))
    bot.add_handler(MessageHandler(filters.TEXT, handle_everything))
    
    await bot.initialize()
    await bot.start()
    await bot.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
    
