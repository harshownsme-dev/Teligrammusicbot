import os, subprocess, sys, asyncio, threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- RAILWAY 24/7 ---
app = Flask(__name__)
@app.route('/')
def h(): return "Bot Active"
def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

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

# --- THE "STREAMING" ENGINE (DIRECT FETCH) ---
def fetch_direct_url(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1',
        'nocheckcertificate': True,
        'geo_bypass': True,
        'skip_download': True, # DO NOT INSTALL THE FILE
        'force_generic_extractor': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Just getting the link and metadata, not the file
        info = ydl.extract_info(query, download=False)
        if 'entries' in info: info = info['entries'][0]
        
        # This is the "Secret" direct link to the audio stream
        return info['url'], info.get('title'), info.get('uploader')

# --- COMMANDS ---
async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text("***Bot alive Devloper -> [ @FUCXD ]💀***", parse_mode='Markdown')

async def get(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not c.args: return
    query = " ".join(c.args)
    status = await u.message.reply_text("🚀") # Rocket for speed
    
    try:
        # Fetching ONLY the URL (Takes <1 second)
        stream_url, title, artist = await asyncio.to_thread(fetch_direct_url, query)
        
        # Tell Telegram to fetch the audio directly from the stream_url
        # This skips the Railway download entirely
        await u.message.reply_audio(
            audio=stream_url, 
            title=title, 
            performer=artist, 
            caption=CREDIT, 
            parse_mode='Markdown'
        )
        await status.delete()
    except Exception:
        await status.edit_text("❌ **Direct fetch failed. Use a link!**")

# --- EXECUTION ---
async def main():
    threading.Thread(target=run, daemon=True).start()
    
    # drop_pending_updates=True clears the 'Conflict' error instantly
    bot = Application.builder().token(TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler("get", get))
    
    print("Direct Stream Mode Active ----")
    print("Dev -> @FUCXD")

    await bot.initialize()
    await bot.start()
    await bot.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
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
    
