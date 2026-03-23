import os, subprocess, sys, asyncio, threading, re
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

app = Flask(__name__)
@app.route('/')
def h(): return "Active"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def init():
    for lib in ['python-telegram-bot', 'yt-dlp', 'flask']:
        try: __import__(lib.replace('-', '_'))
        except: subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])

init()
import yt_dlp

TOKEN = os.environ.get('BOT_TOKEN') or '8595967891:AAHS1PE2om3824-l1ualhUNSQhe7MyNavVw'
CREDIT = "***Developed by [ @FUCXD ]💀***"
WELCOME = "***Bot alive Devloper -> [ @FUCXD ]💀***"

def get_audio_stream(q):
    # Try SoundCloud first because YouTube is blocking Railway IPs
    # We use 'scsearch' for SoundCloud and 'ytsearch' as backup
    search_queries = [f"scsearch1:{q}", f"ytsearch1:{q} official audio"]
    
    opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'skip_download': True,
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'}
    }

    for query in search_queries:
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(query, download=False)
                if info and 'entries' in info and len(info['entries']) > 0:
                    target = info['entries'][0]
                    return target.get('url'), target.get('title'), target.get('uploader')
        except Exception as e:
            print(f"Query {query} failed: {e}")
            continue
    return None, None, None

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
        else:
            print("No results found on any platform.")
    except Exception as e:
        print(f"Final Error: {e}")

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
    
